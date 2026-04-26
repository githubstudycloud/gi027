package com.enterprise.platform.boot.ai.web;

import com.enterprise.platform.ai.AiApiModels;
import com.enterprise.platform.ai.AiApiModels.ChatRequest;
import com.enterprise.platform.ai.AiApiModels.RagAskRequest;
import com.enterprise.platform.ai.EnterpriseAiFacade;
import com.enterprise.platform.boot.ai.service.SpringAiEnterpriseFacade;
import com.enterprise.platform.boot.filter.TraceIdFilter;
import com.enterprise.platform.common.ApiResponse;
import jakarta.servlet.http.HttpServletRequest;
import java.io.IOException;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@RequestMapping("/api/v1/ai")
public class AiController {

    private final EnterpriseAiFacade enterpriseAiFacade;
    private final SpringAiEnterpriseFacade springAiEnterpriseFacade;

    public AiController(EnterpriseAiFacade enterpriseAiFacade,
                        SpringAiEnterpriseFacade springAiEnterpriseFacade) {
        this.enterpriseAiFacade = enterpriseAiFacade;
        this.springAiEnterpriseFacade = springAiEnterpriseFacade;
    }

    @GetMapping("/capabilities")
    public ApiResponse<AiApiModels.AiCapabilities> capabilities(HttpServletRequest request) {
        return ApiResponse.success(enterpriseAiFacade.capabilities(), request.getHeader(TraceIdFilter.TRACE_ID_HEADER));
    }

    @PostMapping("/chat")
    public ApiResponse<AiApiModels.ChatResponse> chat(@org.springframework.web.bind.annotation.RequestBody ChatRequest request,
                                                      HttpServletRequest servletRequest) {
        return ApiResponse.success(
                enterpriseAiFacade.chat(request, servletRequest.getHeader(TraceIdFilter.TRACE_ID_HEADER)),
                servletRequest.getHeader(TraceIdFilter.TRACE_ID_HEADER)
        );
    }

    @PostMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter chatStream(@org.springframework.web.bind.annotation.RequestBody ChatRequest request,
                                 HttpServletRequest servletRequest) {
        String traceId = servletRequest.getHeader(TraceIdFilter.TRACE_ID_HEADER);
        SseEmitter emitter = new SseEmitter(0L);
        springAiEnterpriseFacade.stream(request)
                .subscribe(chunk -> send(emitter, ApiResponse.success(chunk, traceId)),
                        emitter::completeWithError,
                        emitter::complete);
        return emitter;
    }

    @PostMapping("/extract")
    public ApiResponse<AiApiModels.StructuredExtraction> extract(
            @org.springframework.web.bind.annotation.RequestBody AiApiModels.StructuredExtractionRequest request,
            HttpServletRequest servletRequest) {
        return ApiResponse.success(
                enterpriseAiFacade.extract(request),
                servletRequest.getHeader(TraceIdFilter.TRACE_ID_HEADER)
        );
    }

    @PostMapping("/embedding")
    public ApiResponse<AiApiModels.EmbeddingResponse> embedding(
            @org.springframework.web.bind.annotation.RequestBody AiApiModels.EmbeddingRequest request,
            HttpServletRequest servletRequest) {
        return ApiResponse.success(
                enterpriseAiFacade.embedding(request),
                servletRequest.getHeader(TraceIdFilter.TRACE_ID_HEADER)
        );
    }

    @PostMapping("/rag/ingest")
    public ApiResponse<java.util.List<AiApiModels.RagChunk>> ingest(
            @org.springframework.web.bind.annotation.RequestBody AiApiModels.RagIngestRequest request,
            HttpServletRequest servletRequest) {
        return ApiResponse.success(
                enterpriseAiFacade.ingest(request),
                servletRequest.getHeader(TraceIdFilter.TRACE_ID_HEADER)
        );
    }

    @PostMapping("/rag/ask")
    public ApiResponse<AiApiModels.ChatResponse> ragAsk(@org.springframework.web.bind.annotation.RequestBody RagAskRequest request,
                                                        HttpServletRequest servletRequest) {
        return ApiResponse.success(
                enterpriseAiFacade.ragAsk(request, servletRequest.getHeader(TraceIdFilter.TRACE_ID_HEADER)),
                servletRequest.getHeader(TraceIdFilter.TRACE_ID_HEADER)
        );
    }

    @PostMapping("/image")
    public ApiResponse<AiApiModels.ImageResponse> image(@org.springframework.web.bind.annotation.RequestBody AiApiModels.ImageRequest request,
                                                        HttpServletRequest servletRequest) {
        return ApiResponse.success(
                enterpriseAiFacade.generateImage(request),
                servletRequest.getHeader(TraceIdFilter.TRACE_ID_HEADER)
        );
    }

    @PostMapping("/moderation")
    public ApiResponse<AiApiModels.ModerationResponse> moderation(
            @org.springframework.web.bind.annotation.RequestBody AiApiModels.ModerationRequest request,
            HttpServletRequest servletRequest) {
        return ApiResponse.success(
                enterpriseAiFacade.moderate(request),
                servletRequest.getHeader(TraceIdFilter.TRACE_ID_HEADER)
        );
    }

    @PostMapping("/speech")
    public ApiResponse<AiApiModels.SpeechResponse> speech(
            @org.springframework.web.bind.annotation.RequestBody AiApiModels.SpeechRequest request,
            HttpServletRequest servletRequest) {
        return ApiResponse.success(
                enterpriseAiFacade.speech(request),
                servletRequest.getHeader(TraceIdFilter.TRACE_ID_HEADER)
        );
    }

    @PostMapping(value = "/transcription", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ApiResponse<AiApiModels.TranscriptionResponse> transcription(@RequestPart("file") MultipartFile file,
                                                                        HttpServletRequest servletRequest) throws IOException {
        AiApiModels.TranscriptionPayload payload = new AiApiModels.TranscriptionPayload(file.getOriginalFilename(), file.getBytes());
        return ApiResponse.success(
                enterpriseAiFacade.transcribe(payload),
                servletRequest.getHeader(TraceIdFilter.TRACE_ID_HEADER)
        );
    }

    private void send(SseEmitter emitter, Object data) {
        try {
            emitter.send(SseEmitter.event().name("message").data(data));
        } catch (IOException exception) {
            throw new IllegalStateException(exception);
        }
    }
}
