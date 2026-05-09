"""Benchmark v1 (log-analysis-pipeline) vs v2 (log-analysis-pipeline-v2).

Generates fixtures of multiple sizes, runs each implementation N times against
identical inputs, records min/avg/max wall time, and writes a Markdown
comparison report at `reports/benchmark.md`.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import statistics
import sys
import time
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = V2_ROOT.parent
V1_ROOT = SKILLS_DIR / "log-analysis-pipeline"

SIZES = (200, 1000, 2000, 5000)
ITERATIONS = 5
WORK_DIR = V2_ROOT / "reports" / ".bench"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _ensure_fixtures(core_v2, fixtures_dir: Path) -> None:
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    core_v2.generate_fixtures(fixtures_dir, sizes=SIZES)


def _run_once(analyze_fn, json_file: Path, txt_file: Path, out_dir: Path) -> float:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    started = time.perf_counter()
    analyze_fn([json_file, txt_file], out_dir, locale_name="en-US", runtime_name="python")
    return (time.perf_counter() - started) * 1000.0


def _measure(label: str, analyze_fn, json_file: Path, txt_file: Path, base_out: Path) -> dict:
    samples: list[float] = []
    # Warm-up
    _run_once(analyze_fn, json_file, txt_file, base_out / f"warmup-{label}")
    for i in range(ITERATIONS):
        ms = _run_once(analyze_fn, json_file, txt_file, base_out / f"{label}-{i}")
        samples.append(ms)
    return {
        "min": round(min(samples), 2),
        "avg": round(statistics.mean(samples), 2),
        "max": round(max(samples), 2),
        "samples": [round(s, 2) for s in samples],
    }


def main() -> int:
    if not V1_ROOT.exists():
        raise FileNotFoundError(f"v1 not found at {V1_ROOT}")
    core_v1 = _load_module("v1_core", V1_ROOT / "scripts" / "log_analysis_core.py")
    core_v2 = _load_module("v2_core", V2_ROOT / "scripts" / "log_analysis_core_v2.py")

    fixtures_dir = V2_ROOT / "tests" / "fixtures"
    _ensure_fixtures(core_v2, fixtures_dir)

    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    print(f"Iterations per size: {ITERATIONS}")
    print(f"{'size':>6} | {'v1 min/avg ms':>16} | {'v2 min/avg ms':>16} | {'speedup (avg)':>14}")
    print("-" * 70)
    for size in SIZES:
        json_file = fixtures_dir / f"sample-{size}.json"
        txt_file = fixtures_dir / f"sample-{size}.txt"
        v1 = _measure(f"v1-{size}", core_v1.analyze, json_file, txt_file, WORK_DIR / "v1")
        v2 = _measure(f"v2-{size}", core_v2.analyze, json_file, txt_file, WORK_DIR / "v2")
        speedup = round(v1["avg"] / v2["avg"], 2) if v2["avg"] > 0 else float("inf")
        rows.append({"size": size, "v1": v1, "v2": v2, "speedup": speedup})
        print(f"{size:>6} | {v1['min']:>6}/{v1['avg']:>7} | {v2['min']:>6}/{v2['avg']:>7} | {speedup:>14}x")

    all_v2_better = all(r["v2"]["avg"] < r["v1"]["avg"] for r in rows)
    verdict = "v2 wins on every size" if all_v2_better else "v2 NOT yet uniformly faster"

    md = ["# Performance Comparison: v1 vs v2", ""]
    md.append(f"- Iterations per size (after warm-up): **{ITERATIONS}**")
    md.append(f"- Sizes: {', '.join(str(s) for s in SIZES)} records (each runs against JSON + TXT pair)")
    md.append(f"- v1 root: `{V1_ROOT}`")
    md.append(f"- v2 root: `{V2_ROOT}`")
    md.append(f"- Verdict: **{verdict}**")
    md.append("")
    md.append("## Wall time (ms)")
    md.append("")
    md.append("| Size | v1 min | v1 avg | v1 max | v2 min | v2 avg | v2 max | Speedup (avg) |")
    md.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        md.append(
            f"| {r['size']} | {r['v1']['min']} | {r['v1']['avg']} | {r['v1']['max']} | "
            f"{r['v2']['min']} | {r['v2']['avg']} | {r['v2']['max']} | {r['speedup']}x |"
        )
    md.append("")
    md.append("## Raw samples (ms)")
    md.append("")
    md.append("| Size | v1 samples | v2 samples |")
    md.append("|---:|---|---|")
    for r in rows:
        md.append(f"| {r['size']} | {r['v1']['samples']} | {r['v2']['samples']} |")
    md.append("")

    out = V2_ROOT / "reports" / "benchmark.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md), encoding="utf-8")
    json_out = V2_ROOT / "reports" / "benchmark.json"
    json_out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")
    print(f"Wrote {json_out}")
    print(f"Verdict: {verdict}")
    return 0 if all_v2_better else 1


if __name__ == "__main__":
    sys.exit(main())
