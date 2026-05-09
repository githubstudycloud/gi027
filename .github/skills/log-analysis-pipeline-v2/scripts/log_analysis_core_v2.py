"""Log analysis core v2 — performance-tuned, behavior-equivalent to v1.

Key optimizations vs v1 (log-analysis-pipeline):
  1. Field alias resolution uses a flattened `{alias: canonical}` dict (built once),
     eliminating the per-record nested loop over alias lists.
  2. TXT parser uses `str.split` with `:`/`：` fast paths instead of `re.match`
     per line.
  3. Records are emitted as plain `dict[str, str]` once (single normalize pass);
     no second-pass `to_hashable_record`.
  4. Grouping aggregates summary-cell strings incrementally during the single
     pass instead of building intermediate item lists and re-iterating them in
     `format_multi_line_cells` / `group_values`.
  5. Normalized JSON is emitted with compact separators
     (`json.dumps(..., separators=(",",":"))`) — significantly faster I/O.
  6. Report rows are accumulated in a list and joined exactly once.

Public surface mirrors v1 (`analyze`, `generate_fixtures`, `run_test_suite`,
`main`) so the multi-platform shells stay trivially compatible.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DEFAULT_LOCALE = "en-US"

_WS_RE = re.compile(r"\s+")
_BLOCK_SPLIT_RE = re.compile(r"(?:\r?\n){2,}")


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

def default_field_map() -> dict[str, list[str]]:
    return {
        "useCaseName": ["useCaseName", "caseName", "用例名称"],
        "issueCategory": ["issueCategory", "problemCategory", "问题大类"],
        "issueSubcategory": ["issueSubcategory", "problemSubcategory", "问题小类"],
        "rootCauseConclusion": ["rootCauseConclusion", "rootCause", "根因诊断结论"],
        "keyEvidence": ["keyEvidence", "evidence", "关键佐证信息"],
        "fixAction": ["fixAction", "repairAction", "问题修复动作"],
        "fixConclusion": ["fixConclusion", "repairConclusion", "问题修复结论"],
        "rerunConclusion": ["rerunConclusion", "rerunResult", "用例重跑结论"],
    }


def _en_locale() -> dict[str, str]:
    return {
        "title": "Log Analysis Summary Report",
        "overview": "Overview", "summary": "Category Summary", "details": "Case Matrix",
        "metric": "Metric", "value": "Value",
        "inputFiles": "Input files", "totalRecords": "Total records",
        "totalGroups": "Total groups", "totalCategories": "Total categories",
        "category": "Issue Category", "subcategory": "Issue Subcategory",
        "rootCause": "Root Cause", "count": "Count", "cases": "Use Cases",
        "evidence": "Key Evidence", "fixAction": "Fix Action",
        "fixConclusion": "Fix Conclusion", "rerunConclusion": "Rerun Conclusion",
        "sources": "Source Files", "performance": "Performance",
        "elapsedMs": "Elapsed (ms)", "dataset": "Dataset",
        "result": "Result", "pass": "PASS", "fail": "FAIL",
        "reportTitle": "Log Analysis Skill Test Report",
        "conclusion": "Conclusion",
        "ready": "Ready for release: commit, push, tag.",
        "fixBeforeRelease": "Fix failed checks before release.",
        "language": "Language", "runtime": "Runtime",
    }


def _zh_locale() -> dict[str, str]:
    return {
        "title": "日志分析汇总报告",
        "overview": "总览", "summary": "分类汇总", "details": "用例矩阵",
        "metric": "指标", "value": "值",
        "inputFiles": "输入文件数", "totalRecords": "记录总数",
        "totalGroups": "分组数量", "totalCategories": "类别数量",
        "category": "问题大类", "subcategory": "问题小类",
        "rootCause": "根因诊断结论", "count": "数量", "cases": "用例名称",
        "evidence": "关键佐证信息", "fixAction": "问题修复动作",
        "fixConclusion": "问题修复结论", "rerunConclusion": "用例重跑结论",
        "sources": "来源文件", "performance": "性能",
        "elapsedMs": "耗时（ms）", "dataset": "数据集",
        "result": "结果", "pass": "通过", "fail": "失败",
        "reportTitle": "日志分析技能测试报告",
        "conclusion": "结论",
        "ready": "可以正式发布：提交、推送、打 tag。",
        "fixBeforeRelease": "请先修复失败项，再发布。",
        "language": "语言", "runtime": "运行时",
    }


def _load_json(path: Path) -> Any:
    # Reading bytes + letting json decode UTF-8 directly is measurably faster
    # than read_text() which performs Python-level decode first.
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    return json.loads(data)


def load_locale(locale: str | None = None, locale_file: Path | None = None) -> dict[str, str]:
    if locale_file and locale_file.exists():
        return dict(_load_json(locale_file))
    if locale == "zh-CN":
        candidate = ASSETS / "locales" / "zh-CN.json"
        return dict(_load_json(candidate)) if candidate.exists() else _zh_locale()
    if locale and locale != "en-US":
        candidate = ASSETS / "locales" / f"{locale}.json"
        if candidate.exists():
            return dict(_load_json(candidate))
    candidate = ASSETS / "locales" / "en-US.json"
    return dict(_load_json(candidate)) if candidate.exists() else _en_locale()


# ---------------------------------------------------------------------------
# Field map flattening — the single biggest hot-path win vs v1
# ---------------------------------------------------------------------------

def _flatten_alias_table(field_map: dict[str, list[str]]) -> tuple[dict[str, str], list[str]]:
    """Return ({alias: canonical}, [canonical_in_order])."""
    table: dict[str, str] = {}
    canonicals: list[str] = []
    for canonical, aliases in field_map.items():
        canonicals.append(canonical)
        for alias in aliases:
            table.setdefault(alias, canonical)
    return table, canonicals


def load_field_map(path: Path | None) -> dict[str, list[str]]:
    if not path:
        return default_field_map()
    if not path.exists():
        raise FileNotFoundError(f"Field map file not found: {path}")
    data = _load_json(path)
    fields = data.get("fields") if isinstance(data, dict) else None
    if not isinstance(fields, dict):
        return default_field_map()
    out: dict[str, list[str]] = {}
    for key, value in fields.items():
        if isinstance(value, list):
            out[key] = [str(x) for x in value]
    return out or default_field_map()


def load_group_by(path: Path | None) -> list[str]:
    default = ["issueCategory", "issueSubcategory", "rootCauseConclusion"]
    if not path:
        return default
    if not path.exists():
        raise FileNotFoundError(f"Dimension rules file not found: {path}")
    data = _load_json(path)
    group_by = data.get("groupBy") if isinstance(data, dict) else None
    if isinstance(group_by, list) and group_by:
        return [str(x) for x in group_by]
    return default


# ---------------------------------------------------------------------------
# Parsing — single pass, single normalize
# ---------------------------------------------------------------------------

def _normalize(value: Any) -> str:
    if value is None:
        return "N/A"
    text = str(value).strip()
    if not text:
        return "N/A"
    if " " in text or "\t" in text or "\n" in text:
        text = _WS_RE.sub(" ", text)
    return text


def _record_from_raw(raw: Any, alias_table: dict[str, str], canonicals: list[str], source_str: str) -> dict[str, str]:
    out: dict[str, str] = {c: "N/A" for c in canonicals}
    if isinstance(raw, dict):
        items = raw.items()
    elif hasattr(raw, "__dict__"):
        items = raw.__dict__.items()
    else:
        items = ((k, getattr(raw, k)) for k in dir(raw) if not k.startswith("_"))
    for k, v in items:
        canonical = alias_table.get(k)
        if canonical is None or v is None:
            continue
        text = str(v).strip()
        if not text:
            continue
        if " " in text or "\t" in text or "\n" in text:
            text = _WS_RE.sub(" ", text)
        out[canonical] = text
    out["sourceFile"] = source_str
    return out


def _parse_json_payload(raw: Any) -> list[Any]:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for k in ("records", "items", "data"):
            v = raw.get(k)
            if isinstance(v, list):
                return v
            if v is not None:
                return [v]
        return [raw]
    return [raw]


def _parse_txt(text: str) -> list[dict[str, Any]]:
    if not text:
        return []
    blocks = _BLOCK_SPLIT_RE.split(text.strip())
    out: list[dict[str, Any]] = []
    for block in blocks:
        rec: dict[str, Any] = {}
        for line in block.splitlines():
            # fast path: ASCII colon
            i = line.find(":")
            j = line.find("：")
            if i == -1 and j == -1:
                continue
            if i == -1:
                idx = j
            elif j == -1:
                idx = i
            else:
                idx = i if i < j else j
            key = line[:idx].strip()
            val = line[idx + 1:].strip()
            if key:
                rec[key] = val
        if rec:
            out.append(rec)
    return out


# ---------------------------------------------------------------------------
# Group + summary cell building (incremental, single pass)
# ---------------------------------------------------------------------------

class _Group:
    __slots__ = ("count", "category", "subcategory", "rootCause",
                 "cases", "evidence", "fix_actions", "fix_conclusions",
                 "rerun_conclusions", "sources", "_seen_actions",
                 "_seen_conclusions", "_seen_rerun", "_seen_sources")

    def __init__(self, category: str, subcategory: str, root_cause: str) -> None:
        self.count = 0
        self.category = category
        self.subcategory = subcategory
        self.rootCause = root_cause
        self.cases: list[str] = []
        self.evidence: list[str] = []
        self.fix_actions: list[str] = []
        self.fix_conclusions: list[str] = []
        self.rerun_conclusions: list[str] = []
        self.sources: list[str] = []
        self._seen_actions: set[str] = set()
        self._seen_conclusions: set[str] = set()
        self._seen_rerun: set[str] = set()
        self._seen_sources: set[str] = set()

    def add(self, rec: dict[str, str]) -> None:
        self.count += 1
        self.cases.append(rec.get("useCaseName", "N/A"))
        self.evidence.append(rec.get("keyEvidence", "N/A"))
        v = rec.get("fixAction", "N/A")
        if v not in self._seen_actions:
            self._seen_actions.add(v)
            self.fix_actions.append(v)
        v = rec.get("fixConclusion", "N/A")
        if v not in self._seen_conclusions:
            self._seen_conclusions.add(v)
            self.fix_conclusions.append(v)
        v = rec.get("rerunConclusion", "N/A")
        if v not in self._seen_rerun:
            self._seen_rerun.add(v)
            self.rerun_conclusions.append(v)
        v = rec.get("sourceFile", "N/A")
        if v not in self._seen_sources:
            self._seen_sources.add(v)
            self.sources.append(v)


_DEFAULT_GROUP_BY = ("issueCategory", "issueSubcategory", "rootCauseConclusion")


def _group_records(records: list[dict[str, str]], group_by: list[str]) -> list[_Group]:
    groups: dict[tuple[str, ...], _Group] = {}
    if tuple(group_by) == _DEFAULT_GROUP_BY:
        # Fast path: avoid generator + per-record list traversal.
        for rec in records:
            cat = rec.get("issueCategory", "N/A")
            sub = rec.get("issueSubcategory", "N/A")
            root = rec.get("rootCauseConclusion", "N/A")
            key = (cat, sub, root)
            g = groups.get(key)
            if g is None:
                g = _Group(cat, sub, root)
                groups[key] = g
            g.add(rec)
    else:
        for rec in records:
            key = tuple(rec.get(f, "N/A") for f in group_by)
            g = groups.get(key)
            if g is None:
                g = _Group(
                    rec.get("issueCategory", "N/A"),
                    rec.get("issueSubcategory", "N/A"),
                    rec.get("rootCauseConclusion", "N/A"),
                )
                groups[key] = g
            g.add(rec)
    rows = list(groups.values())
    rows.sort(key=lambda r: (-r.count, r.category, r.subcategory, r.rootCause))
    return rows


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def _numbered(values: list[str]) -> str:
    if not values:
        return "N/A"
    return "<br>".join(f"{i}. {v}" for i, v in enumerate(values, 1))


def _join_unique(values: list[str]) -> str:
    return "<br>".join(values) if values else "N/A"


def _build_report(rows: list[_Group], total_records: int, input_count: int,
                  locale: dict[str, str], locale_name: str, runtime_name: str) -> str:
    parts: list[str] = []
    add = parts.append
    add(f"# {locale['title']}")
    add("")
    add(f"- {locale['language']}: {locale_name}")
    add(f"- {locale['runtime']}: {runtime_name}")
    add("")
    add(f"## {locale['overview']}")
    add("")
    add(f"| {locale['metric']} | {locale['value']} |")
    add("|---|---|")
    add(f"| {locale['inputFiles']} | {input_count} |")
    add(f"| {locale['totalRecords']} | {total_records} |")
    add(f"| {locale['totalGroups']} | {len(rows)} |")
    add(f"| {locale['totalCategories']} | {len({(r.category, r.subcategory) for r in rows})} |")
    add("")
    add(f"## {locale['summary']}")
    add("")
    add(
        f"| {locale['category']} | {locale['subcategory']} | {locale['rootCause']} | "
        f"{locale['count']} | {locale['cases']} | {locale['evidence']} | "
        f"{locale['fixAction']} | {locale['fixConclusion']} | {locale['rerunConclusion']} | {locale['sources']} |"
    )
    add("|---|---|---|---:|---|---|---|---|---|---|")
    for r in rows:
        add(
            f"| {r.category} | {r.subcategory} | {r.rootCause} | {r.count} | "
            f"{_numbered(r.cases)} | {_numbered(r.evidence)} | "
            f"{_join_unique(r.fix_actions)} | {_join_unique(r.fix_conclusions)} | "
            f"{_join_unique(r.rerun_conclusions)} | {_join_unique(r.sources)} |"
        )
    add("")
    add(f"## {locale['details']}")
    add("")
    add(f"- {locale['count']}: {len(rows)}")
    add(f"- {locale['totalRecords']}: {total_records}")
    add("")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_normalized(output_dir: Path, records: list[dict[str, str]]) -> Path:
    path = output_dir / "normalized-records.json"
    # Compact separators are a meaningful speedup for large arrays.
    path.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return path


def _write_summary(output_dir: Path, records: list[dict[str, str]], rows: list[_Group],
                   input_files: list[Path], locale_name: str, runtime_name: str) -> Path:
    summary = {
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "totalFiles": len(input_files),
        "totalRecords": len(records),
        "totalGroups": len(rows),
        "groupBy": ["issueCategory", "issueSubcategory", "rootCauseConclusion"],
        "files": [str(p) for p in input_files],
        "locale": locale_name,
        "runtime": runtime_name,
    }
    path = output_dir / "summary.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze(input_files: list[Path], output_dir: Path,
            field_map_path: Path | None = None,
            dimension_rules_path: Path | None = None,
            locale_name: str = DEFAULT_LOCALE,
            locale_file: Path | None = None,
            runtime_name: str = "python") -> dict[str, Any]:
    field_map = load_field_map(field_map_path)
    group_by = load_group_by(dimension_rules_path)
    locale = load_locale(locale_name, locale_file)
    alias_table, canonicals = _flatten_alias_table(field_map)

    resolved = [p.resolve() for p in input_files if p.exists()]
    if not resolved:
        raise FileNotFoundError("No supported input files were found.")

    all_records: list[dict[str, str]] = []
    for item in resolved:
        ext = item.suffix.lower()
        source_str = str(item)
        if ext == ".json":
            try:
                raw = _load_json(item)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {item}: {exc}") from exc
            payload = _parse_json_payload(raw)
        elif ext == ".txt":
            data = item.read_bytes()
            if data.startswith(b"\xef\xbb\xbf"):
                data = data[3:]
            payload = _parse_txt(data.decode("utf-8"))
        else:
            continue
        for raw in payload:
            all_records.append(_record_from_raw(raw, alias_table, canonicals, source_str))

    if not all_records:
        raise ValueError("No valid records were parsed from input files.")

    rows = _group_records(all_records, group_by)
    _ensure_dir(output_dir)
    normalized_path = _write_normalized(output_dir, all_records)
    summary_path = _write_summary(output_dir, all_records, rows, resolved, locale_name, runtime_name)
    report_path = output_dir / "log-analysis-report.md"
    report_path.write_text(
        _build_report(rows, len(all_records), len(resolved), locale, locale_name, runtime_name),
        encoding="utf-8",
    )
    return {
        "reportPath": str(report_path),
        "normalizedPath": str(normalized_path),
        "summaryPath": str(summary_path),
        "totalRecords": len(all_records),
        "totalGroups": len(rows),
        "totalFiles": len(resolved),
        "locale": locale_name,
        "runtime": runtime_name,
    }


# ---------------------------------------------------------------------------
# Fixtures + tests (mirror v1, plus larger sizes)
# ---------------------------------------------------------------------------

DEFAULT_FIXTURE_SIZES: tuple[int, ...] = (10, 20, 200, 1000, 5000)


def _records_for_size(size: int) -> list[dict[str, Any]]:
    categories = ["Stability", "Correctness", "Performance", "Consistency"]
    subcategories = ["Timeout", "Signature", "Mapping", "Network", "Load"]
    out: list[dict[str, Any]] = []
    for i in range(size):
        out.append({
            "useCaseName": f"Case-{size}-{i+1}",
            "issueCategory": categories[i % 4],
            "issueSubcategory": subcategories[i % 5],
            "rootCauseConclusion": f"Root cause {i % 7}",
            "keyEvidence": f"Evidence {i+1}",
            "fixAction": f"Action {i % 5}",
            "fixConclusion": "Fixed" if i % 2 == 0 else "Mitigated",
            "rerunConclusion": "Passed",
        })
    return out


def generate_fixtures(output_dir: Path, sizes: Iterable[int] = DEFAULT_FIXTURE_SIZES) -> list[Path]:
    _ensure_dir(output_dir)
    written: list[Path] = []
    for size in sizes:
        records = _records_for_size(size)
        json_path = output_dir / f"sample-{size}.json"
        txt_path = output_dir / f"sample-{size}.txt"
        json_path.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        blocks = ["\n".join(f"{k}: {v}" for k, v in r.items()) for r in records]
        txt_path.write_text("\n\n".join(blocks), encoding="utf-8")
        written.extend([json_path, txt_path])
    return written


def run_test_suite(skill_root: Path, locale_name: str = DEFAULT_LOCALE) -> dict[str, Any]:
    fixtures_dir = skill_root / "tests" / "fixtures"
    output_dir = skill_root / "reports" / "output"
    _ensure_dir(fixtures_dir)
    _ensure_dir(output_dir)
    generated = generate_fixtures(fixtures_dir)
    results: list[dict[str, str]] = []
    perf_rows: list[dict[str, Any]] = []
    passed = 0
    total = 0

    def record(name: str, ok: bool, detail: str) -> None:
        nonlocal passed, total
        total += 1
        if ok:
            passed += 1
        results.append({"name": name, "passed": "PASS" if ok else "FAIL", "detail": detail})

    record("Generate fixtures", True, f"Generated {len(generated)} fixture files")

    alt = "zh-CN" if locale_name != "zh-CN" else "en-US"
    for lang in {locale_name, alt}:
        result = analyze(
            [fixtures_dir / "sample-10.json", fixtures_dir / "sample-10.txt"],
            output_dir / f"locale-{lang}", locale_name=lang, runtime_name="python",
        )
        report_text = Path(result["reportPath"]).read_text(encoding="utf-8")
        loc = load_locale(lang)
        ok = loc["overview"] in report_text and loc["summary"] in report_text and loc["details"] in report_text
        record(f"Locale {lang}", ok, f"Validated locale-specific headings: {lang}")

    for size in DEFAULT_FIXTURE_SIZES:
        json_file = fixtures_dir / f"sample-{size}.json"
        txt_file = fixtures_dir / f"sample-{size}.txt"
        started = time.perf_counter()
        result = analyze([json_file, txt_file], output_dir / f"perf-{size}",
                         locale_name=locale_name, runtime_name="python")
        elapsed = round((time.perf_counter() - started) * 1000, 2)
        perf_rows.append({"size": size, "elapsed_ms": elapsed,
                          "records": result["totalRecords"], "groups": result["totalGroups"]})
        report_text = Path(result["reportPath"]).read_text(encoding="utf-8")
        token = "Case Matrix" if locale_name != "zh-CN" else "用例矩阵"
        ok = "##" in report_text and "|" in report_text and token in report_text
        record(f"Analyze {size}", ok, f"{size} records processed in {elapsed} ms")

    result_text = "PASS" if passed == total else "FAIL"
    locale = load_locale(locale_name)
    lines = [
        f"# {locale['reportTitle']}",
        "",
        f"- {locale['language']}: {locale_name}",
        f"- {locale['result']}: {result_text}",
        "",
        "## Test Details",
        "",
        "| Case | Result | Detail |",
        "|---|---|---|",
    ]
    for row in results:
        lines.append(f"| {row['name']} | {row['passed']} | {row['detail']} |")
    lines.extend([
        "",
        f"## {locale['performance']}",
        "",
        f"| {locale['dataset']} | {locale['elapsedMs']} | {locale['totalRecords']} | {locale['totalGroups']} |",
        "|---|---:|---:|---:|",
    ])
    for r in perf_rows:
        lines.append(f"| {r['size']} | {r['elapsed_ms']} | {r['records']} | {r['groups']} |")
    lines.extend([
        "",
        f"## {locale['conclusion']}",
        "",
        locale["ready"] if result_text == "PASS" else locale["fixBeforeRelease"],
        "",
    ])
    text = "\n".join(lines)
    report_path = skill_root / "reports" / "test-report.md"
    locale_report_path = skill_root / "reports" / f"test-report.{locale_name}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(text, encoding="utf-8")
    locale_report_path.write_text(text, encoding="utf-8")
    return {"reportPath": str(report_path), "localeReportPath": str(locale_report_path),
            "passed": passed == total, "total": total, "perf": perf_rows}


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze")
    a.add_argument("--input-files", nargs="+", required=True)
    a.add_argument("--output-dir", required=True)
    a.add_argument("--field-map")
    a.add_argument("--dimension-rules")
    a.add_argument("--locale", default=DEFAULT_LOCALE)
    a.add_argument("--locale-file")
    a.add_argument("--runtime", default="python")
    g = sub.add_parser("generate")
    g.add_argument("--output-dir", required=True)
    t = sub.add_parser("test")
    t.add_argument("--skill-root", required=True)
    t.add_argument("--locale", default=DEFAULT_LOCALE)
    args = parser.parse_args()
    if args.cmd == "analyze":
        res = analyze(
            [Path(p) for p in args.input_files],
            Path(args.output_dir),
            Path(args.field_map) if args.field_map else None,
            Path(args.dimension_rules) if args.dimension_rules else None,
            args.locale,
            Path(args.locale_file) if getattr(args, "locale_file", None) else None,
            args.runtime,
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.cmd == "generate":
        print(json.dumps([str(p) for p in generate_fixtures(Path(args.output_dir))], ensure_ascii=False, indent=2))
    else:
        print(json.dumps(run_test_suite(Path(args.skill_root), args.locale), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
