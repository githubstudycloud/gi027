# 日志分析汇总报告

- 语言: zh-CN
- 运行时: python

## 总览

| 指标 | 值 |
|---|---|
| 输入文件数 | 2 |
| 记录总数 | 20 |
| 分组数量 | 10 |
| 类别数量 | 10 |

## 分类汇总

| 问题大类 | 问题小类 | 根因诊断结论 | 数量 | 用例名称 | 关键佐证信息 | 问题修复动作 | 问题修复结论 | 用例重跑结论 | 来源文件 |
|---|---|---|---:|---|---|---|---|---|---|
| Consistency | Mapping | Root cause 0 | 2 | 1. Case-10-8<br>2. Case-10-8 | 1. Evidence 8<br>2. Evidence 8 | Action 2 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.json<br>D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.txt |
| Consistency | Network | Root cause 3 | 2 | 1. Case-10-4<br>2. Case-10-4 | 1. Evidence 4<br>2. Evidence 4 | Action 3 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.json<br>D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.txt |
| Correctness | Load | Root cause 2 | 2 | 1. Case-10-10<br>2. Case-10-10 | 1. Evidence 10<br>2. Evidence 10 | Action 4 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.json<br>D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.txt |
| Correctness | Signature | Root cause 1 | 2 | 1. Case-10-2<br>2. Case-10-2 | 1. Evidence 2<br>2. Evidence 2 | Action 1 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.json<br>D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.txt |
| Correctness | Timeout | Root cause 5 | 2 | 1. Case-10-6<br>2. Case-10-6 | 1. Evidence 6<br>2. Evidence 6 | Action 0 | Mitigated | Passed | D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.json<br>D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.txt |
| Performance | Mapping | Root cause 2 | 2 | 1. Case-10-3<br>2. Case-10-3 | 1. Evidence 3<br>2. Evidence 3 | Action 2 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.json<br>D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.txt |
| Performance | Signature | Root cause 6 | 2 | 1. Case-10-7<br>2. Case-10-7 | 1. Evidence 7<br>2. Evidence 7 | Action 1 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.json<br>D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.txt |
| Stability | Load | Root cause 4 | 2 | 1. Case-10-5<br>2. Case-10-5 | 1. Evidence 5<br>2. Evidence 5 | Action 4 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.json<br>D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.txt |
| Stability | Network | Root cause 1 | 2 | 1. Case-10-9<br>2. Case-10-9 | 1. Evidence 9<br>2. Evidence 9 | Action 3 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.json<br>D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.txt |
| Stability | Timeout | Root cause 0 | 2 | 1. Case-10-1<br>2. Case-10-1 | 1. Evidence 1<br>2. Evidence 1 | Action 0 | Fixed | Passed | D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.json<br>D:\20260422\.github\skills\log-analysis-pipeline\tests\fixtures\sample-10.txt |

## 用例矩阵

- 数量: 10
- 记录总数: 20
