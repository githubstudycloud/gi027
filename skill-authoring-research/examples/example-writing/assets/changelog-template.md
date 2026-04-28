# Changelog 模板

```markdown
## [{版本号}] - {YYYY-MM-DD}

### Added
- 新增 xxx 功能 (#PR编号)
- ...

### Changed
- 优化 xxx 流程 (#PR编号)
- ...

### Fixed
- 修复 xxx 问题 (#Issue编号)
- ...

### ⚠️ Breaking Changes
- 移除 `oldApi()`，请改用 `newApi()`，迁移指南见 [docs/migration.md](docs/migration.md)
```

## 完整示例

```markdown
## [1.2.0] - 2026-04-28

### Added
- 新增 OAuth2 登录支持 (#123)
- 新增暗黑模式 (#145)

### Changed
- 优化首页加载性能 30% (#156)

### Fixed
- 修复分页越界 500 错误 (#160)
- 修复 Safari 下日期选择器异常 (#162)
```
