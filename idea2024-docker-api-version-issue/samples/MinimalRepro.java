package samples;

import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.core.DefaultDockerClientConfig;
import com.github.dockerjava.core.DockerClientImpl;
import com.github.dockerjava.core.RemoteApiVersion;
import com.github.dockerjava.transport.DockerHttpClient;
import com.github.dockerjava.httpclient5.ApacheDockerHttpClient;

/**
 * 最小复现 / 验证程序。
 *
 * 使用方法：
 * 1. 引入 docker-java 3.4.0+ 依赖（见 README 方案 D）
 * 2. 运行 main()：
 *    - 如果 Docker Engine >= 25.0 且使用 VERSION_1_24，将复现 400 错误
 *    - 切换为 VERSION_1_44 后正常返回版本信息
 */
public class MinimalRepro {

    public static void main(String[] args) {
        // ❌ 复现错误：旧 API 版本
        // tryConnect(RemoteApiVersion.VERSION_1_24);

        // ✅ 正确：与 Engine 25+ 兼容
        tryConnect(RemoteApiVersion.VERSION_1_44);
    }

    private static void tryConnect(RemoteApiVersion apiVersion) {
        DefaultDockerClientConfig config = DefaultDockerClientConfig.createDefaultConfigBuilder()
                // Windows 命名管道；Linux 用 unix:///var/run/docker.sock
                .withDockerHost("npipe:////./pipe/docker_engine")
                .withApiVersion(apiVersion)
                .build();

        DockerHttpClient httpClient = new ApacheDockerHttpClient.Builder()
                .dockerHost(config.getDockerHost())
                .sslConfig(config.getSSLConfig())
                .build();

        try (DockerClient client = DockerClientImpl.getInstance(config, httpClient)) {
            System.out.println("Server version: " + client.versionCmd().exec().getVersion());
            System.out.println("API version  : " + client.versionCmd().exec().getApiVersion());
        } catch (Exception e) {
            System.err.println("Failed with apiVersion=" + apiVersion + " : " + e.getMessage());
        }
    }
}
