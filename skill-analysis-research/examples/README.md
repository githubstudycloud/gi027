# 配套示例

本目录提供前 7 章涉及的可运行示例：

| 文件 | 说明 |
|------|------|
| `bug-fix-original.md` | 模拟从网上抓到的原 Claude 格式 Skill |
| `bug-fix-copilot.md` | 适配为 VS Code Copilot 格式后 |
| `bug-fix-optimized.md` | 进一步优化到 94 分版本 |
| `score-skill.ps1` | 自动打分脚本（PowerShell） |
| `convert-skill.ps1` | 跨工具格式转换脚本 |
| `half-baked-skill.md` | "半成品 Skill"反例，用于教学诊断 |

## 使用方法

### 给一个 Skill 打分

```powershell
PS> .\score-skill.ps1 -Path .\bug-fix-original.md
```

### 转换格式

```powershell
PS> .\convert-skill.ps1 -Source .\bug-fix-original.md -Target copilot -OutDir .
```

### 学习诊断流程

按顺序阅读：
1. `half-baked-skill.md`（看反例）
2. `bug-fix-original.md`（看正常作品）
3. `bug-fix-copilot.md`（看跨工具适配）
4. `bug-fix-optimized.md`（看优化到 94 分）
