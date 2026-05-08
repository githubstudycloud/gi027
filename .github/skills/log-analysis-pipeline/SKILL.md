---
name: log-analysis-pipeline
description: 日志分析汇总助手 - 当用户提供一个或多个 JSON/TXT 日志分析文件（可来自不同路径、也可由其他 Skill 生成）时，自动解析字段、按规则聚类、生成 Markdown 表格报告（支持嵌套明细）。当用户说"日志分析"、"汇总日志"、"解析json日志"、"txt问题归类"、"生成问题表格"、"测试日志skill"时自动激活。
argument-hint: "[日志文件路径列表，可选规则文件路径，可选输出路径]"
user-invocable: true
---

# 日志分析汇总助手（JSON/TXT → Markdown）

用于把分散路径下的日志分析文件统一抽取、归类、去重、相似合并，并输出结构化 Markdown 报告。

## 适用场景
- 主 Skill 先生成了 `json` / `txt` 分析文件，需要二次汇总
- 输入文件来自多个固定路径，且格式不完全一致
- 需要按“问题大类 / 问题小类 / 根因诊断结论”等维度统计
- 需要自动生成测试数据、执行测试并产出测试报告

## 参数
- `$ARGUMENTS`：
  - 必填优先：日志文件路径（可多个）
  - 可选：字段映射配置文件（JSON）
  - 可选：维度规则配置文件（JSON）
  - 可选：输出目录

## 默认字段语义
若未提供字段映射配置，默认按以下字段识别（中英混合）：
- 用例名称：`useCaseName`, `caseName`, `用例名称`
- 问题大类：`issueCategory`, `problemCategory`, `问题大类`
- 问题小类：`issueSubcategory`, `problemSubcategory`, `问题小类`
- 根因诊断结论：`rootCauseConclusion`, `rootCause`, `根因诊断结论`
- 关键佐证信息：`keyEvidence`, `evidence`, `关键佐证信息`
- 问题修复动作：`fixAction`, `repairAction`, `问题修复动作`
- 问题修复结论：`fixConclusion`, `repairConclusion`, `问题修复结论`
- 用例重跑结论：`rerunConclusion`, `rerunResult`, `用例重跑结论`

## 工作流程

### 1) 收集输入与规则
1. 若 `$ARGUMENTS` 未给出路径，提示用户提供：
   - 日志文件路径列表（支持 glob 展开后的绝对路径）
   - 可选字段映射文件（例如 `./assets/field-map.example.json`）
   - 可选统计规则文件（例如 `./assets/dimension-rules.example.json`）
2. 校验输入文件存在，过滤不支持类型（仅 `.json` / `.txt`）。

### 2) 解析文件
1. JSON：
   - 支持对象数组、单对象、`records/items/data` 容器结构。
   - 根据字段映射提取标准字段。
2. TXT：
   - 按固定标题解析键值（例如 `用例名称: xxx`）。
   - 支持多段记录（空行分隔）。

### 3) 归一化与分组
1. 标准化记录字段（缺失值记为 `N/A`）。
2. 默认按三维分类：
   - `问题大类` → `问题小类` → `根因诊断结论`
3. 若提供规则文件，按规则覆盖默认维度。
4. 对近似文本进行轻量规范化（空白折叠、大小写归一、常见同义词对齐）。

### 4) 输出报告
执行 [analyze-logs.ps1](./scripts/analyze-logs.ps1)：
- 生成 `markdown` 汇总表（主表 + 嵌套明细）
- 生成标准化明细 `json`（便于后续 Skill 消费）
- 输出统计摘要（总记录数、分类数、Top 问题）

### 5) 生成并执行测试
1. 执行 [generate-test-data.ps1](./scripts/generate-test-data.ps1) 生成测试样例 JSON/TXT。
2. 执行 [run-skill-tests.ps1](./scripts/run-skill-tests.ps1) 进行严格验证：
   - 字段映射是否正确
   - 默认维度分类是否生效
   - 多文件汇总是否完整
   - Markdown 报告结构是否包含必需章节
3. 自动生成测试报告到 `./reports/test-report.md`。

### 6) 发布与版本标记（正式版）
当测试全部通过后：
1. 更新版本号（建议语义化，如 `v1.0.0`）
2. 提交与推送变更
3. 创建并推送 tag（正式版本）

## 输出约定
- Markdown 报告：`<outputDir>/log-analysis-report.md`
- 标准化 JSON：`<outputDir>/normalized-records.json`
- 摘要 JSON：`<outputDir>/summary.json`
- 测试报告：`./reports/test-report.md`

## 失败分支
- 输入文件为空：返回清晰提示并要求补充路径
- 无法解析字段：提示补充字段映射文件
- 测试失败：输出失败项与定位建议，不进入发布步骤

## 参考资产
- 字段映射示例：[field-map.example.json](./assets/field-map.example.json)
- 维度规则示例：[dimension-rules.example.json](./assets/dimension-rules.example.json)
- 测试样例目录：`./tests/fixtures/`
