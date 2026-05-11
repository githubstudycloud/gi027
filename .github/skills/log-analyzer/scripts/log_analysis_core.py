"""Log analysis core — performance-tuned, behavior-equivalent to v1.

Performance-tuned core (formerly v2) (log-analysis-pipeline):
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
        "useCaseName": ["useCaseName", "caseName", "case_name", "用例名称", "case_execution_info.case_name"],
        "issueCategory": ["issueCategory", "problemCategory", "problem_category", "问题大类"],
        "issueSubcategory": ["issueSubcategory", "problemSubcategory", "problem_subcategory", "问题小类"],
        "rootCauseConclusion": ["rootCauseConclusion", "rootCause", "root_case_conclusion", "根因诊断结论"],
        "keyEvidence": [
            "keyEvidence", "evidence", "key_evidence", "key_evdence", "关键佐证信息",
            "key_evidence.reference_doc", "key_evidence.log_match",
            "key_evdence.reference_doc", "key_evdence.log_match"
        ],
        "fixAction": ["fixAction", "repairAction", "问题修复动作"],
        "fixConclusion": ["fixConclusion", "repairConclusion", "问题修复结论"],
        "rerunConclusion": ["rerunConclusion", "rerunResult", "用例重跑结论", "问题重跑结论", "rerun_result"],
        "analysisTime": ["analysisTime", "analysis_time", "分析时间"],
        "deviceSn": ["deviceSn", "device_sn", "version_info.device_sn", "设备SN"],
        "deviceType": ["deviceType", "device_type", "version_info.device_type", "设备类型"],
        "platformVersion": ["platformVersion", "platform_version", "version_info.platform_version", "平台版本"],
        "hyVersion": ["hyVersion", "hy_version", "version_info.hy_version", "HY版本"],
        "caseBeginTime": ["caseBeginTime", "begin_time", "case_execution_info.begin_time", "开始时间"],
        "caseEndTime": ["caseEndTime", "end_time", "case_execution_info.end_time", "结束时间"],
        "caseDuration": ["caseDuration", "duration", "case_execution_info.duration", "耗时"],
        "caseResult": ["caseResult", "result", "case_execution_info.result", "执行结果"],
        "caseErrorMessage": ["caseErrorMessage", "error_message", "case_execution_info.error_message", "错误信息"],
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


def _normalize_key_name(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


def _build_normalized_alias_table(alias_table: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for alias, canonical in alias_table.items():
        out.setdefault(_normalize_key_name(alias), canonical)
    return out


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


def default_report_layout() -> dict[str, Any]:
    return {
        "mode": "single-table",
        "allowMultiCaseCells": True,
        "tableColumns": [
            "category", "subcategory", "rootCause", "count", "cases", "evidence",
            "fixAction", "fixConclusion", "rerunConclusion", "caseResult", "caseErrorMessage", "sources"
        ],
    }


# Canonical column keys -> set of synonyms users may write in report-layout.
# Matching is case/underscore/dot insensitive via _normalize_key_name.
_COLUMN_SYNONYMS: dict[str, str] = {}
def _register_column_synonyms() -> None:
    table: dict[str, list[str]] = {
        "category": ["category", "issueCategory", "problemCategory", "problem_category", "问题大类"],
        "subcategory": ["subcategory", "issueSubcategory", "problemSubcategory", "problem_subcategory", "问题小类"],
        "rootCause": ["rootCause", "rootCauseConclusion", "root_case_conclusion", "rootCauseDiagnosis", "根因诊断结论"],
        "count": ["count", "数量", "total"],
        "cases": ["cases", "useCases", "useCaseName", "case_name", "用例名称"],
        "evidence": ["evidence", "keyEvidence", "key_evidence", "key_evdence", "关键佐证信息"],
        "fixAction": ["fixAction", "fix_action", "repairAction", "问题修复动作"],
        "fixConclusion": ["fixConclusion", "fix_conclusion", "repairConclusion", "问题修复结论"],
        "rerunConclusion": ["rerunConclusion", "rerunResult", "rerun_result", "用例重跑结论"],
        "caseResult": ["caseResult", "result", "execution_result", "executionResult", "执行结果"],
        "caseErrorMessage": ["caseErrorMessage", "errorMessage", "error_message", "错误信息"],
        "sources": ["sources", "sourceFile", "source_file", "来源文件"],
    }
    for canonical, aliases in table.items():
        for alias in aliases:
            _COLUMN_SYNONYMS.setdefault(_normalize_key_name(alias), canonical)
_register_column_synonyms()


def _resolve_column(column: str) -> str | None:
    """Map a user-supplied column name (any synonym) to a canonical key."""
    if not column:
        return None
    return _COLUMN_SYNONYMS.get(_normalize_key_name(column))


def load_report_layout(path: Path | None) -> dict[str, Any]:
    if not path:
        return default_report_layout()
    if not path.exists():
        raise FileNotFoundError(f"Report layout file not found: {path}")
    data = _load_json(path)
    if not isinstance(data, dict):
        return default_report_layout()
    layout = default_report_layout()
    mode = data.get("mode")
    if isinstance(mode, str) and mode:
        layout["mode"] = mode
    allow_multi = data.get("allowMultiCaseCells")
    if isinstance(allow_multi, bool):
        layout["allowMultiCaseCells"] = allow_multi
    cols = data.get("tableColumns")
    if isinstance(cols, list):
        normalized_cols: list[str] = []
        for c in cols:
            text = str(c).strip()
            if not text:
                continue
            resolved = _resolve_column(text)
            normalized_cols.append(resolved if resolved else text)
        if normalized_cols:
            layout["tableColumns"] = normalized_cols
    return layout


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


def _format_key_evidence(value: Any) -> str:
    if isinstance(value, list):
        lines: list[str] = []
        for i, item in enumerate(value, 1):
            if isinstance(item, dict):
                reference_doc = _normalize(item.get("reference_doc") or item.get("referenceDoc") or item.get("doc"))
                log_match = _normalize(item.get("log_match") or item.get("logMatch") or item.get("match"))
                lines.append(f"{i}) reference_doc={reference_doc}; log_match={log_match}")
            else:
                lines.append(f"{i}) {_normalize(item)}")
        return " | ".join(lines) if lines else "N/A"
    return _normalize(value)


def _flatten_raw(raw: Any) -> dict[str, Any]:
    flattened: dict[str, Any] = {}

    def visit(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                next_path = f"{path}.{k}" if path else str(k)
                visit(v, next_path)
            return
        if isinstance(value, list):
            leaf_name = path.rsplit(".", 1)[-1].lower()
            if leaf_name in {"key_evidence", "key_evdence", "keyevidence", "evidence"}:
                flattened[path] = _format_key_evidence(value)
                leaf = path.split(".")[-1]
                flattened.setdefault(leaf, flattened[path])
                return
            if value and all(isinstance(x, dict) for x in value):
                flattened[path] = _normalize(json.dumps(value, ensure_ascii=False, separators=(",", ":")))
            else:
                flattened[path] = _normalize(" | ".join(_normalize(x) for x in value))
            leaf = path.split(".")[-1]
            flattened.setdefault(leaf, flattened[path])
            return

        flattened[path] = value
        if "." in path:
            leaf = path.split(".")[-1]
            flattened.setdefault(leaf, value)

    if isinstance(raw, dict):
        visit(raw, "")
    else:
        flattened["value"] = raw
    return flattened


def _record_from_raw(
    raw: Any,
    alias_table: dict[str, str],
    normalized_alias_table: dict[str, str],
    canonicals: list[str],
    source_str: str,
) -> dict[str, str]:
    out: dict[str, str] = {c: "N/A" for c in canonicals}
    flattened = _flatten_raw(raw)
    for k, v in flattened.items():
        canonical = alias_table.get(k)
        if canonical is None:
            canonical = normalized_alias_table.get(_normalize_key_name(k))
        if canonical is None or v is None:
            continue
        out[canonical] = _normalize(v)
    out["sourceFile"] = source_str
    return out


def _parse_json_payload(raw: Any) -> list[Any]:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        single_case_markers = (
            "case_execution_info", "version_info",
            "key_evidence", "key_evdence",
            "problem_category", "problem_subcategory",
            "root_case_conclusion", "fix_action", "rerun_result",
        )
        if any(k in raw for k in single_case_markers):
            return [raw]
        for k in ("records", "items", "data"):
            v = raw.get(k)
            if isinstance(v, list):
                return v
            if v is not None:
                return [v]
        return [raw]
    return [raw]


_TXT_TITLE_RE = re.compile(r"^[ \t]*用例失败根因分析结果[ \t]*$", re.MULTILINE)
_TXT_NUMBERED_HEADER_RE = re.compile(r"^[ \t]*[\(（]\s*(\d+)\s*[\)）]\s*([^\s:：]+(?:[^\s:：]*)?)[ \t]*$")
_TXT_HEADER_KV_RE = re.compile(r"([^\s:：]+)\s*[:：]\s*(.+?)(?=(?:\s{2,}|\t+)[^\s:：]+\s*[:：]|$)")


def _looks_like_numbered_format(text: str) -> bool:
    if _TXT_TITLE_RE.search(text):
        return True
    return bool(re.search(r"[\(（]\s*1\s*[\)）]\s*问题大类", text))


def _parse_txt_numbered_block(block: str) -> dict[str, str]:
    """Parse one record in the new numbered-section format.

    Layout (Chinese):
        用例失败根因分析结果        (title, optional)
        用例名称: <name>    分析时间: <time>
        (1)问题大类
        <content...>
        (2)问题小类
        <content...>
        (3)根因诊断结论
        ...
        (4)关键佐证信息
        参考文档特征描述: <...>
        本次日志对应信息: <...>
        (5)问题修复动作
        (6)问题修复结论
        (7)问题重跑结论
    """
    rec: dict[str, str] = {}
    current_key: str | None = None
    buf: list[str] = []

    def flush() -> None:
        nonlocal buf, current_key
        if current_key is not None:
            text = "\n".join(buf).strip()
            if text:
                rec[current_key] = text
                # If this section has nested K:V lines (e.g. 关键佐证信息), expose them
                # as their own fields too so alias resolution can pick them up.
                for sub_line in text.splitlines():
                    si = sub_line.find(":")
                    sj = sub_line.find("：")
                    if si == -1 and sj == -1:
                        continue
                    sidx = si if (sj == -1 or (si != -1 and si < sj)) else sj
                    sk = sub_line[:sidx].strip()
                    sv = sub_line[sidx + 1:].strip()
                    if sk and sv and sk not in rec:
                        rec[sk] = sv
        buf = []

    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            if current_key is not None:
                buf.append("")
            continue
        if stripped == "用例失败根因分析结果":
            continue
        m = _TXT_NUMBERED_HEADER_RE.match(line)
        if m:
            flush()
            current_key = m.group(2).strip()
            continue
        if current_key is None:
            # Header K:V line(s) like "用例名称: xxx    分析时间: yyy"
            for km in _TXT_HEADER_KV_RE.finditer(stripped):
                k = km.group(1).strip()
                v = km.group(2).strip()
                if k:
                    rec[k] = v
        else:
            buf.append(line)
    flush()
    return rec


def _parse_txt(text: str) -> list[dict[str, Any]]:
    if not text:
        return []
    if _looks_like_numbered_format(text):
        # Split on the title line; each chunk is one record.
        if _TXT_TITLE_RE.search(text):
            chunks = _TXT_TITLE_RE.split(text)
        else:
            chunks = [text]
        out: list[dict[str, Any]] = []
        for chunk in chunks:
            if not chunk.strip():
                continue
            rec = _parse_txt_numbered_block(chunk)
            if rec:
                out.append(rec)
        if out:
            return out
        # fall through to legacy parser if numbered parser yielded nothing
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
                 "rerun_conclusions", "case_results", "case_errors", "sources",
                 "_seen_actions", "_seen_conclusions", "_seen_rerun",
                 "_seen_case_results", "_seen_case_errors", "_seen_sources")

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
        self.case_results: list[str] = []
        self.case_errors: list[str] = []
        self.sources: list[str] = []
        self._seen_actions: set[str] = set()
        self._seen_conclusions: set[str] = set()
        self._seen_rerun: set[str] = set()
        self._seen_case_results: set[str] = set()
        self._seen_case_errors: set[str] = set()
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
        v = rec.get("caseResult", "N/A")
        if v not in self._seen_case_results:
            self._seen_case_results.add(v)
            self.case_results.append(v)
        v = rec.get("caseErrorMessage", "N/A")
        if v not in self._seen_case_errors:
            self._seen_case_errors.add(v)
            self.case_errors.append(v)
        v = rec.get("sourceFile", "N/A")
        if v not in self._seen_sources:
            self._seen_sources.add(v)
            self.sources.append(v)


class _ExecGroup:
    __slots__ = ("count", "result", "error_message", "duration_bucket", "cases")

    def __init__(self, result: str, error_message: str, duration_bucket: str) -> None:
        self.count = 0
        self.result = result
        self.error_message = error_message
        self.duration_bucket = duration_bucket
        self.cases: list[str] = []

    def add(self, rec: dict[str, str]) -> None:
        self.count += 1
        self.cases.append(rec.get("useCaseName", "N/A"))


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


def _duration_bucket(duration_text: str) -> str:
    text = (duration_text or "").strip().lower()
    if not text or text == "n/a":
        return "N/A"
    try:
        if text.endswith("ms"):
            seconds = float(text[:-2].strip()) / 1000.0
        elif text.endswith("s"):
            seconds = float(text[:-1].strip())
        else:
            seconds = float(text)
    except ValueError:
        return duration_text
    if seconds < 1:
        return "<1s"
    if seconds < 5:
        return "1-5s"
    if seconds < 30:
        return "5-30s"
    return ">=30s"


def _group_execution_info(records: list[dict[str, str]]) -> list[_ExecGroup]:
    groups: dict[tuple[str, str, str], _ExecGroup] = {}
    for rec in records:
        result = rec.get("caseResult", "N/A")
        error = rec.get("caseErrorMessage", "N/A")
        bucket = _duration_bucket(rec.get("caseDuration", "N/A"))
        key = (result, error, bucket)
        g = groups.get(key)
        if g is None:
            g = _ExecGroup(result, error, bucket)
            groups[key] = g
        g.add(rec)
    rows = list(groups.values())
    rows.sort(key=lambda r: (-r.count, r.result, r.error_message, r.duration_bucket))
    return rows


def _case_identity(rec: dict[str, str]) -> str:
    name = rec.get("useCaseName", "N/A")
    if name != "N/A":
        return _normalize_key_name(name)
    source = rec.get("sourceFile", "")
    first = source.split("|", 1)[0].strip()
    if first:
        return _normalize_key_name(Path(first).stem)
    return ""


def _merge_same_case_records(records: list[dict[str, str]]) -> list[dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for rec in records:
        cid = _case_identity(rec)
        if not cid:
            cid = f"auto-{len(merged)}"
        current = merged.get(cid)
        if current is None:
            merged[cid] = dict(rec)
            continue
        for k, v in rec.items():
            old = current.get(k, "N/A")
            if k == "sourceFile":
                old_set = {x.strip() for x in old.split("|") if x.strip() and x.strip() != "N/A"}
                new_set = {x.strip() for x in v.split("|") if x.strip() and x.strip() != "N/A"}
                combined = sorted(old_set | new_set)
                current[k] = " | ".join(combined) if combined else "N/A"
            elif old == "N/A" and v != "N/A":
                current[k] = v
            elif old != "N/A" and v != "N/A" and old != v and k in {
                "keyEvidence", "fixAction", "fixConclusion", "rerunConclusion", "caseErrorMessage"
            }:
                parts = [p.strip() for p in (old + " | " + v).split("|") if p.strip()]
                current[k] = " | ".join(dict.fromkeys(parts))
    return list(merged.values())


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def _numbered(values: list[str]) -> str:
    if not values:
        return "N/A"
    return "<br>".join(f"{i}. {v}" for i, v in enumerate(values, 1))


def _join_unique(values: list[str]) -> str:
    return "<br>".join(values) if values else "N/A"


def _column_header(column: str, locale: dict[str, str]) -> str:
    column = _resolve_column(column) or column
    mapping = {
        "category": ("category", "Issue Category"),
        "subcategory": ("subcategory", "Issue Subcategory"),
        "rootCause": ("rootCause", "Root Cause"),
        "count": ("count", "Count"),
        "cases": ("cases", "Use Cases"),
        "evidence": ("evidence", "Key Evidence"),
        "fixAction": ("fixAction", "Fix Action"),
        "fixConclusion": ("fixConclusion", "Fix Conclusion"),
        "rerunConclusion": ("rerunConclusion", "Rerun Conclusion"),
        "caseResult": ("executionResult", "Execution Result"),
        "caseErrorMessage": ("executionError", "Error Message"),
        "sources": ("sources", "Source Files"),
    }
    key, fallback = mapping.get(column, (column, column))
    return locale.get(key, fallback)


def _column_value(column: str, row: _Group) -> str:
    column = _resolve_column(column) or column
    if column == "category":
        return row.category
    if column == "subcategory":
        return row.subcategory
    if column == "rootCause":
        return row.rootCause
    if column == "count":
        return str(row.count)
    if column == "cases":
        return _numbered(row.cases)
    if column == "evidence":
        return _numbered(row.evidence)
    if column == "fixAction":
        return _join_unique(row.fix_actions)
    if column == "fixConclusion":
        return _join_unique(row.fix_conclusions)
    if column == "rerunConclusion":
        return _join_unique(row.rerun_conclusions)
    if column == "caseResult":
        return _join_unique(row.case_results)
    if column == "caseErrorMessage":
        return _join_unique(row.case_errors)
    if column == "sources":
        return _join_unique(row.sources)
    return "N/A"


def _build_report(rows: list[_Group], exec_rows: list[_ExecGroup], total_records: int, input_count: int,
                  report_layout: dict[str, Any],
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
    table_columns = report_layout.get("tableColumns")
    if not isinstance(table_columns, list) or not table_columns:
        table_columns = default_report_layout()["tableColumns"]
    headers = [_column_header(c, locale) for c in table_columns]
    aligns = ["---:" if (_resolve_column(c) or c) == "count" else "---" for c in table_columns]
    add("| " + " | ".join(headers) + " |")
    add("|" + "|".join(aligns) + "|")
    for r in rows:
        values = [_column_value(c, r) for c in table_columns]
        add("| " + " | ".join(values) + " |")
    add("")
    exec_title = locale.get("executionCluster", "Case Execution Cluster")
    add(f"## {exec_title}")
    add("")
    exec_result_col = locale.get("executionResult", "Execution Result")
    exec_error_col = locale.get("executionError", "Error Message")
    exec_duration_col = locale.get("executionDurationBucket", "Duration Bucket")
    add(f"| {exec_result_col} | {exec_error_col} | {exec_duration_col} | {locale['count']} | {locale['cases']} |")
    add("|---|---|---|---:|---|")
    for r in exec_rows:
        add(f"| {r.result} | {r.error_message} | {r.duration_bucket} | {r.count} | {_numbered(r.cases)} |")
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
                   exec_rows: list[_ExecGroup], group_by: list[str],
                   report_layout: dict[str, Any],
                   input_files: list[Path], locale_name: str, runtime_name: str) -> Path:
    summary = {
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "totalFiles": len(input_files),
        "totalRecords": len(records),
        "totalGroups": len(rows),
        "executionGroups": len(exec_rows),
        "groupBy": group_by,
        "reportLayout": report_layout,
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

# Search order for auto-discovered config files when CLI path is not provided.
# `.example.json` is intentionally excluded — users must copy & rename to opt in.
_AUTO_CONFIG_DIRS: tuple[Path, ...] = (ASSETS, ROOT / "temp")


def _auto_discover_config(filename: str) -> Path | None:
    """Return the first existing `<dir>/<filename>` in `_AUTO_CONFIG_DIRS`."""
    for d in _AUTO_CONFIG_DIRS:
        candidate = d / filename
        if candidate.exists():
            return candidate
    return None


def analyze(input_files: list[Path], output_dir: Path,
            field_map_path: Path | None = None,
            dimension_rules_path: Path | None = None,
            report_layout_path: Path | None = None,
            locale_name: str = DEFAULT_LOCALE,
            locale_file: Path | None = None,
            runtime_name: str = "python") -> dict[str, Any]:
    if field_map_path is None:
        field_map_path = _auto_discover_config("field-map.json")
    if dimension_rules_path is None:
        dimension_rules_path = _auto_discover_config("dimension-rules.json")
    if report_layout_path is None:
        report_layout_path = _auto_discover_config("report-layout.json")
    field_map = load_field_map(field_map_path)
    group_by = load_group_by(dimension_rules_path)
    known_fields = set(field_map.keys())
    group_by = [g for g in group_by if g in known_fields]
    if not group_by:
        group_by = list(_DEFAULT_GROUP_BY)
    report_layout = load_report_layout(report_layout_path)
    locale = load_locale(locale_name, locale_file)
    alias_table, canonicals = _flatten_alias_table(field_map)
    normalized_alias_table = _build_normalized_alias_table(alias_table)

    resolved = [p.resolve() for p in input_files if p.exists()]
    if not resolved:
        raise FileNotFoundError("No supported input files were found.")

    parsed_by_file: dict[str, dict[str, Any]] = {}
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
        records = [
            _record_from_raw(raw, alias_table, normalized_alias_table, canonicals, source_str)
            for raw in payload
        ]
        parsed_by_file[str(item.resolve())] = {
            "path": item.resolve(),
            "stem": str(item.resolve().with_suffix("")),
            "ext": ext,
            "records": records,
        }

    all_records: list[dict[str, str]] = []
    paired_stems: set[str] = set()
    stems: dict[str, dict[str, dict[str, Any]]] = {}
    for info in parsed_by_file.values():
        stems.setdefault(info["stem"], {})[info["ext"]] = info

    for stem, pair in stems.items():
        json_info = pair.get(".json")
        txt_info = pair.get(".txt")
        # Prefer JSON whenever both exist for the same stem (TXT is treated as
        # a fallback / human-readable view of the same record). This avoids
        # producing N/A rows when TXT parsing is incomplete or formats drift.
        if json_info and txt_info:
            all_records.extend(json_info["records"])
            paired_stems.add(stem)

    for info in parsed_by_file.values():
        if info["stem"] in paired_stems:
            continue
        all_records.extend(info["records"])

    all_records = _merge_same_case_records(all_records)

    if not all_records:
        raise ValueError("No valid records were parsed from input files.")

    rows = _group_records(all_records, group_by)
    exec_rows = _group_execution_info(all_records)
    _ensure_dir(output_dir)
    normalized_path = _write_normalized(output_dir, all_records)
    summary_path = _write_summary(output_dir, all_records, rows, exec_rows, group_by, report_layout, resolved, locale_name, runtime_name)
    report_path = output_dir / "log-analysis-report.md"
    report_path.write_text(
        _build_report(rows, exec_rows, len(all_records), len(resolved), report_layout, locale, locale_name, runtime_name),
        encoding="utf-8",
    )
    return {
        "reportPath": str(report_path),
        "normalizedPath": str(normalized_path),
        "summaryPath": str(summary_path),
        "totalRecords": len(all_records),
        "totalGroups": len(rows),
        "executionGroups": len(exec_rows),
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

    structured_json = fixtures_dir / "structured-single-case.json"
    structured_txt = fixtures_dir / "structured-single-case.txt"
    structured_payload = {
        "case_name": "Auth-Timeout-001",
        "problem_category": "Network",
        "problem_subcategory": "Timeout",
        "root_case_conclusion": "Upstream timeout",
        "key_evidence": [
            {"reference_doc": "gw.log", "log_match": "504 Gateway Timeout"}
        ],
        "fix_action": "Increase timeout to 15s",
        "rerun_result": "PASS",
        "analysis_time": "2026-05-09 10:01:02",
        "version_info": {
            "device_sn": "SN-001",
            "device_type": "edge-gateway",
            "platform_version": "4.0.1",
            "hy_version": "2.3.0"
        },
        "case_execution_info": {
            "case_name": "Auth-Timeout-001",
            "begin_time": "2026-05-09 10:00:00",
            "end_time": "2026-05-09 10:00:12",
            "duration": "12s",
            "result": "FAIL",
            "error_message": "HTTP 504"
        }
    }
    structured_json.write_text(json.dumps(structured_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    structured_txt.write_text(
        "\n".join([
            "case_name: Auth-Timeout-001",
            "problem_category: Network",
            "problem_subcategory: Timeout",
            "root_case_conclusion: Upstream timeout",
            "fix_action: Increase timeout to 15s",
            "rerun_result: PASS",
        ]),
        encoding="utf-8",
    )
    structured_result = analyze(
        [structured_json, structured_txt],
        output_dir / "structured-pair",
        locale_name=locale_name,
        runtime_name="python",
    )
    structured_report = Path(structured_result["reportPath"]).read_text(encoding="utf-8")
    structured_normalized = json.loads(Path(structured_result["normalizedPath"]).read_text(encoding="utf-8"))
    structured_ok = (
        structured_result["totalRecords"] == 1
        and structured_result["executionGroups"] >= 1
        and any(r.get("issueSubcategory") == "Timeout" for r in structured_normalized)
        and "Timeout" in structured_report
        and "504 Gateway Timeout" in structured_report
    )
    record(
        "Structured pair merge",
        structured_ok,
        f"json wins when paired with txt; records={structured_result['totalRecords']}; execution groups={structured_result['executionGroups']}; subcategory captured"
    )

    # New: numbered-section TXT format (用例失败根因分析结果) — TXT alone must
    # produce a complete row without N/A on the key fields.
    numbered_txt = fixtures_dir / "numbered-format-case.txt"
    numbered_txt.write_text(
        "\n".join([
            "用例失败根因分析结果",
            "用例名称: Auth-Numbered-001    分析时间: 2026-05-10 09:00:00",
            "(1)问题大类",
            "Network",
            "(2)问题小类",
            "Timeout",
            "(3)根因诊断结论",
            "Upstream gateway returns 504 under burst load",
            "(4)关键佐证信息",
            "参考文档特征描述: gateway-runbook.md 504 章节",
            "本次日志对应信息: 504 Gateway Timeout @ 10:00:11",
            "(5)问题修复动作",
            "Increase upstream timeout to 15s and add retry",
            "(6)问题修复结论",
            "Fixed in build 4.0.2",
            "(7)问题重跑结论",
            "PASS",
        ]),
        encoding="utf-8",
    )
    numbered_result = analyze(
        [numbered_txt],
        output_dir / "numbered-format",
        locale_name=locale_name,
        runtime_name="python",
    )
    numbered_report = Path(numbered_result["reportPath"]).read_text(encoding="utf-8")
    numbered_normalized = json.loads(Path(numbered_result["normalizedPath"]).read_text(encoding="utf-8"))
    numbered_rec = numbered_normalized[0] if numbered_normalized else {}
    numbered_ok = (
        numbered_result["totalRecords"] == 1
        and numbered_rec.get("issueCategory") == "Network"
        and numbered_rec.get("issueSubcategory") == "Timeout"
        and "Upstream gateway" in numbered_rec.get("rootCauseConclusion", "")
        and "504 Gateway Timeout" in numbered_rec.get("keyEvidence", "")
        and numbered_rec.get("fixAction", "N/A") != "N/A"
        and numbered_rec.get("fixConclusion", "N/A") != "N/A"
        and numbered_rec.get("rerunConclusion", "N/A") != "N/A"
        and "Auth-Numbered-001" in numbered_report
        and "Upstream gateway" in numbered_report
    )
    record(
        "Numbered TXT format (用例失败根因分析结果)",
        numbered_ok,
        "TXT-only numbered-section input produces a complete row, no N/A on category/subcategory/rootCause/evidence/fix/rerun"
    )

    legacy_typo_json = fixtures_dir / "legacy-key-evdence.json"
    legacy_typo_json.write_text(
        json.dumps(
            {
                "case_name": "Legacy-Typo-001",
                "problem_category": "Stability",
                "problem_subcategory": "Memory",
                "root_case_conclusion": "Leak in cache",
                "key_evdence": [{"reference_doc": "heap.log", "log_match": "OOM"}],
                "fix_action": "Patch cache",
                "rerun_result": "PASS",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    legacy_result = analyze(
        [legacy_typo_json],
        output_dir / "legacy-typo",
        locale_name=locale_name,
        runtime_name="python",
    )
    legacy_normalized = json.loads(Path(legacy_result["normalizedPath"]).read_text(encoding="utf-8"))
    legacy_ok = (
        legacy_result["totalRecords"] == 1
        and legacy_normalized
        and "OOM" in legacy_normalized[0].get("keyEvidence", "")
        and legacy_normalized[0].get("issueSubcategory") == "Memory"
    )
    record("Legacy key_evdence typo compat", legacy_ok,
           "legacy spelling still mapped to keyEvidence; problem_subcategory recognized")

    synonym_layout = fixtures_dir / "synonym-report-layout.json"
    synonym_layout.write_text(
        json.dumps(
            {
                "mode": "single-table",
                "allowMultiCaseCells": True,
                "tableColumns": ["problem_category", "problem_subcategory", "执行结果", "用例名称", "key_evidence"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    synonym_result = analyze(
        [structured_json, structured_txt],
        output_dir / "synonym-layout",
        report_layout_path=synonym_layout,
        locale_name=locale_name,
        runtime_name="python",
    )
    synonym_report = Path(synonym_result["reportPath"]).read_text(encoding="utf-8")
    synonym_ok = (
        ("Issue Category" in synonym_report or "问题大类" in synonym_report)
        and ("Issue Subcategory" in synonym_report or "问题小类" in synonym_report)
        and ("Execution Result" in synonym_report or "执行结果" in synonym_report)
    )
    record("Synonym column names", synonym_ok,
           "tableColumns accepts problem_category/执行结果/用例名称/key_evidence aliases")

    # Auto-discovery: drop a temp report-layout.json with only 2 columns and run
    # analyze() with no explicit path; it should be picked up from skill_root/temp.
    auto_dir = skill_root / "temp"
    auto_dir.mkdir(parents=True, exist_ok=True)
    auto_layout = auto_dir / "report-layout.json"
    auto_layout_existed = auto_layout.exists()
    auto_layout_backup = auto_layout.read_bytes() if auto_layout_existed else None
    try:
        auto_layout.write_text(
            json.dumps(
                {
                    "mode": "single-table",
                    "allowMultiCaseCells": True,
                    "tableColumns": ["category", "count"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        auto_result = analyze(
            [fixtures_dir / "sample-10.json"],
            output_dir / "auto-discover",
            locale_name=locale_name,
            runtime_name="python",
        )
        auto_report = Path(auto_result["reportPath"]).read_text(encoding="utf-8")
        # With only category+count columns the rerun-conclusion / sources columns must be absent.
        auto_ok = (
            ("Rerun Conclusion" not in auto_report and "用例重跑结论" not in auto_report)
            and ("Source Files" not in auto_report and "来源文件" not in auto_report)
        )
        record("Auto-discover temp/report-layout.json", auto_ok,
               "analyze() picks up temp/report-layout.json when no --report-layout is passed")
    finally:
        if auto_layout_backup is not None:
            auto_layout.write_bytes(auto_layout_backup)
        elif auto_layout.exists():
            auto_layout.unlink()

    custom_layout = fixtures_dir / "custom-report-layout.json"
    custom_layout.write_text(
        json.dumps(
            {
                "mode": "single-table",
                "allowMultiCaseCells": True,
                "tableColumns": ["category", "rootCause", "count", "caseResult", "cases"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    custom_layout_result = analyze(
        [fixtures_dir / "sample-10.json"],
        output_dir / "custom-layout",
        report_layout_path=custom_layout,
        locale_name=locale_name,
        runtime_name="python",
    )
    custom_layout_report = Path(custom_layout_result["reportPath"]).read_text(encoding="utf-8")
    layout_ok = ("执行结果" in custom_layout_report or "Execution Result" in custom_layout_report) and (
        "来源文件" not in custom_layout_report and "Source Files" not in custom_layout_report
    )
    record("Custom report layout", layout_ok, "Validated configurable report columns via --report-layout")

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
    a.add_argument("--report-layout")
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
            Path(args.report_layout) if args.report_layout else None,
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
