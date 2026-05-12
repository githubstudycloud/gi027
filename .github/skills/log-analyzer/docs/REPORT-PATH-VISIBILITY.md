# 报告产物路径如何在客户端正确显示 —— 分析与解决方案

> 适用范围：`log-analyzer` / `log-analysis-pipeline-v2` 等 skill。
> 适用宿主：GitHub Copilot Chat、Claude Code、OpenCode、Codex CLI、CherryStudio 自定义客户端，以及任何通过 stdout/stderr 与脚本交互的 AI 客户端。

---

## 1. 问题陈述

Skill 内部 Python 脚本 `analyze` 会在 `--output-dir` 下生成多份产物：

| 产物 | 默认路径（相对 output-dir） |
|---|---|
| Markdown 报告 | `log-analysis-report.md` |
| HTML 报告 | `log-analysis-report.html` |
| 归一化记录（紧凑 JSON） | `normalized-records.json` |
| 摘要 | `summary.json` |

**Python 写盘成功 ≠ 客户端 UI 上一定能看见／可点击。** 实际反馈出来的现象包括：

- Copilot Chat 把 stdout 当纯文本贴出来，路径不是可点击链接。
- Claude Code 把相对路径解析到了**当前工作区**而不是 skill 目录下，导致 404。
- OpenCode 在 `.opencode/skills/` 下运行 skill，但 UI 的"打开文件"按钮只接受 workspace-relative 路径。
- CherryStudio 自定义 webview 里 `file://` 链接被 CSP 拦截，HTML 报告完全打不开。
- Windows 路径里的 `\` 被 markdown 当转义字符吞掉（`D:\foo\bar` → `D:foobar`）。
- 引入时间戳子目录后 (`timestamped/<ts>/`) 调用方根本无从猜测最终路径。

**根本原因：**Skill 把"写文件"当成了交付契约，但实际的交付契约是"**客户端能让用户打开这个文件**"。两者之间隔着 stdout 文本约定、宿主沙箱、UI 渲染规则。

---

## 2. 失败模式分类

### 2.1 路径表达层
| ID | 失败模式 | 触发条件 |
|---|---|---|
| P1 | 相对路径但 CWD 不一致 | 用户在仓库根目录调用、宿主在 skill 目录调用、CI 在临时目录调用 |
| P2 | 反斜杠被吃掉 | Windows 输出 `D:\...` 进入 markdown 渲染器 |
| P3 | 绝对路径含空格未编码 | `C:\Users\John Doe\...` 在 `file://` 中断裂 |
| P4 | 时间戳目录调用方未知 | `timestamped/20260512-093000/` 在 stdout 出现前无法预测 |
| P5 | 长链接被 UI 截断/折行 | 列宽限制导致复制后路径残缺 |

### 2.2 渲染层
| ID | 失败模式 | 触发条件 |
|---|---|---|
| R1 | 客户端不识别裸路径 | 必须显式 `[text](url)` 或 `file://` 才能点 |
| R2 | 客户端不允许 `file://` | webview CSP、浏览器安全策略 |
| R3 | 客户端只接受 workspace-relative | VS Code 文件链接、Copilot 链接规约 |
| R4 | 不渲染 HTML 报告，只渲染 markdown | 多数 chat UI |
| R5 | stdout 末尾被流式截断 | 输出过大、客户端只保留最后 N 行 |

### 2.3 文件系统层
| ID | 失败模式 | 触发条件 |
|---|---|---|
| F1 | 沙箱内 skill 不能写出到工作区 | OpenCode/Claude Code 的工具沙箱 |
| F2 | 同名覆盖 | 重复运行覆盖了用户正在看的报告 |
| F3 | 跨盘符 / 跨容器路径 | Docker、WSL、远程 SSH 工作区 |

---

## 3. 现状盘点（本仓库）

`analyze` CLI 在成功后已经做的事：

```python
print(json.dumps(res, ensure_ascii=False, indent=2))
# res = {
#   "reportPath": "...",
#   "htmlPath": "...",
#   "normalizedPath": "...",
#   "summaryPath": "...",
#   "outputDir": "...",
#   "totalRecords": N, "totalGroups": M, ...
# }
```

✅ 优点：已有机器可读的结构化清单。
⚠️ 不足：
1. 路径全部是 `str(Path)` —— Windows 下是反斜杠，进入 markdown 会出问题（P2）。
2. 没有 workspace-relative 形式（R3）。
3. 没有 `file://` URI 形式（R1）。
4. 没有一段"AI 友好的人类可读摘要"，模型可能不会把 JSON 反引号包好。
5. 时间戳子目录每次都变（P4），没有写一个 `latest` 稳定别名。

