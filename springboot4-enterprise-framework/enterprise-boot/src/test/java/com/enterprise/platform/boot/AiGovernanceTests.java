package com.enterprise.platform.boot;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(properties = {
        "platform.ai.governance.requests-per-minute=2"
})
@AutoConfigureMockMvc
class AiGovernanceTests {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void aiEndpointsShouldReturnTooManyRequestsWhenRateLimitExceeded() throws Exception {
        var requestBuilder = get("/api/v1/ai/capabilities").with(request -> {
            request.setRemoteAddr("198.51.100.10");
            return request;
        });

        mockMvc.perform(requestBuilder)
                .andExpect(status().isOk());

        mockMvc.perform(requestBuilder)
                .andExpect(status().isOk());

        mockMvc.perform(requestBuilder)
                .andExpect(status().isTooManyRequests())
                .andExpect(jsonPath("$.code").value("A0002"));
    }
}
