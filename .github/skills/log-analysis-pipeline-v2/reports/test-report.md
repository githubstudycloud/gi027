# 日志分析技能测试报告

- 语言: zh-CN
- 结果: PASS

## Test Details

| Case | Result | Detail |
|---|---|---|
| Generate fixtures | PASS | Generated 10 fixture files |
| Structured pair merge | PASS | paired json/txt merged to 1 record(s); execution groups=1; subcategory captured |
| Legacy key_evdence typo compat | PASS | legacy spelling still mapped to keyEvidence; problem_subcategory recognized |
| Synonym column names | PASS | tableColumns accepts problem_category/执行结果/用例名称/key_evidence aliases |
| Custom report layout | PASS | Validated configurable report columns via --report-layout |
| Locale zh-CN | PASS | Validated locale-specific headings: zh-CN |
| Locale en-US | PASS | Validated locale-specific headings: en-US |
| Analyze 10 | PASS | 10 records processed in 2.54 ms |
| Analyze 20 | PASS | 20 records processed in 2.09 ms |
| Analyze 200 | PASS | 200 records processed in 9.13 ms |
| Analyze 1000 | PASS | 1000 records processed in 29.3 ms |
| Analyze 5000 | PASS | 5000 records processed in 132.25 ms |

## 性能

| 数据集 | 耗时（ms） | 记录总数 | 分组数量 |
|---|---:|---:|---:|
| 10 | 2.54 | 10 | 10 |
| 20 | 2.09 | 20 | 20 |
| 200 | 9.13 | 200 | 140 |
| 1000 | 29.3 | 1000 | 140 |
| 5000 | 132.25 | 5000 | 140 |

## 结论

可以正式发布：提交、推送、打 tag。
