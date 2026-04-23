package com.enterprise.platform.common;

import java.time.Instant;

public record ApiResponse<T>(
        Instant timestamp,
        String code,
        String message,
        String traceId,
        T data
) {

    public static <T> ApiResponse<T> success(T data, String traceId) {
        return new ApiResponse<>(Instant.now(), ErrorCode.SUCCESS.code(), "success", traceId, data);
    }

    public static ApiResponse<Void> failure(ErrorCode errorCode, String message, String traceId) {
        return new ApiResponse<>(Instant.now(), errorCode.code(), message, traceId, null);
    }
}
