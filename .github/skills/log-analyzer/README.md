# log-analyzer

日志分析汇总助手的**可分发骨架版**。无版本后缀，便于后续整目录覆盖升级。

## 一行命令自检
```powershell
python scripts/log_analysis_core.py test --skill-root . --locale en-US
```

会自动：
1. 生成 10 / 20 / 200 / 1000 / 5000 五档样例（位于 `tests/fixtures/`）。
2. 跑结构化 JSON+TXT 合并、`key_evdence` 旧拼写兼容、同义列名等验证。
3. 跑端到端性能采样，写入 `reports/test-report.md`。

## 一行命令分析自己的日志
```powershell
python scripts/log_analysis_core.py analyze --input-files <file1> <file2> --output-dir reports/output --locale zh-CN
```

可选：`--field-map`、`--dimension-rules`、`--report-layout` 指向 `assets/` 下的示例或自定义配置。

## ⚠️ 重要约定
- **不要重命名或移动 `scripts/`、`assets/`、`tests/`、`reports/` 目录**。脚本依赖目录相对位置解析资源。
- 若需要升级，**整目录覆盖** `log-analyzer/` 即可。
- **想让自然语言触发也走自己的配置**：把 `assets/*.example.json` 复制并改名为同名无 `.example` 的文件（如 `field-map.json`）即可，脚本会自动优先加载。
- 如需高级特性（v1 vs v2 基准、多平台启动器、Node 兜底），请使用 [../log-analysis-pipeline-v2/](../log-analysis-pipeline-v2/)。

更多细节看 [SKILL.md](./SKILL.md)。
