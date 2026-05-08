# log-analysis-pipeline 架构说明

## 目标
这个 Skill 的目标是把分散的 JSON/TXT 日志分析结果，统一转换成一份结构化、可本地化、可扩展的 Markdown 报告。

## 架构层次

### 1. 入口层
- `SKILL.md` 负责描述技能触发词、工作流程和输出规范
- PowerShell / Bash / Python / Node.js 入口负责选择合适的运行方式

### 2. 核心层
- `scripts/log_analysis_core.py` 是统一的分析与测试核心
- 它负责解析、归一化、分组、报告生成、测试样例生成

### 3. 配置层
- `assets/field-map.example.json`：字段映射示例
- `assets/dimension-rules.example.json`：分组规则示例
- `assets/locales/*.json`：多语言文案包
- `assets/runtime-config.example.json`：平台与运行时选择示例
- `assets/report-layout.example.json`：报告布局示例

### 4. 测试层
- `scripts/generate-test-data.py` 生成 10 / 20 / 200 条测试样例
- `scripts/run-skill-tests.py` 执行正确性与性能测试
- `reports/test-report.md` 输出测试结果

### 5. 输出层
- `reports/output/log-analysis-report.md`
- `reports/output/normalized-records.json`
- `reports/output/summary.json`

## 设计原则
- Markdown 是唯一强制输出格式
- 优先单表聚合，避免多个零散表格
- 多语言通过配置驱动，不把文本硬编码在逻辑里
- 平台选择优先“本机最优”，再退回到 Python 或 Node.js
- 性能测试必须有 10 / 20 / 200 三档样例

## 扩展方式
- 增加字段别名：修改字段映射示例
- 增加新语言：新增 locale JSON 文件
- 调整布局：修改报告布局示例
- 扩展性能测试：修改样例生成规模
