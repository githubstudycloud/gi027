# log-analysis-pipeline

A cross-platform skill for aggregating JSON/TXT log-analysis files into a single Markdown report.

## What it does
- Parses log-analysis files from multiple paths
- Groups cases by issue category, subcategory, and root cause
- Produces a dense Markdown table with multi-case cells
- Supports locale-aware output through JSON locale packs
- Generates 10 / 20 / 200 record fixtures for performance testing

## How to run
- Windows: use `scripts/run-skill-tests.ps1` or `scripts/analyze-logs.ps1`
- Linux / macOS: use `scripts/run-skill.sh`
- Node.js: use `npm test` or `npm run analyze`
- Python: use `scripts/run-skill-tests.py` or `scripts/analyze-logs.py`

## Files to know
- `SKILL.md` — skill behavior and workflow
- `scripts/log_analysis_core.py` — portable analysis and test engine
- `assets/locales/` — language packs
- `assets/runtime-config.example.json` — runtime selection example
- `reports/test-report.md` — generated test report

## Output
- `reports/output/log-analysis-report.md`
- `reports/output/normalized-records.json`
- `reports/output/summary.json`

## Beginner tips
- Start with one JSON and one TXT fixture first.
- If fields do not map, update `assets/field-map.example.json`.
- If report text is wrong for your language, switch locale in config.