---

## 4. 解决方案

### 4.1 输出契约（必须）

`analyze` 的 **stdout 最后一行**保证是单行 JSON manifest，字段如下；每个路径同时提供 4 种形式：

```json
{
  "schemaVersion": "1.0",
  "outputDir": {
    "abs": "D:/20260422/.github/skills/log-analyzer/reports/output/timestamped/20260512-093000",
    "rel": ".github/skills/log-analyzer/reports/output/timestamped/20260512-093000",
    "uri": "file:///D:/20260422/.github/skills/log-analyzer/reports/output/timestamped/20260512-093000",
    "posix": ".github/skills/log-analyzer/reports/output/timestamped/20260512-093000"
  },
  "artifacts": {
    "reportMd":      { "abs": "...", "rel": "...", "uri": "...", "posix": "..." },
    "reportHtml":    { "abs": "...", "rel": "...", "uri": "...", "posix": "..." },
    "normalized":    { "abs": "...", "rel": "...", "uri": "...", "posix": "..." },
    "summary":       { "abs": "...", "rel": "...", "uri": "...", "posix": "..." }
  },
  "latest": {
    "outputDir": ".github/skills/log-analyzer/reports/output/latest",
    "reportMd":  ".github/skills/log-analyzer/reports/output/latest/log-analysis-report.md"
  },
  "totalRecords": 123, "totalGroups": 17
}
```

设计要点：
- **始终用正斜杠** 的 posix 形式，避免 P2/P3。
- `rel` 相对 `process.cwd()`，由脚本调用 `os.path.relpath` 计算，命中 R3。
- `uri` 用 `pathlib.Path(...).as_uri()`，已做空格/Unicode 编码，命中 R1，但保留 R2 备用。
- `latest/` 是同 `outputDir` 的**软链接或拷贝**，给"调用方还不知道时间戳"的场景一个稳定锚点（P4）。Windows 没权限建符号链接时退化为 junction 或目录拷贝。

### 4.2 人类可读摘要（强烈建议）

在 JSON 之前，先输出一段紧凑 markdown，让任何不解析 JSON 的 UI 也能给用户可点链接：

```markdown
## 报告产物
- 📄 Markdown：[log-analysis-report.md](./.github/skills/log-analyzer/reports/output/latest/log-analysis-report.md)
- 🌐 HTML：[log-analysis-report.html](./.github/skills/log-analyzer/reports/output/latest/log-analysis-report.html)
- 📊 摘要：[summary.json](./.github/skills/log-analyzer/reports/output/latest/summary.json)
- 📦 归一化：[normalized-records.json](./.github/skills/log-analyzer/reports/output/latest/normalized-records.json)
- 📂 目录：`.github/skills/log-analyzer/reports/output/latest/`
```

要点：
- 路径全部 posix 正斜杠。
- 使用 `latest/` 锚定，每次都一样，便于 UI 收藏 / AI 复用。
- `./` 开头让 VS Code、Cursor、Trae、IDEA AI 插件按 workspace-relative 解析。
- 同时给"目录"的 backtick 形式，方便复制粘贴。

### 4.3 Skill 内部实施（代码骨架）

修改 `analyze()` 返回值与 `main()` 的最终输出：

```python
def _path_quadruple(p: Path, cwd: Path) -> dict[str, str]:
    p = p.resolve()
    posix = p.as_posix()
    try:
        rel = os.path.relpath(p, cwd).replace("\\", "/")
    except ValueError:  # 跨盘符
        rel = posix
    return {"abs": posix, "rel": rel, "uri": p.as_uri(), "posix": posix}

def _maintain_latest(output_dir: Path) -> Path:
    """在 reports/output/latest 指向最新一次运行。优先 symlink，回退到 junction，再回退到 copy。"""
    latest = output_dir.parent / "latest"
    try:
        if latest.exists() or latest.is_symlink():
            if latest.is_symlink() or latest.is_dir():
                if latest.is_symlink(): latest.unlink()
                else: shutil.rmtree(latest)
        try:
            latest.symlink_to(output_dir, target_is_directory=True)
        except (OSError, NotImplementedError):
            shutil.copytree(output_dir, latest)
    except Exception:
        pass  # latest 是"锦上添花"，失败不影响主流程
    return latest
```

