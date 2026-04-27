package com.enterprise.platform.boot.advice;

import com.enterprise.platform.boot.filter.TraceIdFilter;
import com.enterprise.platform.common.ApiResponse;
import com.enterprise.platform.common.BusinessException;
import com.enterprise.platform.common.ErrorCode;
import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.MDC;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException exception,
                                                                     HttpServletRequest request) {
        HttpStatus status = exception.getErrorCode() == ErrorCode.RATE_LIMITED
                ? HttpStatus.TOO_MANY_REQUESTS
                : HttpStatus.BAD_REQUEST;
        return ResponseEntity.status(status)
                .body(ApiResponse.failure(exception.getErrorCode(), exception.getMessage(), resolveTraceId(request)));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidationException(MethodArgumentNotValidException exception,
                                                                       HttpServletRequest request) {
        FieldError fieldError = exception.getBindingResult().getFieldErrors().stream().findFirst().orElse(null);
        String message = fieldError == null ? "validation failed" : fieldError.getField() + " " + fieldError.getDefaultMessage();
        return ResponseEntity.badRequest()
                .body(ApiResponse.failure(ErrorCode.VALIDATION_ERROR, message, resolveTraceId(request)));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleUnhandledException(Exception exception,
                                                                      HttpServletRequest request) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.failure(ErrorCode.SYSTEM_ERROR, "internal server error", resolveTraceId(request)));
    }

    private String resolveTraceId(HttpServletRequest request) {
        String traceId = request.getHeader(TraceIdFilter.TRACE_ID_HEADER);
        return traceId == null ? MDC.get(TraceIdFilter.TRACE_ID_KEY) : traceId;
    }
}
