package com.enterprise.platform.boot.ai.service;

import com.enterprise.platform.ai.AiApiModels;
import com.enterprise.platform.ai.AiApiModels.AiCapabilities;
import com.enterprise.platform.ai.AiApiModels.ChatRequest;
import com.enterprise.platform.ai.AiApiModels.ChatResponse;
import com.enterprise.platform.ai.AiApiModels.EmbeddingRequest;
import com.enterprise.platform.ai.AiApiModels.EmbeddingResponse;
import com.enterprise.platform.ai.AiApiModels.ImageRequest;
import com.enterprise.platform.ai.AiApiModels.ImageResponse;
import com.enterprise.platform.ai.AiApiModels.ModerationRequest;
import com.enterprise.platform.ai.AiApiModels.ModerationResponse;
import com.enterprise.platform.ai.AiApiModels.RagAskRequest;
import com.enterprise.platform.ai.AiApiModels.RagChunk;
import com.enterprise.platform.ai.AiApiModels.RagIngestRequest;
import com.enterprise.platform.ai.AiApiModels.SpeechRequest;
import com.enterprise.platform.ai.AiApiModels.SpeechResponse;
import com.enterprise.platform.ai.AiApiModels.StructuredExtraction;
import com.enterprise.platform.ai.AiApiModels.StructuredExtractionRequest;
import com.enterprise.platform.ai.AiApiModels.TranscriptionPayload;
import com.enterprise.platform.ai.AiApiModels.TranscriptionResponse;
import com.enterprise.platform.ai.EnterpriseAiFacade;
import com.enterprise.platform.boot.ai.config.AiProperties;
import com.enterprise.platform.boot.ai.tool.PlatformAiTools;
import com.enterprise.platform.common.BusinessException;
import com.enterprise.platform.common.ErrorCode;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.audio.transcription.AudioTranscriptionPrompt;
import org.springframework.ai.audio.transcription.TranscriptionModel;
import org.springframework.ai.audio.tts.TextToSpeechModel;
import org.springframework.ai.audio.tts.TextToSpeechPrompt;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.converter.BeanOutputConverter;
import org.springframework.ai.document.Document;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.image.ImageModel;
import org.springframework.ai.image.ImagePrompt;
import org.springframework.ai.moderation.ModerationModel;
import org.springframework.ai.moderation.ModerationPrompt;
import org.springframework.ai.openai.OpenAiAudioSpeechOptions;
import org.springframework.ai.openai.OpenAiImageOptions;
import org.springframework.ai.transformer.splitter.TokenTextSplitter;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

@Service
public class SpringAiEnterpriseFacade implements EnterpriseAiFacade {

    private static final Logger log = LoggerFactory.getLogger(SpringAiEnterpriseFacade.class);

    private final ObjectProvider<ChatClient.Builder> chatClientBuilderProvider;
    private final ObjectProvider<EmbeddingModel> embeddingModelProvider;
    private final ObjectProvider<ImageModel> imageModelProvider;
    private final ObjectProvider<ModerationModel> moderationModelProvider;
    private final ObjectProvider<TranscriptionModel> transcriptionModelProvider;
    private final ObjectProvider<TextToSpeechModel> textToSpeechModelProvider;
    private final ObjectMapper objectMapper;
    private final AiProperties aiProperties;
    private final PlatformAiTools platformAiTools;

    private final List<VectorEntry> vectorEntries = new ArrayList<>();
    private final Object vectorLock = new Object();

    public SpringAiEnterpriseFacade(ObjectProvider<ChatClient.Builder> chatClientBuilderProvider,
                                    ObjectProvider<EmbeddingModel> embeddingModelProvider,
                                    ObjectProvider<ImageModel> imageModelProvider,
                                    ObjectProvider<ModerationModel> moderationModelProvider,
                                    ObjectProvider<TranscriptionModel> transcriptionModelProvider,
                                    ObjectProvider<TextToSpeechModel> textToSpeechModelProvider,
                                    ObjectMapper objectMapper,
                                    AiProperties aiProperties,
                                    PlatformAiTools platformAiTools) {
        this.chatClientBuilderProvider = chatClientBuilderProvider;
        this.embeddingModelProvider = embeddingModelProvider;
        this.imageModelProvider = imageModelProvider;
        this.moderationModelProvider = moderationModelProvider;
        this.transcriptionModelProvider = transcriptionModelProvider;
        this.textToSpeechModelProvider = textToSpeechModelProvider;
        this.objectMapper = objectMapper;
        this.aiProperties = aiProperties;
        this.platformAiTools = platformAiTools;
        loadVectorStore();
    }

    @Override
    public AiCapabilities capabilities() {
        return new AiCapabilities(
                chatClientBuilderProvider.getIfAvailable() != null,
                chatClientBuilderProvider.getIfAvailable() != null,
                chatClientBuilderProvider.getIfAvailable() != null,
                embeddingModelProvider.getIfAvailable() != null,
                embeddingModelProvider.getIfAvailable() != null,
                imageModelProvider.getIfAvailable() != null,
                transcriptionModelProvider.getIfAvailable() != null,
                textToSpeechModelProvider.getIfAvailable() != null,
                moderationModelProvider.getIfAvailable() != null,
                true
        );
    }

