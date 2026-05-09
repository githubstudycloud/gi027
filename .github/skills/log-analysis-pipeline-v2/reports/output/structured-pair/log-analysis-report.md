# 日志分析汇总报告

- 语言: zh-CN
- 运行时: python

## 总览

| 指标 | 值 |
|---|---|
| 输入文件数 | 2 |
| 记录总数 | 1 |
| 分组数量 | 1 |
| 类别数量 | 1 |

## 分类汇总

| 问题大类 | 问题小类 | 根因诊断结论 | 数量 | 用例名称 | 关键佐证信息 | 问题修复动作 | 问题修复结论 | 用例重跑结论 | 来源文件 |
|---|---|---|---:|---|---|---|---|---|---|
| Network | Timeout | Upstream timeout | 1 | 1. Auth-Timeout-001 | 1. 1) reference_doc=gw.log; log_match=504 Gateway Timeout | Increase timeout to 15s | N/A | PASS | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\structured-single-case.json | D:\20260422\.github\skills\log-analysis-pipeline-v2\tests\fixtures\structured-single-case.txt |

## 执行信息聚类

| 执行结果 | 错误信息 | 耗时分桶 | 数量 | 用例名称 |
|---|---|---|---:|---|
| FAIL | HTTP 504 | 5-30s | 1 | 1. Auth-Timeout-001 |

## 用例矩阵

- 数量: 1
- 记录总数: 1
