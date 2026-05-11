# 新手引导（log-analysis-pipeline-v2）

## 0. 我应该用 v1 还是 v2？
- 只有零星几十条记录、想要最稳定的版本：用 [v1](../log-analysis-pipeline)
- 一次要分析 1000 条以上、或想要 v1/v2 对比基准：用 v2（本目录）

## 1. 环境检查
- Python ≥ 3.9（脚本只依赖 stdlib，不需要 pip install）
- Node ≥ 18（仅当走 Node 兜底链路）
- PowerShell ≥ 5.1（Windows 默认自带，命令名 `powershell`）
- Linux/macOS：bash + python3

> 下文 `<skills-root>` = 你实际安装 skill 的目录：`.github/skills`（Copilot）/ `.claude/skills`（Claude Code）/ `.opencode/skills`（OpenCode）/ Codex 等。脚本通过 `__file__` 自动定位资源，所以只需 `cd` 到 skill 目录后用相对路径调用即可。

## 2. 三步跑通
```powershell
# Windows
cd <skills-root>/log-analysis-pipeline-v2
python scripts/run-skill-tests.py . zh-CN     # ① 跑测试 + 生成 fixture
python scripts/benchmark.py                    # ② 跑 v1 vs v2 性能对比
notepad reports/benchmark.md                   # ③ 看对比报告
```

```bash
# Linux / macOS
cd <skills-root>/log-analysis-pipeline-v2
bash scripts/run-skill.sh zh-CN
python3 scripts/benchmark.py
cat reports/benchmark.md
```

## 3. 用自己的日志文件
```powershell
python scripts/analyze-logs.py analyze `
    --input-files path/to/a.json path/to/b.txt `
    --output-dir ./out `
    --locale zh-CN
```
关键参数：
- `--field-map path.json`：自定义字段别名映射（结构示例：`assets/field-map.example.json`）
- `--dimension-rules path.json`：自定义聚类维度
- `--locale en-US|zh-CN|<other>`：选 locale；自定义可用 `--locale-file path.json`

## 4. 常见报错排查
| 报错 | 原因 | 解决 |
|---|---|---|
| `Python runtime not found` | PowerShell/Bash 找不到 python | 安装 Python 3.9+，或装 Node 走 mjs 兜底 |
| `No supported input files were found.` | 路径错或后缀不在 `.json/.txt` | 检查路径，仅支持这两种 |
| `No valid records were parsed` | 文件为空或字段全部不匹配 | 提供 `--field-map` 让 alias 命中你的字段名 |
| benchmark 报 `v1 not found` | 仓库里没有 v1 兄弟目录 | 保留 `../log-analysis-pipeline` 与 v2 平级 |

## 5. 把它接到主 Skill
主 Skill 调本 Skill 的标准入参：
1. 一组 JSON/TXT 日志分析文件路径
2. 可选字段映射文件 + 维度规则文件 + locale
3. 输出目录

返回的 `summary.json` 即可继续被下一个 Skill 消费。
