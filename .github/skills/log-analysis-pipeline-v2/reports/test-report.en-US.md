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
| Custom report layout | PASS | Validated configurable report columns via --report-layout |
| Locale en-US | PASS | Validated locale-specific headings: en-US |
| Locale zh-CN | PASS | Validated locale-specific headings: zh-CN |
| Analyze 10 | PASS | 10 records processed in 1.86 ms |
| Analyze 20 | PASS | 20 records processed in 2.74 ms |
| Analyze 200 | PASS | 200 records processed in 9.0 ms |
| Analyze 1000 | PASS | 1000 records processed in 27.61 ms |
| Analyze 5000 | PASS | 5000 records processed in 137.73 ms |

## Performance

| Dataset | Elapsed (ms) | Total records | Total groups |
|---|---:|---:|---:|
| 10 | 1.86 | 10 | 10 |
| 20 | 2.74 | 20 | 20 |
| 200 | 9.0 | 200 | 140 |
| 1000 | 27.61 | 1000 | 140 |
| 5000 | 137.73 | 5000 | 140 |

## Conclusion

Ready for release: commit, push, tag.
