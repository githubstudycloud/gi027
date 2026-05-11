"""Render a styled HTML report from a log-analysis Markdown report.

The Markdown grammar accepted here is intentionally narrow — it matches what
``log_analysis_core_v2.py`` (and the sibling ``log-analyzer`` skill) emits:

* ``# Title``                                           -> H1
* ``## Section``                                        -> H2 with anchor + TOC entry
* ``- key: value`` or ``- bullet``                      -> definition list / bullet list
* ``| a | b | c |`` followed by ``|---|---|---:|``      -> table (sticky header)
* ``<br>`` inside table cells                           -> kept verbatim

The renderer is dependency-free so the skill stays portable (Claude Code,
OpenCode, GitHub Copilot, plain ``python``…).

CLI:
    python scripts/report_html.py --input <report.md> --output <report.html>

Library:
    from report_html import convert_file, markdown_to_html
    convert_file(Path("report.md"), Path("report.html"), title="...")
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import time
from pathlib import Path

__all__ = ["markdown_to_html", "convert_file", "main"]

_SLUG_STRIP_RE = re.compile(r"[^\w\u4e00-\u9fff\- ]+", re.UNICODE)
_BR_TOKEN = "\u0001BR\u0001"  # private-use placeholder to survive escaping
_RESULT_BADGE_RE = re.compile(r"^(PASS|FAIL|ERROR|SKIP|N/A|通过|失败|错误)$")
_BUCKET_BADGE_RE = re.compile(r"^(<1s|1-5s|5-30s|>=30s|N/A)$")


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = _SLUG_STRIP_RE.sub("", text)
    text = text.replace(" ", "-")
    return text or "section"


def _escape_cell(text: str) -> str:
    # Preserve <br> tags, escape everything else.
    safe = text.replace("<br>", _BR_TOKEN).replace("<br/>", _BR_TOKEN).replace("<br />", _BR_TOKEN)
    safe = html.escape(safe, quote=False)
    return safe.replace(_BR_TOKEN, "<br>")


def _badge(text: str) -> str:
    plain = text.strip()
    if _RESULT_BADGE_RE.match(plain):
        cls = "pass" if plain in {"PASS", "通过"} else (
            "fail" if plain in {"FAIL", "ERROR", "失败", "错误"} else "muted"
        )
        return f'<span class="badge badge-{cls}">{html.escape(plain)}</span>'
    if _BUCKET_BADGE_RE.match(plain):
        return f'<span class="badge badge-bucket">{html.escape(plain)}</span>'
    return _escape_cell(text)


def _render_cell(text: str, *, is_count_col: bool) -> str:
    stripped = text.strip()
    if is_count_col and stripped.isdigit():
        return f'<span class="num">{stripped}</span>'
    # Apply badge styling only on tight single tokens (no <br>, no spaces).
    if "<br>" not in stripped and " " not in stripped and stripped:
        return _badge(stripped)
    return _escape_cell(text)


def _parse_table(rows: list[str]) -> tuple[list[str], list[str], list[list[str]]]:
    """Return (headers, aligns, body_rows)."""
    def split_row(line: str) -> list[str]:
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        return [c.strip() for c in line.split("|")]

    headers = split_row(rows[0])
    aligns_raw = split_row(rows[1]) if len(rows) > 1 else []
    aligns: list[str] = []
    for a in aligns_raw:
        a = a.strip()
        if a.startswith(":") and a.endswith(":"):
            aligns.append("center")
        elif a.endswith(":"):
            aligns.append("right")
        else:
            aligns.append("left")
    while len(aligns) < len(headers):
        aligns.append("left")
    body = [split_row(r) for r in rows[2:]]
    return headers, aligns, body


def _render_table(rows: list[str]) -> str:
    headers, aligns, body = _parse_table(rows)
    count_idx = {i for i, h in enumerate(headers) if h.lower() in {"count", "数量"}}
    out: list[str] = ['<div class="table-wrap"><table>']
    out.append("<thead><tr>")
    for h, a in zip(headers, aligns):
        out.append(f'<th class="align-{a}">{html.escape(h)}</th>')
    out.append("</tr></thead><tbody>")
    for r in body:
        if not any(c.strip() for c in r):
            continue
        out.append("<tr>")
        for i, cell in enumerate(r):
            align = aligns[i] if i < len(aligns) else "left"
            rendered = _render_cell(cell, is_count_col=i in count_idx)
            out.append(f'<td class="align-{align}">{rendered}</td>')
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def _render_bullet(line: str) -> str:
    # `- key: value` -> definition style; otherwise plain bullet.
    body = line[2:].strip() if line.startswith("- ") else line.strip()
    if ": " in body:
        key, _, value = body.partition(": ")
        return f'<li><span class="bk">{html.escape(key)}</span><span class="bv">{html.escape(value)}</span></li>'
    return f"<li>{html.escape(body)}</li>"


_CSS = """\
:root {
  color-scheme: light dark;
  --bg: #fafbfc;
  --fg: #1f2328;
  --muted: #6e7781;
  --border: #d0d7de;
  --card: #ffffff;
  --accent: #0969da;
  --accent-soft: #ddf4ff;
  --row-alt: #f6f8fa;
  --pass-bg: #dafbe1; --pass-fg: #116329;
  --fail-bg: #ffebe9; --fail-fg: #82071e;
  --muted-bg: #eaeef2; --muted-fg: #57606a;
  --bucket-bg: #fff8c5; --bucket-fg: #7d4e00;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0d1117; --fg: #e6edf3; --muted: #8b949e;
    --border: #30363d; --card: #161b22; --accent: #58a6ff;
    --accent-soft: #1f3147; --row-alt: #161b22;
    --pass-bg: #033a16; --pass-fg: #56d364;
    --fail-bg: #4c1010; --fail-fg: #ff7b72;
    --muted-bg: #21262d; --muted-fg: #8b949e;
    --bucket-bg: #4d3800; --bucket-fg: #d4a72c;
  }
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg);
  font: 14px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue",
  "PingFang SC", "Microsoft YaHei", Arial, sans-serif; }
