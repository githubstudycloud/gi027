package com.enterprise.platform.boot.service;

import com.enterprise.platform.core.SystemFacade;
import com.enterprise.platform.core.SystemStatus;
import java.util.List;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Service;

@Service
public class DefaultSystemFacade implements SystemFacade {

    private final Environment environment;

    public DefaultSystemFacade(Environment environment) {
        this.environment = environment;
    }

    @Override
    public SystemStatus getSystemStatus() {
        String applicationName = environment.getProperty("spring.application.name", "enterprise-platform");
        String[] profiles = environment.getActiveProfiles();
        String activeProfile = profiles.length == 0 ? "default" : String.join(",", profiles);
        return new SystemStatus(
                applicationName,
                activeProfile,
                Runtime.version().toString(),
                true,
                List.of("web", "security", "validation", "actuator", "trace-id")
        );
    }
}
