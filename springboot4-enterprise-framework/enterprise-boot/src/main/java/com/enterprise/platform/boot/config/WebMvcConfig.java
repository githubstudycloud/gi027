package com.enterprise.platform.boot.config;

import com.enterprise.platform.boot.ai.web.AiGovernanceInterceptor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    private final AiGovernanceInterceptor aiGovernanceInterceptor;

    public WebMvcConfig(AiGovernanceInterceptor aiGovernanceInterceptor) {
        this.aiGovernanceInterceptor = aiGovernanceInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(aiGovernanceInterceptor)
                .addPathPatterns("/api/v1/ai/**");
    }
}