.page { display: grid; grid-template-columns: 260px minmax(0, 1fr);
  gap: 24px; max-width: 1500px; margin: 0 auto; padding: 24px; }
nav.toc { position: sticky; top: 16px; align-self: start;
  background: var(--card); border: 1px solid var(--border); border-radius: 8px;
  padding: 16px; max-height: calc(100vh - 32px); overflow: auto; font-size: 13px; }
nav.toc h2 { margin: 0 0 8px; font-size: 12px; text-transform: uppercase;
  letter-spacing: .04em; color: var(--muted); border: 0; padding: 0; }
nav.toc ol { margin: 0; padding-left: 18px; }
nav.toc li { margin: 4px 0; }
nav.toc a { color: var(--fg); text-decoration: none; }
nav.toc a:hover { color: var(--accent); }
main { min-width: 0; }
main h1 { font-size: 22px; margin: 0 0 4px; }
main h2 { font-size: 17px; margin: 28px 0 12px;
  padding-bottom: 6px; border-bottom: 1px solid var(--border); scroll-margin-top: 16px; }
main h2 a.anchor { color: var(--muted); text-decoration: none; margin-right: 6px;
  font-weight: normal; opacity: 0; transition: opacity .15s; }
main h2:hover a.anchor { opacity: 1; }
.meta { display: flex; flex-wrap: wrap; gap: 8px 14px; color: var(--muted); margin: 0 0 18px; }
.meta .chip { background: var(--card); border: 1px solid var(--border);
  border-radius: 999px; padding: 2px 10px; font-size: 12px; }
.meta .chip b { color: var(--fg); margin-right: 4px; }
ul.bullets { list-style: none; padding: 0; margin: 0 0 8px;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 6px 16px; }
ul.bullets li { background: var(--card); border: 1px solid var(--border);
  border-radius: 6px; padding: 6px 10px; display: flex; gap: 8px; align-items: baseline; }
