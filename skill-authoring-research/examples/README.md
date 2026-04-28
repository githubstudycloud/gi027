# 示例 Skill 集合

本目录包含三个完整可学习的 Skill 示例，分别对应三种最常见类型。

## 目录

| 示例 | 类型 | 学习重点 |
|------|------|---------|
| [example-workflow/](./example-workflow/) | 工作流型 | 多步骤、决策点、模板内嵌 |
| [example-tool/](./example-tool/) | 工具型 | 外部命令、配置、安全约束 |
| [example-writing/](./example-writing/) | 写作型 | 结构化产物、规范模板 |

## 如何使用这些示例

### 方式 1：直接安装到本机测试

```powershell
# 复制到用户级 Skill 目录
Copy-Item -Recurse .\example-workflow C:\Users\John\.claude\skills\

# 重启 VS Code Chat，输入 / 应能看到 example-workflow
```

### 方式 2：作为模板改造

```powershell
# 复制后改名
Copy-Item -Recurse .\example-workflow C:\Users\John\.claude\skills\my-real-skill

# 修改 SKILL.md 的 frontmatter：
#   name: my-real-skill   ← 必须与新文件夹名一致
#   description: ...      ← 改成你的描述
```

## 验证示例正确性

将示例复制到 `~/.claude/skills/` 后：

1. 打开 VS Code，重启 Chat
2. 在输入框输入 `/`
3. 应在斜杠命令列表中看到 `example-workflow`、`example-tool`、`example-writing`
4. 输入触发关键词（如"写commit"），应自动加载对应 Skill

如果**看不到**：检查 `name` 与文件夹名是否一致、frontmatter 是否合法 YAML。
