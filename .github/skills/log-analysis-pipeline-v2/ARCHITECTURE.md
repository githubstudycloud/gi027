# 架构说明（log-analysis-pipeline-v2）

## 总体流水线

```
  ┌─ analyze-logs.ps1  (Windows 优先)
  ├─ run-skill.sh      (Linux/macOS 优先)
  ├─ run-skill.mjs     (Node 兜底)
  └─ analyze-logs.py / run-skill-tests.py  (Python 直跑)
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │   log_analysis_core_v2.py (核心)    │
   │                                     │
   │  load_field_map ─┐                  │
   │                  ├─ _flatten_alias_table ──► {alias→canonical}  (一次)
   │  load_group_by ──┘                                              │
   │                                                                  │
   │  for file in inputs:                                             │
   │    if .json: _load_json (bytes) → _parse_json_payload            │
   │    if .txt:  _parse_txt (find/split fast path)                   │
   │    for raw in payload: _record_from_raw  ──► dict[str,str]       │
   │                                                                  │
   │  _group_records (default groupBy fast path,                      │
   │                  _Group.__slots__ + 增量去重)                    │
   │                                                                  │
   │  _build_report  ──► Markdown (单表 + <br> 多行)                  │
   │  _write_normalized (compact JSON)                                │
   │  _write_summary    (pretty JSON)                                 │
   └─────────────────────────────────────┘
```

## 与 v1 的关键路径差异

| 阶段 | v1 | v2 |
|---|---|---|
| 字段映射查找 | 每条记录 × 每字段 × 遍历 alias 列表 | 一次性扁平化为 `{alias: canonical}`，O(1) 查找 |
| TXT 行解析 | `re.match(...)` 每行 | `find(":") / find("：")` + `split` 快路径 |
| 记录构造 | parse → `to_hashable_record` → `get_field_value` × 字段数 | 单遍直接产出 `dict[str,str]` |
| 分组聚合 | `defaultdict(list)` + 二次遍历做单元格字符串 | `_Group(__slots__)` 增量构建去重列表 |
| 渲染 | 调用 `format_multi_line_cells` / `group_values` 二次遍历 items | 直接 `<br>`.join 已构造好的字段 |
| JSON 输入 | `read_text(encoding="utf-8-sig")` | `read_bytes()` + 手动 BOM 处理 |
| normalized JSON 输出 | `json.dumps(..., indent=2)` | `json.dumps(..., separators=(",",":"))` 紧凑 |

## 扩展点
- **字段映射**：`assets/field-map.example.json`（结构 `{ "fields": {canonical: [aliases...]} }`）
- **维度规则**：`assets/dimension-rules.example.json`（`{ "groupBy": [...] }`）
- **语言包**：`assets/locales/<locale>.json`，与 v1 共用 schema
- **运行时配置**：`assets/runtime-config.example.json`（platform / runtime / locale / outputDir）
- **报告布局**：`assets/report-layout.example.json`

## 性能基准的可复现性
- `scripts/benchmark.py` 通过 `importlib.util.spec_from_file_location` 同时
  加载 v1 与 v2 的核心模块，对**完全相同的 fixture 文件**调用各自的 `analyze`，
  对每一档规模都做 1 次 warmup + 5 次正式测量并汇总 min/avg/max
- fixture 由 v2 的 `generate_fixtures` 产生，确保两侧输入一致
- 输出 `reports/benchmark.md` + `reports/benchmark.json`

## 进一步可探索的方向（未实施）
- 多输入文件并发解析（`concurrent.futures.ThreadPoolExecutor`，I/O bound 场景受益）
- 可选 `orjson` 加速（保持 stdlib 兜底）
- normalized JSON 流式写出（10 万条以上规模下减少内存峰值）
