---
name: example-writing
description: 示例写作 Skill - 演示 Changelog 撰写助手的标准编写形态。当用户说"写changelog"、"生成更新日志"、"release notes"时自动激活。
argument-hint: "[版本号]"
---

# Changelog 撰写助手（示例）

> 这是研究目录中的 **写作型 Skill 示例**，展示遵循特定格式产出文档的写法。

## 何时使用
- 准备发版需要整理 Changelog
- 基于 git log 生成结构化更新说明

## 参数说明
- `$ARGUMENTS`：版本号，例如 `1.2.0`

## 写作流程

### 第一步：确定上下文
```bash
# 找上一个 tag
git describe --tags --abbrev=0

# 收集自上一个 tag 以来的提交
git log <last-tag>..HEAD --pretty=format:"%h %s"
```

### 第二步：分类提交
按 [Keep a Changelog](https://keepachangelog.com/) 规范：

| 分类 | 来源 commit type |
|------|----------------|
| Added | feat |
| Changed | refactor, perf |
| Fixed | fix |
| Deprecated | （手动标记） |
| Removed | （手动标记） |
| Security | （手动标记） |

### 第三步：生成 Changelog
使用 [模板](./assets/changelog-template.md) 渲染。

### 第四步：附加到 CHANGELOG.md
插入到 `## [Unreleased]` 之后、上一版本之前。

## 写作要求
- 每条目以动词开头（"新增"、"修复"、"优化"）
- 同一条目控制在 1 行内
- 标注关联 PR/Issue 编号
- BREAKING CHANGE 必须单独成段并加 ⚠️ 标记
