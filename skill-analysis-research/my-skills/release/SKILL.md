---
name: release
description: 发布管理助手 - 自动化版本发布流程：版本号、CHANGELOG、Tag、发布说明。当用户说"发布版本"、"release"、"打tag"、"准备发版"时自动激活。
argument-hint: "[版本号 如 2.1.0，或 patch/minor/major]"
allowed-tools: Read, Write, Edit, Bash
---

# 发布管理助手

遵循语义化版本（SemVer），自动化完成从 develop 到生产的发布流程。

## 参数
- `$ARGUMENTS`：目标版本号（`2.1.0`）或自动递增（`patch` / `minor` / `major`）

## 工作流程

### 阶段 1：发布前检查

```bash
# 当前分支和状态
git branch --show-current
git status
git log --oneline main..develop | head -20

# 当前版本
cat package.json | grep '"version"' 2>/dev/null || \
cat pom.xml | grep '<version>' 2>/dev/null | head -1 || \
cat pyproject.toml | grep 'version' | head -1
```

**发布前门控检查：**
```
✅ 所有 CI 检查通过（测试/lint/安全扫描）
✅ staging 环境验证通过
✅ 没有未解决的 Critical Bug
✅ 数据库迁移已测试回滚
✅ 破坏性变更已记录在 BREAKING CHANGES
```

如有检查未通过，**停止发布并报告原因**。

### 阶段 2：计算版本号

```bash
# 读取最近的 commits（从上次 tag 到现在）
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

根据 Conventional Commits 自动推断版本号：
```
feat!: 或 BREAKING CHANGE: → MAJOR 版本 +1
feat: → MINOR 版本 +1
fix: / perf: → PATCH 版本 +1
docs: / chore: → PATCH（仅补丁，不影响用户）
```

如果 `$ARGUMENTS` 指定了版本号，直接使用；否则自动计算并展示给用户确认。

### 阶段 3：生成 CHANGELOG

解析 `git log` 中的 Conventional Commits，生成变更日志：

```bash
git log $(git describe --tags --abbrev=0)..HEAD --format="%s|%h|%an" | grep -E "^(feat|fix|perf|refactor|BREAKING)"
```

在 `CHANGELOG.md` 中插入新版本条目（在 `## [Unreleased]` 后面）：

```markdown
## [{新版本}] - {今天日期}

### ⚠️ Breaking Changes
- {feat!: 或 BREAKING CHANGE commits}

### ✨ 新功能
- {feat: commits，格式：描述 (#PR号)}

### 🐛 Bug 修复
- {fix: commits}

### ⚡ 性能优化
- {perf: commits}

### 📝 文档
- {docs: commits}

### 🔧 其他
- {chore: / ci: commits（仅重要的）}
```

### 阶段 4：更新版本文件

**根据技术栈更新版本号：**

```bash
# Node.js 项目
npm version {版本号} --no-git-tag-version

# Java Maven
mvn versions:set -DnewVersion={版本号}

# Java Gradle（手动更新 build.gradle）
# Python
sed -i 's/version = ".*"/version = "{版本号}"/' pyproject.toml
```

### 阶段 5：创建发布 PR

```bash
# 创建 release 分支
git checkout -b release/{版本号} develop
git add CHANGELOG.md {版本文件}
git commit -m "chore(release): prepare v{版本号}"
```

**输出 PR 描述模板：**

```markdown
## Release v{版本号}

### 变更摘要
{从 CHANGELOG 提取的关键变更}

### 发布检查清单
- [ ] CHANGELOG.md 已更新
- [ ] 版本号已更新
- [ ] staging 环境测试通过
- [ ] 数据库迁移已验证
- [ ] 所有 CI 检查通过
- [ ] 已通知相关团队

### 部署步骤
1. 合并此 PR 到 main
2. 打 Tag：`git tag v{版本号}`
3. 触发生产部署流水线
4. 验证生产环境健康检查
5. 合并 release 分支回 develop

### 回滚方案
{如果部署失败的回滚步骤}
```

### 阶段 6：发布后操作（合并后执行）

```bash
# 打 tag
git tag -a v{版本号} -m "Release v{版本号}"
git push origin v{版本号}

# 合并回 develop（包含版本号更新）
git checkout develop
git merge --no-ff release/{版本号}
git push origin develop

# 删除 release 分支
git branch -d release/{版本号}
```

**输出最终发布报告：**
```
✅ v{版本号} 发布完成
   Tag: v{版本号}
   变更：+{N}个功能 / {N}个修复
   CHANGELOG: 已更新
   下一版本：v{预计下个版本}
```
