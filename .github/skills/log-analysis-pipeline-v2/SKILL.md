---
name: log-analysis-pipeline-v2
description: 日志分析汇总助手 v2（高性能版） - 当用户提供一个或多个 JSON/TXT 日志分析文件（可分散于不同路径，也可由其他 Skill 生成）时，自动解析、按规则聚类、生成 Markdown 表格报告（支持嵌套明细）。相对 v1 在 200/1000/2000/5000 条规模上经基准测试稳定快约 2 倍。当用户说"日志分析v2"、"高性能日志汇总"、"benchmark日志skill"、"v1 vs v2"时自动激活。
argument-hint: "[日志文件路径列表，可选规则文件路径，可选输出路径]"
user-invocable: true
---

# 日志分析汇总助手 v2（高性能版）

行为与 [log-analysis-pipeline](../log-analysis-pipeline/SKILL.md) 基本等价，并增强了结构化场景：
解析 JSON/TXT → 字段映射（支持字段名演进/别名）→ 按 `问题大类 / 问题小类 / 根因诊断结论`（可追加执行字段）聚类 →
渲染单表多行的 Markdown + 执行信息聚类表 → 输出 normalized JSON / summary JSON。

重点适配字段（优先）：
- 顶层：`case_name`、`problem_category`、`root_case_conclusion`、`fix_action`、`rerun_result`、`analysis_time`
- 嵌套：`version_info.{device_sn,device_type,platform_version,hy_version}`
- 嵌套：`case_execution_info.{case_name,begin_time,end_time,duration,result,error_message}`
- 嵌套数组：`key_evdence[]`（每项支持 `reference_doc` + `log_match`）

输入假设增强：
- 支持 JSON 和 TXT 成对输入（通常同名不同后缀），且每个文件仅 1 个用例。
- 当检测到成对同名 JSON/TXT 且都只含 1 条时，会自动合并为 1 条标准化记录（优先保留 JSON 的丰富字段）。
- 对字段名大小写、下划线/驼峰差异进行容错匹配，便于后续字段改名或新增。

## 与 v1 的差异（性能优化点）
1. **alias 扁平化查表**：将 `{canonical: [aliases…]}` 在加载期一次性翻成
   `{alias: canonical}` 字典，热路径不再嵌套循环（v1 每条记录都要遍历所有别名）。
2. **TXT 解析快路径**：用 `str.find` + `str.split` 处理 `:` / `：`，避免每行
   `re.match` 调用。
3. **单遍 normalize**：解析时直接产出最终 `dict[str,str]` 记录，去掉 v1 的
   二次 `to_hashable_record` + `get_field_value` 链路。
4. **分组增量聚合（`_Group.__slots__`）**：在分组的同一遍中就把摘要单元格用
   去重列表与计数构建出来，渲染阶段直接 `<br>.join`，去掉 v1 的两次列表遍历
   （`format_multi_line_cells` + `group_values`）。
5. **默认 groupBy 内联快路径**：当维度规则与默认一致时跳过 `tuple(...generator)`
   的开销。
6. **bytes-based JSON 解码**：`path.read_bytes()` + 手动剥 BOM，避免 `read_text`
   的 Python 层 decode。
7. **紧凑 JSON 输出**：normalized-records.json 使用
   `json.dumps(..., separators=(",", ":"))`，序列化更快、文件更小。

## 基准结果（5 次取均值，warmup 1 次）
最新一次测得（Windows / Python 3.13）：

| 规模 | v1 平均 | v2 平均 | 加速比 |
|---:|---:|---:|---:|
| 200 | 7.81 ms | 4.30 ms | 1.82x |
| 1000 | 38.02 ms | 16.45 ms | 2.31x |
| 2000 | 70.22 ms | 33.53 ms | 2.09x |
| 5000 | 178.26 ms | 85.60 ms | 2.08x |

完整数据见 [reports/benchmark.md](./reports/benchmark.md) /
[reports/benchmark.json](./reports/benchmark.json)。

## 工作流程
与 v1 一致，仅核心实现替换为 [scripts/log_analysis_core_v2.py](./scripts/log_analysis_core_v2.py)。

1. 收集输入与规则（同 v1）
2. 解析 JSON / TXT（v2 单遍 + 快路径）
3. 归一化与分组（v2 增量聚合）
4. 渲染 Markdown（单表 + `<br>` 多行单元格）
5. 生成测试 + 性能样例（10 / 20 / 200 / 1000 / 5000）
6. 与 v1 对比：执行 [scripts/benchmark.py](./scripts/benchmark.py)

可选参数增强：
- `--report-layout <path>`：指定报告布局配置（列顺序/列集合）。
- 当 `dimension-rules` 中 `groupBy` 包含未知字段时，会自动过滤；若过滤后为空，回退默认维度
   `issueCategory / issueSubcategory / rootCauseConclusion`。

## 结构化输入示例（单用例）

```json
{
   "case_name": "Login-Timeout-001",
   "problem_category": "Network",
   "root_case_conclusion": "Upstream gateway timeout",
   "key_evdence": [
      {"reference_doc": "gw-logs-20260509.txt", "log_match": "504 Gateway Timeout"}
   ],
   "fix_action": "Increase upstream timeout to 15s",
   "rerun_result": "PASS",
   "analysis_time": "2026-05-09 10:01:02",
   "version_info": {
      "device_sn": "SN-001",
      "device_type": "edge-gateway",
      "platform_version": "4.0.1",
      "hy_version": "2.3.0"
   },
   "case_execution_info": {
      "case_name": "Login-Timeout-001",
      "begin_time": "2026-05-09 10:00:00",
      "end_time": "2026-05-09 10:00:12",
      "duration": "12s",
      "result": "FAIL",
      "error_message": "HTTP 504"
   }
}
```

## 平台优先级 & 兜底
- Windows：`scripts/run-skill-tests.ps1` → Python
- Linux/macOS：`scripts/run-skill.sh` → python3 → python → node
- 通用 Node 兜底：`scripts/run-skill.mjs`
- Python 直跑：`scripts/run-skill-tests.py`、`scripts/analyze-logs.py`

## 多语言
与 v1 共用 locale schema：`./assets/locales/zh-CN.json`、`./assets/locales/en-US.json`，
也可用 `--locale-file` 指向任意外部语言包。

## 输出约定
- Markdown 报告：`<outputDir>/log-analysis-report.md`
- 标准化 JSON：`<outputDir>/normalized-records.json`（紧凑格式）
- 摘要 JSON：`<outputDir>/summary.json`
- 测试报告：`./reports/test-report.md`、`./reports/test-report.<locale>.md`
- 基准报告：`./reports/benchmark.md`、`./reports/benchmark.json`

## 失败分支
与 v1 一致；额外：basenchmark 找不到 v1 目录会显式报错。

## 版本说明
- `v2.0.0`：性能优化 + 与 v1 等价的功能与产物 + 5000 级 fixture 与 v1 对比基准
