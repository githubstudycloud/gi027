# Conventional Commits 模板

```
<type>(<scope>): <subject>

<body>

<footer>
```

## 字段规则

- **type**: feat | fix | docs | style | refactor | test | chore | perf | ci | build
- **scope**: 模块名（小写），可省略
- **subject**: 50 字以内，祈使句，不加句号
- **body**: 详细说明，每行 72 字内（可选）
- **footer**: BREAKING CHANGE / Refs / Closes（可选）

## 示例

```
feat(auth): 新增 OAuth2 登录

- 集成 Google/GitHub
- 添加 token 刷新

Closes: #123
```

```
fix(api): 修复用户列表分页越界

当 page 超过总页数时返回 400 而非 500。

Refs: #456
```
