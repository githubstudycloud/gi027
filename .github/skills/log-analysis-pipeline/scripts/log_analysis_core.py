from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DEFAULT_LOCALE = "en-US"


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


def default_locale() -> dict[str, str]:
    return {
        "title": "Log Analysis Summary Report",
        "overview": "Overview",
        "summary": "Category Summary",
        "details": "Case Matrix",
        "metric": "Metric",
        "value": "Value",
        "inputFiles": "Input files",
        "totalRecords": "Total records",
        "totalGroups": "Total groups",
        "totalCategories": "Total categories",
        "category": "Issue Category",
        "subcategory": "Issue Subcategory",
        "rootCause": "Root Cause",
        "count": "Count",
        "cases": "Use Cases",
        "evidence": "Key Evidence",
        "fixAction": "Fix Action",
        "fixConclusion": "Fix Conclusion",
        "rerunConclusion": "Rerun Conclusion",
        "sources": "Source Files",
        "performance": "Performance",
        "elapsedMs": "Elapsed (ms)",
        "dataset": "Dataset",
        "result": "Result",
        "pass": "PASS",
        "fail": "FAIL",
        "reportTitle": "Log Analysis Skill Test Report",
        "conclusion": "Conclusion",
        "ready": "Ready for release: commit, push, tag.",
        "fixBeforeRelease": "Fix failed checks before release.",
        "language": "Language",
        "runtime": "Runtime",
    }


def zh_locale() -> dict[str, str]:
    return {
        "title": "日志分析汇总报告",
        "overview": "总览",
        "summary": "分类汇总",
        "details": "用例矩阵",
        "metric": "指标",
        "value": "值",
        "inputFiles": "输入文件数",
        "totalRecords": "记录总数",
        "totalGroups": "分组数量",
        "totalCategories": "类别数量",
        "category": "问题大类",
        "subcategory": "问题小类",
        "rootCause": "根因诊断结论",
        "count": "数量",
        "cases": "用例名称",
        "evidence": "关键佐证信息",
        "fixAction": "问题修复动作",
        "fixConclusion": "问题修复结论",
        "rerunConclusion": "用例重跑结论",
        "sources": "来源文件",
        "performance": "性能",
        "elapsedMs": "耗时（ms）",
        "dataset": "数据集",
        "result": "结果",
        "pass": "通过",
        "fail": "失败",
        "reportTitle": "日志分析技能测试报告",
        "conclusion": "结论",
        "ready": "可以正式发布：提交、推送、打 tag。",
        "fixBeforeRelease": "请先修复失败项，再发布。",
        "language": "语言",
        "runtime": "运行时",
    }


def load_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_locale(locale: str | None = None, locale_file: Path | None = None) -> dict[str, str]:
    if locale_file and locale_file.exists():
        data = load_json_file(locale_file)
        return dict(data)
    if locale == "zh-CN":
        candidate = ASSETS / "locales" / "zh-CN.json"
        if candidate.exists():
            return dict(load_json_file(candidate))
        return zh_locale()
    if locale == "en-US" or not locale:
        candidate = ASSETS / "locales" / "en-US.json"
        if candidate.exists():
            return dict(load_json_file(candidate))
        return default_locale()
    candidate = ASSETS / "locales" / f"{locale}.json"
    if candidate.exists():
        return dict(load_json_file(candidate))
    return default_locale()


def normalize_text(value: Any) -> str:
    if value is None:
        return "N/A"
    text = str(value).strip()
    if not text:
        return "N/A"
    text = re.sub(r"\s+", " ", text)
    return text


def to_hashable_record(record: Any) -> dict[str, Any]:
    if isinstance(record, dict):
        return record
    if hasattr(record, "__dict__"):
        return dict(record.__dict__)
    return {k: getattr(record, k) for k in dir(record) if not k.startswith("_")}


