# Log Analysis Skill Test Report

- Language: en-US
- Result: PASS

## Test Details

| Case | Result | Detail |
|---|---|---|
| Generate fixtures | PASS | Generated 10 fixture files |
| Structured pair merge | PASS | paired json/txt merged to 1 record(s); execution groups=1; subcategory captured |
| Legacy key_evdence typo compat | PASS | legacy spelling still mapped to keyEvidence; problem_subcategory recognized |
| Synonym column names | PASS | tableColumns accepts problem_category/执行结果/用例名称/key_evidence aliases |
| Auto-discover temp/report-layout.json | PASS | analyze() picks up temp/report-layout.json when no --report-layout is passed |
| Custom report layout | PASS | Validated configurable report columns via --report-layout |
| Locale zh-CN | PASS | Validated locale-specific headings: zh-CN |
| Locale en-US | PASS | Validated locale-specific headings: en-US |
| Analyze 10 | PASS | 10 records processed in 1.89 ms |
| Analyze 20 | PASS | 20 records processed in 2.19 ms |
| Analyze 200 | PASS | 200 records processed in 16.78 ms |
| Analyze 1000 | PASS | 1000 records processed in 207.71 ms |
| Analyze 5000 | PASS | 5000 records processed in 4245.21 ms |

## Performance

| Dataset | Elapsed (ms) | Total records | Total groups |
|---|---:|---:|---:|
| 10 | 1.89 | 1 | 1 |
| 20 | 2.19 | 1 | 1 |
| 200 | 16.78 | 1 | 1 |
| 1000 | 207.71 | 1 | 1 |
| 5000 | 4245.21 | 1 | 1 |

## Conclusion

Ready for release: commit, push, tag.
