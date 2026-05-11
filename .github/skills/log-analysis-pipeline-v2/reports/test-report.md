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
| HTML report generated alongside Markdown | PASS | analyze() default emits log-analysis-report.html with sticky-header tables, TOC and PASS/FAIL/duration-bucket badges |
| generate_html=False suppresses HTML | PASS | analyze(generate_html=False) writes only Markdown; htmlPath is None and no .html file is produced |
| Legacy key_evdence typo compat | PASS | legacy spelling still mapped to keyEvidence; problem_subcategory recognized |
| Synonym column names | PASS | tableColumns accepts problem_category/执行结果/用例名称/key_evidence aliases |
| Auto-discover temp/report-layout.json | PASS | analyze() picks up temp/report-layout.json when no --report-layout is passed |
| Custom report layout | PASS | Validated configurable report columns via --report-layout |
| Locale en-US | PASS | Validated locale-specific headings: en-US |
| Locale zh-CN | PASS | Validated locale-specific headings: zh-CN |
| Analyze 10 | PASS | 10 records processed in 1.86 ms |
| Analyze 20 | PASS | 20 records processed in 2.24 ms |
| Analyze 200 | PASS | 200 records processed in 12.0 ms |
| Analyze 1000 | PASS | 1000 records processed in 96.86 ms |
| Analyze 5000 | PASS | 5000 records processed in 1586.44 ms |

## 性能

| 数据集 | 耗时（ms） | 记录总数 | 分组数量 |
|---|---:|---:|---:|
| 10 | 1.86 | 1 | 1 |
| 20 | 2.24 | 1 | 1 |
| 200 | 12.0 | 1 | 1 |
| 1000 | 96.86 | 1 | 1 |
| 5000 | 1586.44 | 1 | 1 |

## 结论

可以正式发布：提交、推送、打 tag。
