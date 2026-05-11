# 日志分析技能测试报告

- 语言: zh-CN
- 结果: PASS

## Test Details

| Case | Result | Detail |
|---|---|---|
| Generate fixtures | PASS | Generated 10 fixture files |
| Structured pair merge | PASS | json wins when paired with txt; records=1; execution groups=1; subcategory captured |
| Numbered TXT format (用例失败根因分析结果) | PASS | TXT-only numbered-section input produces a complete row, no N/A on category/subcategory/rootCause/evidence/fix/rerun |
| Numbered TXT loose format (multi-line sections, colons in body) | PASS | headers each on their own line; sections span many lines/blank lines; colons in body and 本次日志对应信息 multi-line value all preserved correctly without garbage keys |
| Timestamped output subdirectory | PASS | analyze(timestamped_output=True) writes into <output-dir>/YYYYMMDD-HHMMSS/ so successive runs don't overwrite |
| Legacy key_evdence typo compat | PASS | legacy spelling still mapped to keyEvidence; problem_subcategory recognized |
| Synonym column names | PASS | tableColumns accepts problem_category/执行结果/用例名称/key_evidence aliases |
| Auto-discover temp/report-layout.json | PASS | analyze() picks up temp/report-layout.json when no --report-layout is passed |
| Custom report layout | PASS | Validated configurable report columns via --report-layout |
| Locale zh-CN | PASS | Validated locale-specific headings: zh-CN |
| Locale en-US | PASS | Validated locale-specific headings: en-US |
| Analyze 10 | PASS | 10 records processed in 1.55 ms |
| Analyze 20 | PASS | 20 records processed in 1.95 ms |
| Analyze 200 | PASS | 200 records processed in 11.84 ms |
| Analyze 1000 | PASS | 1000 records processed in 97.11 ms |
| Analyze 5000 | PASS | 5000 records processed in 1557.43 ms |

## 性能

| 数据集 | 耗时（ms） | 记录总数 | 分组数量 |
|---|---:|---:|---:|
| 10 | 1.55 | 1 | 1 |
| 20 | 1.95 | 1 | 1 |
| 200 | 11.84 | 1 | 1 |
| 1000 | 97.11 | 1 | 1 |
| 5000 | 1557.43 | 1 | 1 |

## 结论

可以正式发布：提交、推送、打 tag。