    @Override
    public ChatResponse chat(ChatRequest request, String traceId) {
        List<RagChunk> references = request.useKnowledgeBase() ? searchKnowledge(request.message(), request.topK()) : List.of();
        String userMessage = buildUserMessage(request.message(), references);

        ChatClient.ChatClientRequestSpec spec = chatClient().prompt()
                .system(resolveSystemPrompt(request.systemPrompt(), request.useKnowledgeBase()))
                .user(userMessage);

        if (request.useTools()) {
            spec = spec.tools(platformAiTools);
        }

        String content = spec.call().content();
        return new ChatResponse(content, traceId, references);
    }

    public Flux<String> stream(ChatRequest request) {
        List<RagChunk> references = request.useKnowledgeBase() ? searchKnowledge(request.message(), request.topK()) : List.of();
        String userMessage = buildUserMessage(request.message(), references);

        ChatClient.ChatClientRequestSpec spec = chatClient().prompt()
                .system(resolveSystemPrompt(request.systemPrompt(), request.useKnowledgeBase()))
                .user(userMessage);

        if (request.useTools()) {
            spec = spec.tools(platformAiTools);
        }

        return spec.stream().content();
    }

    @Override
    public StructuredExtraction extract(StructuredExtractionRequest request) {
        BeanOutputConverter<StructuredExtraction> converter = new BeanOutputConverter<>(StructuredExtraction.class);
        String prompt = """
                请从下面内容中提取结构化信息。
                输出必须严格遵循给定 JSON 结构。
                %s

                内容：
                %s
                """.formatted(converter.getFormat(), request.message());

        String content = chatClient().prompt()
                .system("你是企业级平台的结构化信息抽取助手。")
                .user(prompt)
                .call()
                .content();
        return converter.convert(content);
    }

    @Override
    public EmbeddingResponse embedding(EmbeddingRequest request) {
        EmbeddingModel embeddingModel = requireModel(embeddingModelProvider, "EmbeddingModel");
        float[] vector = embeddingModel.embed(request.text());
        List<Float> preview = new ArrayList<>();
        for (int i = 0; i < Math.min(vector.length, 12); i++) {
            preview.add(vector[i]);
        }
        return new EmbeddingResponse(vector.length, preview);
    }

    @Override
    public List<RagChunk> ingest(RagIngestRequest request) {
        EmbeddingModel embeddingModel = requireModel(embeddingModelProvider, "EmbeddingModel");

        Map<String, Object> metadata = new HashMap<>();
        if (request.metadata() != null) {
            metadata.putAll(request.metadata());
        }
        metadata.put("title", request.title());
        metadata.put("documentId", request.documentId());
        metadata.put("ingestedAt", Instant.now().toString());

        Document source = new Document(request.content(), metadata);
        List<Document> chunks = TokenTextSplitter.builder().build().apply(List.of(source));
        List<RagChunk> result = new ArrayList<>();

        synchronized (vectorLock) {
            for (Document chunk : chunks) {
                String chunkId = UUID.randomUUID().toString();
                float[] vector = embeddingModel.embed(chunk.getText());
                Map<String, Object> chunkMetadata = new HashMap<>(chunk.getMetadata());
                chunkMetadata.put("chunkId", chunkId);
                VectorEntry entry = new VectorEntry(chunkId, request.documentId(), chunk.getText(), chunkMetadata, vector);
                vectorEntries.add(entry);
                result.add(toRagChunk(entry, 1.0d));
            }
            saveVectorStore();
        }

        return result;
    }

    @Override
    public ChatResponse ragAsk(RagAskRequest request, String traceId) {
        List<RagChunk> references = searchKnowledge(request.question(), request.topK());
        String userMessage = buildUserMessage(request.question(), references);
        String content = chatClient().prompt()
                .system(resolveSystemPrompt(null, true))
                .user(userMessage)
                .call()
                .content();
        return new ChatResponse(content, traceId, references);
    }

    @Override
    public ImageResponse generateImage(ImageRequest request) {
        ImageModel imageModel = requireModel(imageModelProvider, "ImageModel");
        OpenAiImageOptions imageOptions = OpenAiImageOptions.builder()
                .model(aiProperties.getImageModel())
                .build();
        var response = imageModel.call(new ImagePrompt(request.prompt(), imageOptions));
        var image = response.getResult().getOutput();
        return new ImageResponse(image.getUrl(), image.getB64Json());
    }

    @Override
    public ModerationResponse moderate(ModerationRequest request) {
        ModerationModel moderationModel = requireModel(moderationModelProvider, "ModerationModel");
        var response = moderationModel.call(new ModerationPrompt(request.text()));
        var moderation = response.getResult().getOutput();
        String detail = moderation.toString();
        boolean flagged = detail.toLowerCase().contains("flagged=true");
        return new ModerationResponse(flagged, moderation.getModel(), detail);
    }

