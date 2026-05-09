# 日志分析技能测试报告

- 语言: zh-CN
- 结果: PASS

## Test Details

| Case | Result | Detail |
|---|---|---|
| Generate fixtures | PASS | Generated 10 fixture files |
| Structured pair merge | PASS | paired json/txt merged to 1 record(s); execution groups=1 |
| Custom report layout | PASS | Validated configurable report columns via --report-layout |
| Locale en-US | PASS | Validated locale-specific headings: en-US |
| Locale zh-CN | PASS | Validated locale-specific headings: zh-CN |
| Analyze 10 | PASS | 10 records processed in 1.43 ms |
| Analyze 20 | PASS | 20 records processed in 1.8 ms |
| Analyze 200 | PASS | 200 records processed in 7.22 ms |
| Analyze 1000 | PASS | 1000 records processed in 24.77 ms |
| Analyze 5000 | PASS | 5000 records processed in 128.66 ms |

## 性能

| 数据集 | 耗时（ms） | 记录总数 | 分组数量 |
|---|---:|---:|---:|
| 10 | 1.43 | 10 | 10 |
| 20 | 1.8 | 20 | 20 |
| 200 | 7.22 | 200 | 140 |
| 1000 | 24.77 | 1000 | 140 |
| 5000 | 128.66 | 5000 | 140 |

## 结论

可以正式发布：提交、推送、打 tag。
