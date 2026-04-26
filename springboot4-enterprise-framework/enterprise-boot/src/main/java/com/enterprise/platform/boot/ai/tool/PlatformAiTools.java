package com.enterprise.platform.boot.ai.tool;

import com.enterprise.platform.core.SystemFacade;
import java.time.LocalDateTime;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Component;

@Component
public class PlatformAiTools {

    private final SystemFacade systemFacade;

    public PlatformAiTools(SystemFacade systemFacade) {
        this.systemFacade = systemFacade;
    }

    @Tool(description = "获取当前应用平台的系统状态，包括应用名、激活环境、JVM 版本和平台能力列表")
    public String getPlatformStatus() {
        return systemFacade.getSystemStatus().toString();
    }

    @Tool(description = "获取当前系统时间，用于回答今天日期、现在几点、明天星期几等实时问题")
    public String getCurrentDateTime() {
        return LocalDateTime.now().toString();
    }

    @Tool(description = "根据系统能力名称判断平台是否支持某项能力，例如 web、security、validation、actuator、trace-id")
    public String supportsCapability(String capability) {
        boolean supported = systemFacade.getSystemStatus().capabilities().stream()
                .anyMatch(item -> item.equalsIgnoreCase(capability));
        return supported ? "SUPPORTED" : "UNSUPPORTED";
    }
}