    @Override
    public SpeechResponse speech(SpeechRequest request) {
        TextToSpeechModel speechModel = requireModel(textToSpeechModelProvider, "TextToSpeechModel");
        OpenAiAudioSpeechOptions options = OpenAiAudioSpeechOptions.builder()
                .model(aiProperties.getSpeechModel())
                .voice(aiProperties.getSpeechVoice())
                .build();
        var response = speechModel.call(new TextToSpeechPrompt(request.text(), options));
        byte[] audio = response.getResult().getOutput();
        return new SpeechResponse(options.getFormat(), Base64.getEncoder().encodeToString(audio));
    }

    @Override
    public TranscriptionResponse transcribe(TranscriptionPayload payload) {
        TranscriptionModel transcriptionModel = requireModel(transcriptionModelProvider, "TranscriptionModel");
        ByteArrayResource resource = new ByteArrayResource(payload.content()) {
            @Override
            public String getFilename() {
                return payload.filename();
            }
        };
        var response = transcriptionModel.call(new AudioTranscriptionPrompt(resource));
        return new TranscriptionResponse(response.getResult().getOutput());
    }

    private String buildUserMessage(String message, List<RagChunk> references) {
        if (references.isEmpty()) {
            return message;
        }
        String referenceText = references.stream()
                .map(chunk -> "[%s] %s".formatted(chunk.chunkId(), chunk.text()))
                .collect(Collectors.joining("\n\n"));
        return """
                用户问题：
                %s

                可参考的知识库片段：
                %s

                回答要求：
                1. 优先基于知识库片段回答。
                2. 如果知识库无法完全覆盖，请明确指出推断部分。
                3. 尽量在回答中引用片段编号。
                """.formatted(message, referenceText);
    }

    private String resolveSystemPrompt(String customPrompt, boolean knowledgeBaseEnabled) {
        String prompt = customPrompt == null || customPrompt.isBlank() ? aiProperties.getDefaultSystemPrompt() : customPrompt;
        if (!knowledgeBaseEnabled) {
            return prompt;
        }
        return prompt + "\n已启用企业知识库增强回答，请优先依据检索片段作答。";
    }

    private List<RagChunk> searchKnowledge(String query, int topK) {
        EmbeddingModel embeddingModel = requireModel(embeddingModelProvider, "EmbeddingModel");
        float[] queryVector = embeddingModel.embed(query);
        int actualTopK = topK <= 0 ? aiProperties.getRagTopK() : topK;
        synchronized (vectorLock) {
            return vectorEntries.stream()
                    .map(entry -> Map.entry(entry, cosineSimilarity(queryVector, entry.vector())))
                    .sorted(Map.Entry.<VectorEntry, Double>comparingByValue(Comparator.reverseOrder()))
                    .limit(actualTopK)
                    .map(item -> toRagChunk(item.getKey(), item.getValue()))
                    .toList();
        }
    }

    private RagChunk toRagChunk(VectorEntry entry, double score) {
        return new RagChunk(entry.chunkId(), entry.documentId(), score, entry.text(), entry.metadata());
    }

    private double cosineSimilarity(float[] first, float[] second) {
        if (first.length != second.length) {
            return 0.0d;
        }
        double dot = 0.0d;
        double firstNorm = 0.0d;
        double secondNorm = 0.0d;
        for (int i = 0; i < first.length; i++) {
            dot += first[i] * second[i];
            firstNorm += first[i] * first[i];
            secondNorm += second[i] * second[i];
        }
        if (firstNorm == 0.0d || secondNorm == 0.0d) {
            return 0.0d;
        }
        return dot / (Math.sqrt(firstNorm) * Math.sqrt(secondNorm));
    }

    private ChatClient chatClient() {
        ChatClient.Builder builder = chatClientBuilderProvider.getIfAvailable();
        if (builder == null) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "Spring AI chat client is not configured");
        }
        return builder.build();
    }

    private <T> T requireModel(ObjectProvider<T> provider, String type) {
        T model = provider.getIfAvailable();
        if (model == null) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, type + " is not configured");
        }
        return model;
    }

    private void loadVectorStore() {
        Path path = resolveVectorStorePath();
        if (!Files.exists(path)) {
            return;
        }
        try {
            List<VectorEntry> stored = objectMapper.readValue(path.toFile(), new TypeReference<>() {
            });
            vectorEntries.clear();
            vectorEntries.addAll(stored);
        } catch (IOException exception) {
            log.warn("Failed to load AI vector store from {}", path, exception);
        }
    }

    private void saveVectorStore() {
        Path path = resolveVectorStorePath();
        try {
            Files.createDirectories(path.getParent());
            objectMapper.writerWithDefaultPrettyPrinter().writeValue(path.toFile(), vectorEntries);
        } catch (IOException exception) {
            log.warn("Failed to save AI vector store to {}", path, exception);
        }
    }

    private Path resolveVectorStorePath() {
        return Path.of(aiProperties.getRagStoreFile()).toAbsolutePath();
    }

    private record VectorEntry(
            String chunkId,
            String documentId,
            String text,
            Map<String, Object> metadata,
            float[] vector
    ) {
    }
}
