# log-analysis-pipeline-v2

性能优化版的 [log-analysis-pipeline](../log-analysis-pipeline)。
功能与产物与 v1 等价，关键热路径在 200 / 1000 / 2000 / 5000 条规模上**稳定快约 2 倍**。

## 何时用 v2
- 单次输入接近或超过 1000 条记录
- 希望保留 v1 的所有诉求（多平台启动器、Python/Node 兜底、多语言、单表多行渲染、嵌套明细、性能 fixture）
- 需要可复现的 v1 vs v2 性能对比报告

## 跑通最小例子（Windows）
```powershell
cd .github/skills/log-analysis-pipeline-v2
python scripts/run-skill-tests.py . zh-CN          # 双语测试
python scripts/benchmark.py                         # v1 vs v2 对比
powershell -NoProfile -File scripts/run-skill-tests.ps1 -Locale en-US
node scripts/run-skill.mjs en-US
```

## 跑通最小例子（Linux / macOS）
```bash
cd .github/skills/log-analysis-pipeline-v2
bash scripts/run-skill.sh zh-CN
python3 scripts/benchmark.py
```

## 主要文件
- [SKILL.md](./SKILL.md) — Skill 行为与差异说明
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 架构与流水线
- [GUIDE-FOR-BEGINNERS.md](./GUIDE-FOR-BEGINNERS.md) — 新手引导
- [scripts/log_analysis_core_v2.py](./scripts/log_analysis_core_v2.py) — 核心
- [scripts/benchmark.py](./scripts/benchmark.py) — v1 vs v2 基准
- [reports/benchmark.md](./reports/benchmark.md) — 最近一次基准结果
- [reports/test-report.md](./reports/test-report.md) — 测试报告

## 输出
- `reports/output/log-analysis-report.md`
- `reports/output/normalized-records.json`（紧凑 JSON）
- `reports/output/summary.json`
- `reports/test-report.<locale>.md`
- `reports/benchmark.md` + `reports/benchmark.json`

## 与 v1 行为兼容性
- Markdown 表头、列顺序、`<br>` 多行渲染、`N/A` 占位、维度排序键全部一致
- normalized-records.json 字段集合相同，仅 v2 默认紧凑格式
- summary.json 字段一致

## 想直接发给同事用？
本目录用于**测试/验证/基准对比**。如果要把能力直接发给同事使用，请使用零版本号的轻量骨架：
[../log-analyzer/](../log-analyzer/) — 同一份核心代码，但目录精简、文档极简、便于整目录覆盖升级。
