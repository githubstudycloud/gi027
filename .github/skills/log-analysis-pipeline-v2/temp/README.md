# temp/ — 实战演练样例

> 这个目录是**给你照着改**的真实示例集，不影响 v2 的内置自检。

## 目录用途
1. `field-map.json` / `dimension-rules.json` / `report-layout.json`
   — 假设你已经从 [`../assets/*.example.json`](../assets/) 复制并改名（**去掉 `.example`**），
   这就是改完后的样子。注意 `.example.json` 不会被脚本自动加载，必须通过 CLI 参数显式指向。

2. `cases/` — 三组真实结构的 JSON + 同名 TXT 用例：
   - `case-001-login-timeout.*` — 网络超时（含完整 `key_evidence` 数组）
   - `case-002-auth-signature.*` — 签名错误（NTP 时间漂移）
   - `case-003-cache-leak-legacy-typo.*` — 故意使用旧拼写 `key_evdence` 演示向后兼容

## 是否需要去掉 `.example` 后缀？
- `.example.json` 本身不会被自动加载。
- **推荐做法**：把 `assets/xxx.example.json` 复制一份到 `assets/` 同级（或本 `temp/`），改名为 `xxx.json`。
- v2.2 起脚本会 **自动发现** `assets/field-map.json`、`assets/dimension-rules.json`、`assets/report-layout.json`（优先）或本 `temp/` 下同名文件（次选），AI 以自然语言触发时**无需额外传参**。
- CLI 显式 `--field-map/--dimension-rules/--report-layout` 仍然优先级最高，便于临时切换。

## TXT 输入相关（v2.3+）
- 当同 stem 同时有 `xxx.json` 和 `xxx.txt` 时，**优先 JSON、忽略 TXT**，避免 TXT 不完整导致出现 N/A 行。
- TXT 现支持「用例失败根因分析结果」编号分段格式（`(1)问题大类` … `(7)问题重跑结论`），同时仍兼容传统 `key: value`。
- 若拿到的是任意自由格式 TXT，**建议先让大模型按字段名转 JSON 再调用**：`case_name / problem_category / problem_subcategory / root_case_conclusion / key_evidence(数组，元素含 reference_doc/log_match) / fix_action / fix_conclusion / rerun_result / analysis_time`。

## 一键跑通
> 先 `cd` 到 skill 目录再执行；`<skills-root>` = 你实际安装 skill 的根目录（GitHub Copilot=`.github/skills`，Claude Code=`.claude/skills`，OpenCode=`.opencode/skills`，Codex 等同理）。脚本通过 `__file__` 自动定位资源，所以下面所有相对路径在任何宿主下都成立。

```powershell
cd <skills-root>/log-analysis-pipeline-v2
python scripts/log_analysis_core_v2.py analyze `
  --input-files `
    temp/cases/case-001-login-timeout.json `
    temp/cases/case-001-login-timeout.txt `
    temp/cases/case-002-auth-signature.json `
    temp/cases/case-002-auth-signature.txt `
    temp/cases/case-003-cache-leak-legacy-typo.json `
    temp/cases/case-003-cache-leak-legacy-typo.txt `
  --field-map       temp/field-map.json `
  --dimension-rules temp/dimension-rules.json `
  --report-layout   temp/report-layout.json `
  --output-dir      temp/output `
  --locale zh-CN
```

预期：
- 同名 JSON+TXT 自动配对合并 → 共 **3 条**记录
- 报告列按 `report-layout.json` 的同义名（`problem_category` / `执行结果` / `用例名称` / `key_evidence` 等）渲染
- 旧拼写 `key_evdence` 也能进 `keyEvidence` 列
