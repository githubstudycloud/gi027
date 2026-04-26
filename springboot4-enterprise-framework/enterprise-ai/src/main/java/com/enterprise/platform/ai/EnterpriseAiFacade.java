package com.enterprise.platform.ai;

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
import java.util.List;

public interface EnterpriseAiFacade {

    AiCapabilities capabilities();

    ChatResponse chat(ChatRequest request, String traceId);

    StructuredExtraction extract(StructuredExtractionRequest request);

    EmbeddingResponse embedding(EmbeddingRequest request);

    List<RagChunk> ingest(RagIngestRequest request);

    ChatResponse ragAsk(RagAskRequest request, String traceId);

    ImageResponse generateImage(ImageRequest request);

    ModerationResponse moderate(ModerationRequest request);

    SpeechResponse speech(SpeechRequest request);

    TranscriptionResponse transcribe(TranscriptionPayload payload);
}
