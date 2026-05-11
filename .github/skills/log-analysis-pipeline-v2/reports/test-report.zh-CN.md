# 日志分析技能测试报告

- 语言: zh-CN
- 结果: PASS

## Test Details

| Case | Result | Detail |
|---|---|---|
| Generate fixtures | PASS | Generated 10 fixture files |
| Structured pair merge | PASS | json wins when paired with txt; records=1; execution groups=1; subcategory captured |
| Numbered TXT format (用例失败根因分析结果) | PASS | TXT-only numbered-section input produces a complete row, no N/A on category/subcategory/rootCause/evidence/fix/rerun |
| Legacy key_evdence typo compat | PASS | legacy spelling still mapped to keyEvidence; problem_subcategory recognized |
| Synonym column names | PASS | tableColumns accepts problem_category/执行结果/用例名称/key_evidence aliases |
| Auto-discover temp/report-layout.json | PASS | analyze() picks up temp/report-layout.json when no --report-layout is passed |
| Custom report layout | PASS | Validated configurable report columns via --report-layout |
| Locale en-US | PASS | Validated locale-specific headings: en-US |
| Locale zh-CN | PASS | Validated locale-specific headings: zh-CN |
| Analyze 10 | PASS | 10 records processed in 1.73 ms |
| Analyze 20 | PASS | 20 records processed in 2.74 ms |
| Analyze 200 | PASS | 200 records processed in 10.56 ms |
| Analyze 1000 | PASS | 1000 records processed in 90.91 ms |
| Analyze 5000 | PASS | 5000 records processed in 1461.64 ms |

## 性能

| 数据集 | 耗时（ms） | 记录总数 | 分组数量 |
|---|---:|---:|---:|
| 10 | 1.73 | 1 | 1 |
| 20 | 2.74 | 1 | 1 |
| 200 | 10.56 | 1 | 1 |
| 1000 | 90.91 | 1 | 1 |
| 5000 | 1461.64 | 1 | 1 |

## 结论

可以正式发布：提交、推送、打 tag。
