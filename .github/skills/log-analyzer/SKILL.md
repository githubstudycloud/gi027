---
name: log-analyzer
description: 日志分析汇总助手（可分发骨架版） - 当用户提供一个或多个 JSON/TXT 日志分析文件时，自动解析嵌套字段（含 case_execution_info / version_info / key_evidence 等）、按问题大类/小类/根因聚类，输出 Markdown 报告 + normalized JSON + summary JSON。列与字段名都支持同义/多语言别名。当用户说"日志分析"、"日志汇总"、"问题归类生成表格"时自动激活。
argument-hint: "[日志文件路径列表，可选规则文件路径，可选输出路径]"
user-invocable: true
---

# log-analyzer — 日志分析汇总助手（骨架版）

> ⚠️ **不要修改本目录的目录结构与脚本相对路径**。脚本通过 `Path(__file__).resolve().parent.parent` 解析 `assets/`、`tests/`、`reports/`。改动目录会导致默认资源/输出路径失效。

## 它能做什么
- 解析 **JSON**（含深度嵌套，如 `version_info.*`、`case_execution_info.*`、`key_evidence[]`）。
- 解析 **TXT**（`key: value` 块，空行分组）。
- 对 **同名 JSON + TXT** 单用例文件自动合并为一条标准化记录。
- 按 `问题大类 / 问题小类 / 根因诊断结论` 聚类，并补一张「用例执行聚类表」。
- 输出 Markdown 报告 + 紧凑 normalized JSON + summary JSON。

## 支持的字段（核心）
顶层：`case_name`、`problem_category`、`problem_subcategory`、`root_case_conclusion`、`fix_action`、`fix_conclusion`、`rerun_result`、`analysis_time`
嵌套：`version_info.{device_sn,device_type,platform_version,hy_version}`
嵌套：`case_execution_info.{case_name,begin_time,end_time,duration,result,error_message}`
数组：`key_evidence[]`（每项 `reference_doc` + `log_match`，**兼容旧拼写 `key_evdence`**）

字段映射支持别名扩展：见 [assets/field-map.example.json](./assets/field-map.example.json)。

## 30 秒上手
```powershell
# 自检 + 生成样例 + 跑性能 + 写测试报告（一体化）
python .github/skills/log-analyzer/scripts/log_analysis_core.py test --skill-root .github/skills/log-analyzer --locale en-US

# 分析自己的日志
python .github/skills/log-analyzer/scripts/log_analysis_core.py analyze `
  --input-files path\to\case-1.json path\to\case-1.txt `
  --output-dir .github/skills/log-analyzer/reports/output `
  --locale zh-CN
```

## 配置化报告列（同义兼容）
`--report-layout <path>` 指定布局，`tableColumns` 元素可写任意同义名：

```json
{
  "tableColumns": ["problem_category", "问题小类", "根因诊断结论", "count", "用例名称", "key_evidence", "执行结果", "错误信息"]
}
```

底层会自动归一到内部列键（`category` / `subcategory` / `rootCause` / `count` / `cases` / `evidence` / `caseResult` / `caseErrorMessage` …）。

## 目录结构（请勿改名）
```
log-analyzer/
├─ SKILL.md
├─ README.md
├─ scripts/
│  └─ log_analysis_core.py     # 单文件核心，CLI: analyze | generate | test
├─ assets/
│  ├─ field-map.example.json
│  ├─ dimension-rules.example.json
│  ├─ report-layout.example.json
│  └─ locales/{en-US,zh-CN}.json
├─ tests/fixtures/             # test 子命令自动生成
└─ reports/                    # test/analyze 输出
```

## 想看更多
- 完整测试 + 性能基准 + v1 对比 → [../log-analysis-pipeline-v2/SKILL.md](../log-analysis-pipeline-v2/SKILL.md)
- 这里只保留最小骨架，方便升级时整目录覆盖。
