package com.enterprise.platform.boot;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.httpBasic;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class EnterpriseApplicationTests {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void pingEndpointShouldBeAccessibleWithoutAuthentication() throws Exception {
        mockMvc.perform(get("/api/v1/system/ping"))
                .andExpect(status().isOk())
                .andExpect(header().exists("X-Trace-Id"))
                .andExpect(jsonPath("$.code").value("00000"))
                .andExpect(jsonPath("$.data.status").value("pong"));
    }

    @Test
    void statusEndpointShouldRequireAuthentication() throws Exception {
        mockMvc.perform(get("/api/v1/system/status"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void statusEndpointShouldReturnDataAfterAuthentication() throws Exception {
        mockMvc.perform(get("/api/v1/system/status").with(httpBasic("platform-admin", "changeit")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.applicationName").value("enterprise-platform"))
                .andExpect(jsonPath("$.data.secureModeEnabled").value(true));
    }
}
