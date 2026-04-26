package com.enterprise.platform.boot.ai.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "platform.ai")
public class AiProperties {

    private String defaultSystemPrompt = """
            你是企业级 Spring Boot 4.x 平台内置 AI 助手。
            回答时优先使用简洁、准确、可执行的中文。
            如果用户问题涉及平台运行状态、时间、系统能力，请优先通过可用工具获取实时信息。
            如果启用了知识库，请优先基于知识库内容回答，不要虚构不存在的制度或接口。
            """;

    private int ragTopK = 4;

    private String ragStoreFile = "data/ai/vector-store.json";

    private String imageModel = "gpt-image-1";

    private String transcriptionModel = "gpt-4o-mini-transcribe";

    private String speechModel = "gpt-4o-mini-tts";

    private String speechVoice = "alloy";

    public String getDefaultSystemPrompt() {
        return defaultSystemPrompt;
    }

    public void setDefaultSystemPrompt(String defaultSystemPrompt) {
        this.defaultSystemPrompt = defaultSystemPrompt;
    }

    public int getRagTopK() {
        return ragTopK;
    }

    public void setRagTopK(int ragTopK) {
        this.ragTopK = ragTopK;
    }

    public String getRagStoreFile() {
        return ragStoreFile;
    }

    public void setRagStoreFile(String ragStoreFile) {
        this.ragStoreFile = ragStoreFile;
    }

    public String getImageModel() {
        return imageModel;
    }

    public void setImageModel(String imageModel) {
        this.imageModel = imageModel;
    }

    public String getTranscriptionModel() {
        return transcriptionModel;
    }

    public void setTranscriptionModel(String transcriptionModel) {
        this.transcriptionModel = transcriptionModel;
    }

    public String getSpeechModel() {
        return speechModel;
    }

    public void setSpeechModel(String speechModel) {
        this.speechModel = speechModel;
    }

    public String getSpeechVoice() {
        return speechVoice;
    }

    public void setSpeechVoice(String speechVoice) {
        this.speechVoice = speechVoice;
    }
}
