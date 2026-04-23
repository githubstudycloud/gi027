package com.enterprise.platform.boot.web;

import com.enterprise.platform.common.ApiResponse;
import com.enterprise.platform.core.SystemFacade;
import com.enterprise.platform.core.SystemStatus;
import java.util.Map;
import org.slf4j.MDC;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import static com.enterprise.platform.boot.filter.TraceIdFilter.TRACE_ID_KEY;

@RestController
@RequestMapping("/api/v1/system")
public class SystemController {

    private final SystemFacade systemFacade;

    public SystemController(SystemFacade systemFacade) {
        this.systemFacade = systemFacade;
    }

    @GetMapping("/ping")
    public ApiResponse<Map<String, String>> ping() {
        return ApiResponse.success(Map.of("status", "pong"), MDC.get(TRACE_ID_KEY));
    }

    @GetMapping("/status")
    public ApiResponse<SystemStatus> status() {
        return ApiResponse.success(systemFacade.getSystemStatus(), MDC.get(TRACE_ID_KEY));
    }
}
