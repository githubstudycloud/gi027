package com.enterprise.platform.ai;

import java.util.List;
import java.util.Map;

public final class AiApiModels {

    private AiApiModels() {
    }

    public record AiCapabilities(
            boolean chatEnabled,
            boolean structuredOutputEnabled,
            boolean toolCallingEnabled,
            boolean ragEnabled,
            boolean embeddingEnabled,
            boolean imageEnabled,
            boolean transcriptionEnabled,
            boolean textToSpeechEnabled,
            boolean moderationEnabled,
            boolean mcpReady
    ) {
    }

    public record ChatRequest(
            String message,
            String systemPrompt,
            boolean useTools,
            boolean useKnowledgeBase,
            int topK
    ) {
    }

    public record ChatResponse(
            String content,
            String traceId,
            List<RagChunk> references
    ) {
    }

    public record StructuredExtractionRequest(
            String message
    ) {
    }

    public record StructuredExtraction(
            String title,
            String summary,
            List<String> actionItems,
            String riskLevel
    ) {
    }

    public record EmbeddingRequest(
            String text
    ) {
    }

    public record EmbeddingResponse(
            int dimensions,
            List<Float> vectorPreview
    ) {
    }

    public record RagIngestRequest(
            String documentId,
            String title,
            String content,
            Map<String, Object> metadata
    ) {
    }

    public record RagAskRequest(
            String question,
            int topK
    ) {
    }

    public record RagChunk(
            String chunkId,
            String documentId,
            double score,
            String text,
            Map<String, Object> metadata
    ) {
    }

    public record ImageRequest(
            String prompt
    ) {
    }

    public record ImageResponse(
            String url,
            String b64Json
    ) {
    }

    public record ModerationRequest(
            String text
    ) {
    }

    public record ModerationResponse(
            boolean flagged,
            String model,
            String detail
    ) {
    }

    public record SpeechRequest(
            String text
    ) {
    }

    public record SpeechResponse(
            String format,
            String audioBase64
    ) {
    }

    public record TranscriptionPayload(
            String filename,
            byte[] content
    ) {
    }

    public record TranscriptionResponse(
            String text
    ) {
    }
}
