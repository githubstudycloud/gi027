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

## 一键跑通
在仓库根目录执行：

```powershell
python .github/skills/log-analysis-pipeline-v2/scripts/log_analysis_core_v2.py analyze `
  --input-files `
    .github/skills/log-analysis-pipeline-v2/temp/cases/case-001-login-timeout.json `
    .github/skills/log-analysis-pipeline-v2/temp/cases/case-001-login-timeout.txt `
    .github/skills/log-analysis-pipeline-v2/temp/cases/case-002-auth-signature.json `
    .github/skills/log-analysis-pipeline-v2/temp/cases/case-002-auth-signature.txt `
    .github/skills/log-analysis-pipeline-v2/temp/cases/case-003-cache-leak-legacy-typo.json `
    .github/skills/log-analysis-pipeline-v2/temp/cases/case-003-cache-leak-legacy-typo.txt `
  --field-map       .github/skills/log-analysis-pipeline-v2/temp/field-map.json `
  --dimension-rules .github/skills/log-analysis-pipeline-v2/temp/dimension-rules.json `
  --report-layout   .github/skills/log-analysis-pipeline-v2/temp/report-layout.json `
  --output-dir      .github/skills/log-analysis-pipeline-v2/temp/output `
  --locale zh-CN
```

预期：
- 同名 JSON+TXT 自动配对合并 → 共 **3 条**记录
- 报告列按 `report-layout.json` 的同义名（`problem_category` / `执行结果` / `用例名称` / `key_evidence` 等）渲染
- 旧拼写 `key_evdence` 也能进 `keyEvidence` 列