并在 `main()` 末尾用：
```python
print(_render_summary_markdown(res))   # 4.2 的 markdown
print(json.dumps(res, ensure_ascii=False))  # 单行 JSON manifest（4.1）
```

### 4.4 客户端侧适配

**Copilot / Claude Code / OpenCode**：依赖 4.2 的 markdown 链接和 4.1 的 JSON 即可，无需改宿主。

**CherryStudio 自定义客户端**：
1. 在 main process 拿到 stdout 后，按最后一行解析 JSON。
2. 把 manifest 通过 IPC 发给 renderer。
3. Renderer 用 `webview.openExternal(uri)` 而不是 `<a href="file://...">`，绕过 CSP（解决 R2）。
4. HTML 报告若必须内嵌显示，用 `<iframe sandbox="allow-same-origin">` + `file://` 不行时改用读取文件内容后 `srcdoc` 注入。

最小渲染端伪代码：
```js
const lines = stdout.trim().split('\n');
const manifest = JSON.parse(lines[lines.length - 1]);
const html = await fs.readFile(manifest.artifacts.reportHtml.abs, 'utf8');
iframe.srcdoc = html;
```

---

## 5. 测试用例（必须加进 `run_test_suite`）

| 用例 | 断言 |
|---|---|
| manifest 末行解析 | `json.loads(stdout.splitlines()[-1])` 不抛异常 |
| 路径四元组完整 | 每个 artifact 都有 abs/rel/uri/posix 四字段 |
| posix 字段不含 `\` | `"\\" not in manifest["artifacts"]["reportMd"]["posix"]` |
| `uri` 通过 `urllib.parse.urlparse` 解析后 scheme=='file' | 真 |
| `latest/` 存在且 `log-analysis-report.md` 可读 | 真 |
| 跨 CWD 调用 rel 仍可点 | 在两个不同 CWD 各跑一次，断言 rel 不同但都是合法相对路径 |

加这 6 条进现有 18 项里，目标 24/24。

---

## 6. 失败模式 → 对策对应表

| 失败模式 | 对策 |
|---|---|
| P1 CWD 不一致 | 同时输出 abs + rel + uri；`latest/` 锚点 |
| P2 反斜杠被吃 | 全部输出 posix |
| P3 空格未编码 | `Path.as_uri()` |
| P4 时间戳未知 | `latest/` 软链 |
| P5 长链接截断 | manifest 单行 JSON 在最后；markdown 链接不依赖断点 |
| R1 不识别裸路径 | `[text](path)` markdown 链接 |
| R2 file:// 被 CSP 拦 | manifest 提供 abs，渲染端用 IPC 读文件后 `srcdoc` 注入 |
| R3 只认 workspace-relative | `rel` 字段 |
| R4 不渲染 HTML | 同时输出 markdown 报告链接 |
| R5 stdout 被截断 | manifest 单行紧凑 JSON 放最后；上方先给人类摘要 |
| F1 沙箱不让写工作区 | 通过 `--output-dir` 让宿主指定可写位置 |
| F2 重复运行覆盖 | 默认 timestamped 子目录 |
| F3 跨容器路径 | abs 用容器内路径，rel 用工作区相对；宿主负责映射 |

---

## 7. 落地清单（实施顺序）

1. [ ] `analyze()` 内部把每个产物路径打包为 `_path_quadruple` 四元组。
2. [ ] 新增 `_maintain_latest()`，写 `reports/output/latest`。
3. [ ] `main()` 在 JSON 之前先打印人类可读 markdown 块。
4. [ ] manifest 末行改为**单行紧凑 JSON**（不 indent），便于 `tail -1 | jq`。
5. [ ] `run_test_suite` 增加 §5 的 6 条断言（18 → 24）。
6. [ ] `SKILL.md` 增加"产物路径契约 v1.0"章节，链接到本文档。
7. [ ] CherryStudio 客户端示例代码放到 `examples/cherrystudio-renderer/`（可选）。

每步都不破坏现有 18/18 测试，stdout 上方增加内容，下方仍保留可解析 JSON。

---

## 8. 兼容性与回滚

- manifest 增加字段属于**向后兼容扩展**：老的调用方读 `reportPath`/`htmlPath` 仍然能拿到字符串（保留为 posix 形式）。
- `latest/` 是新建目录，对老调用方透明。
- 人类可读 markdown 仅在 stdout 上方追加，不影响"取最后一行作为 JSON"的约定。

如需回滚：删除 `_maintain_latest` 调用与 `_render_summary_markdown` 输出即可。
