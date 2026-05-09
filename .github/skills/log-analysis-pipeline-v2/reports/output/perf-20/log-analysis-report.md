# 日志分析汇总报告

- 语言: zh-CN
- 运行时: python

## 总览

| 指标 | 值 |
|---|---|
| 输入文件数 | 2 |
| 记录总数 | 40 |
| 分组数量 | 20 |
| 类别数量 | 20 |

## 分类汇总

| 问题大类 | 问题小类 | 根因诊断结论 | 数量 | 用例名称 | 关键佐证信息 | 问题修复动作 | 问题修复结论 | 用例重跑结论 | 来源文件 |
|---|---|---|---:|---|---|---|---|---|---|
| Consistency | Load | Root cause 5 | 2 | 1. Case-20-20<br>2. Case-20-20 | 1. Evidence 20<br>2. Evidence 20 | Action 4 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Consistency | Mapping | Root cause 0 | 2 | 1. Case-20-8<br>2. Case-20-8 | 1. Evidence 8<br>2. Evidence 8 | Action 2 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Consistency | Network | Root cause 3 | 2 | 1. Case-20-4<br>2. Case-20-4 | 1. Evidence 4<br>2. Evidence 4 | Action 3 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Consistency | Signature | Root cause 4 | 2 | 1. Case-20-12<br>2. Case-20-12 | 1. Evidence 12<br>2. Evidence 12 | Action 1 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Consistency | Timeout | Root cause 1 | 2 | 1. Case-20-16<br>2. Case-20-16 | 1. Evidence 16<br>2. Evidence 16 | Action 0 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Correctness | Load | Root cause 2 | 2 | 1. Case-20-10<br>2. Case-20-10 | 1. Evidence 10<br>2. Evidence 10 | Action 4 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Correctness | Mapping | Root cause 3 | 2 | 1. Case-20-18<br>2. Case-20-18 | 1. Evidence 18<br>2. Evidence 18 | Action 2 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Correctness | Network | Root cause 6 | 2 | 1. Case-20-14<br>2. Case-20-14 | 1. Evidence 14<br>2. Evidence 14 | Action 3 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Correctness | Signature | Root cause 1 | 2 | 1. Case-20-2<br>2. Case-20-2 | 1. Evidence 2<br>2. Evidence 2 | Action 1 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Correctness | Timeout | Root cause 5 | 2 | 1. Case-20-6<br>2. Case-20-6 | 1. Evidence 6<br>2. Evidence 6 | Action 0 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Performance | Load | Root cause 0 | 2 | 1. Case-20-15<br>2. Case-20-15 | 1. Evidence 15<br>2. Evidence 15 | Action 4 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Performance | Mapping | Root cause 2 | 2 | 1. Case-20-3<br>2. Case-20-3 | 1. Evidence 3<br>2. Evidence 3 | Action 2 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Performance | Network | Root cause 4 | 2 | 1. Case-20-19<br>2. Case-20-19 | 1. Evidence 19<br>2. Evidence 19 | Action 3 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Performance | Signature | Root cause 6 | 2 | 1. Case-20-7<br>2. Case-20-7 | 1. Evidence 7<br>2. Evidence 7 | Action 1 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Performance | Timeout | Root cause 3 | 2 | 1. Case-20-11<br>2. Case-20-11 | 1. Evidence 11<br>2. Evidence 11 | Action 0 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Stability | Load | Root cause 4 | 2 | 1. Case-20-5<br>2. Case-20-5 | 1. Evidence 5<br>2. Evidence 5 | Action 4 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Stability | Mapping | Root cause 5 | 2 | 1. Case-20-13<br>2. Case-20-13 | 1. Evidence 13<br>2. Evidence 13 | Action 2 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Stability | Network | Root cause 1 | 2 | 1. Case-20-9<br>2. Case-20-9 | 1. Evidence 9<br>2. Evidence 9 | Action 3 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Stability | Signature | Root cause 2 | 2 | 1. Case-20-17<br>2. Case-20-17 | 1. Evidence 17<br>2. Evidence 17 | Action 1 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |
| Stability | Timeout | Root cause 0 | 2 | 1. Case-20-1<br>2. Case-20-1 | 1. Evidence 1<br>2. Evidence 1 | Action 0 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.json<br>D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\sample-20.txt |

## 用例矩阵

- 数量: 20
- 记录总数: 40
