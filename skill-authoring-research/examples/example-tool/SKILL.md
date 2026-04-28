---
name: example-tool
description: 示例工具 Skill - 演示日志搜索助手的标准编写形态。当用户说"搜索日志"、"查日志"、"log search"时自动激活。
argument-hint: "[关键词] [时间范围]"
---

# 日志搜索助手（示例）

> 这是研究目录中的 **工具型 Skill 示例**，展示连接外部系统的写法。

## 支持的操作
| 操作 | 说明 |
|------|------|
| search | 关键词搜索 |
| tail | 实时跟踪 |
| stats | 错误统计 |

## 配置
默认从环境变量读取：
- `LOG_DIR`：日志根目录（默认 `/var/log/app`）
- `LOG_RETENTION_DAYS`：保留天数（默认 7）

## 工作流程

### 第一步：解析参数
- 关键词：必填
- 时间范围：可选，默认最近 1 小时
- 文件过滤：可选，默认 `*.log`

### 第二步：选择执行方式
| 场景 | 命令 |
|------|------|
| 关键词搜索 | `grep -rn <keyword> $LOG_DIR --include='*.log'` |
| 时间过滤 | `find $LOG_DIR -mmin -60 -name '*.log' \| xargs grep <keyword>` |
| 错误统计 | `grep -c ERROR $LOG_DIR/*.log` |

### 第三步：格式化输出
按 [输出模板](./references/output-format.md) 整理结果。

## 安全约束
- 禁止 `rm`、`>` 重定向等修改操作
- 单次返回不超过 100 行匹配结果
- 路径必须在 `$LOG_DIR` 范围内
