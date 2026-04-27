package com.enterprise.platform.common;

public enum ErrorCode {
    SUCCESS("00000"),
    BUSINESS_ERROR("B0001"),
    VALIDATION_ERROR("V0001"),
    UNAUTHORIZED("A0001"),
    RATE_LIMITED("A0002"),
    SYSTEM_ERROR("S0001");

    private final String code;

    ErrorCode(String code) {
        this.code = code;
    }

    public String code() {
        return code;
    }
}