ul.bullets .bk { color: var(--muted); font-size: 12px; }
ul.bullets .bv { color: var(--fg); font-weight: 500; }
.table-wrap { overflow-x: auto; border: 1px solid var(--border);
  border-radius: 8px; background: var(--card); margin: 0 0 16px; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
thead th { position: sticky; top: 0; background: var(--accent-soft); color: var(--fg);
  text-align: left; font-weight: 600; padding: 8px 10px;
  border-bottom: 1px solid var(--border); white-space: nowrap; }
tbody td { padding: 8px 10px; border-bottom: 1px solid var(--border);
  vertical-align: top; word-break: break-word; max-width: 360px; }
tbody tr:nth-child(even) td { background: var(--row-alt); }
tbody tr:hover td { background: var(--accent-soft); }
td.align-right, th.align-right { text-align: right; }
td.align-center, th.align-center { text-align: center; }
.num { font-variant-numeric: tabular-nums; font-weight: 600; }
.badge { display: inline-block; padding: 1px 8px; border-radius: 999px;
  font-size: 12px; font-weight: 600; line-height: 1.6; }
.badge-pass { background: var(--pass-bg); color: var(--pass-fg); }
.badge-fail { background: var(--fail-bg); color: var(--fail-fg); }
.badge-muted { background: var(--muted-bg); color: var(--muted-fg); }
.badge-bucket { background: var(--bucket-bg); color: var(--bucket-fg);
  font-variant-numeric: tabular-nums; }
@media (max-width: 900px) {
  .page { grid-template-columns: 1fr; }
  nav.toc { position: static; max-height: none; }
}
"""


def markdown_to_html(md_text: str, *, title: str | None = None) -> str:
    """Convert our subset of Markdown to a styled standalone HTML document."""
    lines = md_text.splitlines()
    body: list[str] = []
    toc: list[tuple[str, str]] = []  # (slug, text)
    meta_chips: list[tuple[str, str]] = []  # (key, value) from top-level bullets under H1
    bullet_buf: list[str] = []
    table_buf: list[str] = []
    h1_text: str | None = None
    seen_first_h2 = False

    def flush_bullets() -> None:
        if not bullet_buf:
            return
        body.append("<ul class='bullets'>")
        for ln in bullet_buf:
            body.append(_render_bullet(ln))
        body.append("</ul>")
        bullet_buf.clear()

    def flush_table() -> None:
        if not table_buf:
            return
        body.append(_render_table(table_buf))
        table_buf.clear()

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush_bullets()
            flush_table()
            continue
        if line.startswith("# "):
            flush_bullets(); flush_table()
            h1_text = line[2:].strip()
            continue
        if line.startswith("## "):
            flush_bullets(); flush_table()
            seen_first_h2 = True
            text = line[3:].strip()
            slug = _slugify(text)
            toc.append((slug, text))
            body.append(
                f'<h2 id="{slug}"><a class="anchor" href="#{slug}" aria-hidden="true">#</a>{html.escape(text)}</h2>'
            )
            continue
        if line.startswith("|"):
            flush_bullets()
            table_buf.append(line)
            continue
        if line.startswith("- "):
            flush_table()
            # Bullets before the first H2 become header chips (compact summary).
            if not seen_first_h2:
                body_text = line[2:].strip()
                if ": " in body_text:
                    k, _, v = body_text.partition(": ")
                    meta_chips.append((k.strip(), v.strip()))
                    continue
            bullet_buf.append(line)
            continue
        # Fallback: plain paragraph line.
        flush_bullets(); flush_table()
        body.append(f"<p>{html.escape(line)}</p>")

    flush_bullets()
    flush_table()

    doc_title = title or h1_text or "Log Analysis Report"
    meta_chips.append(("Generated", time.strftime("%Y-%m-%d %H:%M:%S")))

    chips_html = "".join(
        f'<span class="chip"><b>{html.escape(k)}:</b>{html.escape(v)}</span>'
        for k, v in meta_chips
    )
    toc_html = "".join(
        f'<li><a href="#{slug}">{html.escape(text)}</a></li>' for slug, text in toc
    )

    return (
        "<!doctype html>\n<html lang='zh-CN'><head><meta charset='utf-8'>"
        f"<title>{html.escape(doc_title)}</title>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<style>{_CSS}</style></head><body>"
        "<div class='page'>"
        f"<nav class='toc'><h2>Contents</h2><ol>{toc_html}</ol></nav>"
        f"<main><h1>{html.escape(h1_text or doc_title)}</h1>"
        f"<div class='meta'>{chips_html}</div>"
        + "".join(body)
        + "</main></div></body></html>\n"
    )


def convert_file(md_path: Path, html_path: Path, *, title: str | None = None) -> Path:
    md_text = md_path.read_text(encoding="utf-8")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(markdown_to_html(md_text, title=title), encoding="utf-8")
    return html_path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Render a styled HTML report from a log-analysis Markdown report.")
    p.add_argument("--input", required=True, type=Path,
                   help="Path to log-analysis-report.md")
    p.add_argument("--output", type=Path, default=None,
                   help="Path to write the HTML (default: <input-stem>.html alongside input)")
    p.add_argument("--title", default=None,
                   help="Override the <title> tag (default: first H1 from the Markdown)")
    args = p.parse_args(argv)
    in_path: Path = args.input
    if not in_path.exists():
        print(f"input not found: {in_path}", file=sys.stderr)
        return 2
    out_path: Path = args.output or in_path.with_suffix(".html")
    convert_file(in_path, out_path, title=args.title)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
