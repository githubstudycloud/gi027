package com.enterprise.platform.boot.ai.web;

import com.enterprise.platform.boot.ai.config.AiProperties;
import com.enterprise.platform.boot.filter.TraceIdFilter;
import com.enterprise.platform.common.BusinessException;
import com.enterprise.platform.common.ErrorCode;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Component
public class AiGovernanceInterceptor implements HandlerInterceptor {

    private static final Logger auditLog = LoggerFactory.getLogger("AI_AUDIT");
    private static final String START_TIME_ATTRIBUTE = AiGovernanceInterceptor.class.getName() + ".startTime";

    private final AiProperties aiProperties;
    private final Map<String, WindowCounter> requestCounters = new ConcurrentHashMap<>();

    public AiGovernanceInterceptor(AiProperties aiProperties) {
        this.aiProperties = aiProperties;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        request.setAttribute(START_TIME_ATTRIBUTE, System.currentTimeMillis());
        if (aiProperties.getGovernance().isRateLimitEnabled()) {
            enforceRateLimit(request);
        }
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request,
                                HttpServletResponse response,
                                Object handler,
                                Exception ex) {
        if (!aiProperties.getGovernance().isAuditEnabled()) {
            return;
        }

        long startedAt = (long) request.getAttribute(START_TIME_ATTRIBUTE);
        long durationMs = Math.max(0L, System.currentTimeMillis() - startedAt);
        String principal = request.getUserPrincipal() == null ? "anonymous" : request.getUserPrincipal().getName();
        String traceId = request.getHeader(TraceIdFilter.TRACE_ID_HEADER);
        if (traceId == null || traceId.isBlank()) {
            traceId = MDC.get(TraceIdFilter.TRACE_ID_KEY);
        }

        auditLog.info(
                "traceId={} principal={} method={} path={} status={} durationMs={} remoteAddr={} contentType={}",
                traceId,
                principal,
                request.getMethod(),
                request.getRequestURI(),
                response.getStatus(),
                durationMs,
                request.getRemoteAddr(),
                request.getContentType()
        );
    }

    private void enforceRateLimit(HttpServletRequest request) {
        int limit = Math.max(1, aiProperties.getGovernance().getRequestsPerMinute());
        long windowMinute = Instant.now().getEpochSecond() / 60;
        String subject = resolveSubject(request);

        WindowCounter current = requestCounters.compute(subject, (key, existing) -> {
            if (existing == null || existing.windowMinute() != windowMinute) {
                return new WindowCounter(windowMinute, 1);
            }
            return new WindowCounter(windowMinute, existing.count() + 1);
        });

        if (current.count() > limit) {
            throw new BusinessException(
                    ErrorCode.RATE_LIMITED,
                    "ai request rate limit exceeded, please retry later"
            );
        }
    }

    private String resolveSubject(HttpServletRequest request) {
        if (request.getUserPrincipal() != null) {
            return "user:" + request.getUserPrincipal().getName();
        }
        return "anonymous:" + request.getRemoteAddr();
    }

    private record WindowCounter(long windowMinute, int count) {
    }
}