def get_field_value(record: dict[str, Any], aliases: list[str]) -> str:
    for alias in aliases:
        if alias in record:
            value = record.get(alias)
            if value is not None and str(value).strip():
                return normalize_text(value)
    return "N/A"


def parse_json_file(path: Path) -> list[Any]:
    parsed = load_json_file(path)
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        for key in ("records", "items", "data"):
            if key in parsed:
                data = parsed[key]
                if isinstance(data, list):
                    return data
                return [data]
        return [parsed]
    return [parsed]


def parse_txt_file(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig").strip()
    if not text:
        return []
    blocks = re.split(r"(?:\r?\n){2,}", text)
    records: list[dict[str, Any]] = []
    for block in blocks:
        rec: dict[str, Any] = {}
        for line in block.splitlines():
            m = re.match(r"^\s*([^:：]+)\s*[:：]\s*(.*)$", line)
            if m:
                rec[m.group(1).strip()] = m.group(2).strip()
        if rec:
            records.append(rec)
    return records


def load_field_map(path: Path | None) -> dict[str, list[str]]:
    if not path:
        return default_field_map()
    if not path.exists():
        raise FileNotFoundError(f"Field map file not found: {path}")
    data = load_json_file(path)
    fields = data.get("fields") if isinstance(data, dict) else None
    if not isinstance(fields, dict):
        return default_field_map()
    mapped: dict[str, list[str]] = {}
    for key, value in fields.items():
        if isinstance(value, list):
            mapped[key] = [str(item) for item in value]
    return mapped or default_field_map()


def load_group_by(path: Path | None) -> list[str]:
    default = ["issueCategory", "issueSubcategory", "rootCauseConclusion"]
    if not path:
        return default
    if not path.exists():
        raise FileNotFoundError(f"Dimension rules file not found: {path}")
    data = load_json_file(path)
    group_by = data.get("groupBy") if isinstance(data, dict) else None
    if isinstance(group_by, list) and group_by:
        return [str(item) for item in group_by]
    return default


def normalize_record(record: Any, field_map: dict[str, list[str]], source_file: Path) -> dict[str, str]:
    record = to_hashable_record(record)
    normalized: dict[str, str] = {}
    for canonical, aliases in field_map.items():
        normalized[canonical] = get_field_value(record, aliases)
    normalized["sourceFile"] = str(source_file)
    return normalized


def group_records(records: list[dict[str, str]], group_by: list[str]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for record in records:
        key = tuple(record.get(field, "N/A") for field in group_by)
        groups[key].append(record)
    rows: list[dict[str, Any]] = []
    for key, items in groups.items():
        first = items[0]
        rows.append({
            "key": key,
            "count": len(items),
            "category": first.get("issueCategory", "N/A"),
            "subcategory": first.get("issueSubcategory", "N/A"),
            "rootCause": first.get("rootCauseConclusion", "N/A"),
            "useCaseName": items,
        })
    rows.sort(key=lambda row: (-row["count"], row["category"], row["subcategory"], row["rootCause"]))
    return rows


def group_values(items: list[dict[str, str]], field: str) -> str:
    values: list[str] = []
    seen: set[str] = set()
    for item in items:
        value = normalize_text(item.get(field))
        if value not in seen:
            seen.add(value)
            values.append(value)
    return "<br>".join(values) if values else "N/A"


def format_multi_line_cells(items: list[dict[str, str]], field: str, prefix: str = "") -> str:
    lines = []
    for idx, item in enumerate(items, 1):
        value = normalize_text(item.get(field))
        if prefix:
            lines.append(f"{idx}. {prefix}{value}")
        else:
            lines.append(f"{idx}. {value}")
    return "<br>".join(lines) if lines else "N/A"


def build_report(rows: list[dict[str, Any]], records: list[dict[str, str]], input_files: list[Path], locale: dict[str, str], locale_name: str, runtime_name: str) -> str:
    lines: list[str] = []
    lines.append(f"# {locale['title']}")
    lines.append("")
    lines.append(f"- {locale['language']}: {locale_name}")
    lines.append(f"- {locale['runtime']}: {runtime_name}")
    lines.append("")
    lines.append(f"## {locale['overview']}")
    lines.append("")
    lines.append(f"| {locale['metric']} | {locale['value']} |")
    lines.append("|---|---|")
    lines.append(f"| {locale['inputFiles']} | {len(input_files)} |")
    lines.append(f"| {locale['totalRecords']} | {len(records)} |")
    lines.append(f"| {locale['totalGroups']} | {len(rows)} |")
    lines.append(f"| {locale['totalCategories']} | {len({(row['category'], row['subcategory']) for row in rows})} |")
    lines.append("")
    lines.append(f"## {locale['summary']}")
    lines.append("")
    lines.append(f"| {locale['category']} | {locale['subcategory']} | {locale['rootCause']} | {locale['count']} | {locale['cases']} | {locale['evidence']} | {locale['fixAction']} | {locale['fixConclusion']} | {locale['rerunConclusion']} | {locale['sources']} |")
    lines.append("|---|---|---|---:|---|---|---|---|---|---|")
    for row in rows:
        items = row["useCaseName"]
        lines.append(
            "| "
            f"{row['category']} | {row['subcategory']} | {row['rootCause']} | {row['count']} | "
            f"{format_multi_line_cells(items, 'useCaseName')} | "
            f"{format_multi_line_cells(items, 'keyEvidence')} | "
            f"{group_values(items, 'fixAction')} | "
            f"{group_values(items, 'fixConclusion')} | "
            f"{group_values(items, 'rerunConclusion')} | "
            f"{group_values(items, 'sourceFile')} |"
        )
    lines.append("")
    lines.append(f"## {locale['details']}")
    lines.append("")
    lines.append(f"- {locale['count']}: {len(rows)}")
    lines.append(f"- {locale['totalRecords']}: {len(records)}")
    lines.append("")
    return "\n".join(lines)


def write_summary(output_dir: Path, records: list[dict[str, str]], rows: list[dict[str, Any]], input_files: list[Path], locale_name: str, runtime_name: str) -> Path:
    summary = {
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "totalFiles": len(input_files),
        "totalRecords": len(records),
        "totalGroups": len(rows),
        "groupBy": ["issueCategory", "issueSubcategory", "rootCauseConclusion"],
        "files": [str(path) for path in input_files],
        "locale": locale_name,
        "runtime": runtime_name,
    }
    path = output_dir / "summary.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_normalized(output_dir: Path, records: list[dict[str, str]]) -> Path:
    path = output_dir / "normalized-records.json"
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def analyze(input_files: list[Path], output_dir: Path, field_map_path: Path | None = None, dimension_rules_path: Path | None = None, locale_name: str = DEFAULT_LOCALE, locale_file: Path | None = None, runtime_name: str = "python") -> dict[str, Any]:
    field_map = load_field_map(field_map_path)
    group_by = load_group_by(dimension_rules_path)
    locale = load_locale(locale_name, locale_file)
    resolved: list[Path] = []
    for item in input_files:
        if item.exists():
            resolved.append(item.resolve())
    if not resolved:
        raise FileNotFoundError("No supported input files were found.")

    all_records: list[dict[str, str]] = []
    for item in resolved:
        ext = item.suffix.lower()
        if ext == ".json":
            source = parse_json_file(item)
        elif ext == ".txt":
            source = parse_txt_file(item)
        else:
            continue
        for rec in source:
            all_records.append(normalize_record(rec, field_map, item))

    if not all_records:
        raise ValueError("No valid records were parsed from input files.")

    rows = group_records(all_records, group_by)
    ensure_output_dir(output_dir)
    normalized_path = write_normalized(output_dir, all_records)
    summary_path = write_summary(output_dir, all_records, rows, resolved, locale_name, runtime_name)
    report_path = output_dir / "log-analysis-report.md"
    report_path.write_text(build_report(rows, all_records, resolved, locale, locale_name, runtime_name), encoding="utf-8")
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


def _records_for_size(size: int) -> list[dict[str, Any]]:
    records = []
    categories = ["Stability", "Correctness", "Performance", "Consistency"]
    subcategories = ["Timeout", "Signature", "Mapping", "Network", "Load"]
    for i in range(size):
        category = categories[i % len(categories)]
        sub = subcategories[i % len(subcategories)]
        records.append({
            "useCaseName": f"Case-{size}-{i+1}",
            "issueCategory": category,
            "issueSubcategory": sub,
            "rootCauseConclusion": f"Root cause {i % 7}",
            "keyEvidence": f"Evidence {i+1}",
            "fixAction": f"Action {i % 5}",
            "fixConclusion": "Fixed" if i % 2 == 0 else "Mitigated",
            "rerunConclusion": "Passed",
        })
    return records


def generate_fixtures(output_dir: Path, sizes: Iterable[int] = (10, 20, 200)) -> list[Path]:
    ensure_output_dir(output_dir)
    written: list[Path] = []
    for size in sizes:
        records = _records_for_size(size)
        json_path = output_dir / f"sample-{size}.json"
        txt_path = output_dir / f"sample-{size}.txt"
        json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        txt_blocks = []
        for rec in records:
            txt_blocks.append("\n".join(f"{k}: {v}" for k, v in rec.items()))
        txt_path.write_text("\n\n".join(txt_blocks), encoding="utf-8")
        written.extend([json_path, txt_path])
    return written


def run_test_suite(skill_root: Path, locale_name: str = DEFAULT_LOCALE) -> dict[str, Any]:
    fixtures_dir = skill_root / "tests" / "fixtures"
    output_dir = skill_root / "reports" / "output"
    ensure_output_dir(fixtures_dir)
    ensure_output_dir(output_dir)
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

    alternate_locale = "zh-CN" if locale_name != "zh-CN" else "en-US"
    for lang in {locale_name, alternate_locale}:
        result = analyze([fixtures_dir / "sample-10.json", fixtures_dir / "sample-10.txt"], output_dir / f"locale-{lang}", locale_name=lang, runtime_name="python")
        report_text = Path(result["reportPath"]).read_text(encoding="utf-8")
        locale = load_locale(lang)
        ok = locale["overview"] in report_text and locale["summary"] in report_text and locale["details"] in report_text
        record(f"Locale {lang}", ok, f"Validated locale-specific headings: {lang}")

    for size in (10, 20, 200):
        json_file = fixtures_dir / f"sample-{size}.json"
        txt_file = fixtures_dir / f"sample-{size}.txt"
        started = time.perf_counter()
        result = analyze([json_file, txt_file], output_dir / f"perf-{size}", locale_name=locale_name, runtime_name="python")
        elapsed = round((time.perf_counter() - started) * 1000, 2)
        perf_rows.append({"size": size, "elapsed_ms": elapsed, "records": result["totalRecords"], "groups": result["totalGroups"]})
        report_text = (Path(result["reportPath"])).read_text(encoding="utf-8")
        ok = all(token in report_text for token in ["##", "|", "Case Matrix" if locale_name != "zh-CN" else "用例矩阵"])
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
    for row in perf_rows:
        lines.append(f"| {row['size']} | {row['elapsed_ms']} | {row['records']} | {row['groups']} |")
    lines.extend([
        "",
        f"## {locale['conclusion']}",
        "",
        locale['ready'] if result_text == "PASS" else locale['fixBeforeRelease'],
        "",
    ])
    report_path = skill_root / "reports" / "test-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return {"reportPath": str(report_path), "passed": passed == total, "total": total, "perf": perf_rows}


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
