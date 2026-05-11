# Log Analysis Skill Test Report

- Language: en-US
- Result: PASS

## Test Details

| Case | Result | Detail |
|---|---|---|
| Generate fixtures | PASS | Generated 10 fixture files |
| Structured pair merge | PASS | json wins when paired with txt; records=1; execution groups=1; subcategory captured |
| Numbered TXT format (用例失败根因分析结果) | PASS | TXT-only numbered-section input produces a complete row, no N/A on category/subcategory/rootCause/evidence/fix/rerun |
| Numbered TXT loose format (multi-line sections, colons in body) | PASS | headers each on their own line; sections span many lines/blank lines; colons in body and 本次日志对应信息 multi-line value all preserved correctly without garbage keys |
| Legacy key_evdence typo compat | PASS | legacy spelling still mapped to keyEvidence; problem_subcategory recognized |
| Synonym column names | PASS | tableColumns accepts problem_category/执行结果/用例名称/key_evidence aliases |
| Auto-discover temp/report-layout.json | PASS | analyze() picks up temp/report-layout.json when no --report-layout is passed |
| Custom report layout | PASS | Validated configurable report columns via --report-layout |
| Locale zh-CN | PASS | Validated locale-specific headings: zh-CN |
| Locale en-US | PASS | Validated locale-specific headings: en-US |
| Analyze 10 | PASS | 10 records processed in 1.57 ms |
| Analyze 20 | PASS | 20 records processed in 1.98 ms |
| Analyze 200 | PASS | 200 records processed in 10.94 ms |
| Analyze 1000 | PASS | 1000 records processed in 93.77 ms |
| Analyze 5000 | PASS | 5000 records processed in 1542.11 ms |

## Performance

| Dataset | Elapsed (ms) | Total records | Total groups |
|---|---:|---:|---:|
| 10 | 1.57 | 1 | 1 |
| 20 | 1.98 | 1 | 1 |
| 200 | 10.94 | 1 | 1 |
| 1000 | 93.77 | 1 | 1 |
| 5000 | 1542.11 | 1 | 1 |

## Conclusion

Ready for release: commit, push, tag.
