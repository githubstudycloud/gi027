package com.enterprise.platform.core;

import java.util.List;

public record SystemStatus(
        String applicationName,
        String activeProfile,
        String javaVersion,
        boolean secureModeEnabled,
        List<String> capabilities
) {
}
