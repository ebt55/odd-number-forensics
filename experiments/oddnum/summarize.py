"""Summarize a runs/*.jsonl file: parity rates per model x condition + value histograms.

    python summarize.py runs/pilot.jsonl [--out results/pilot.md]
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import conditions as C

HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE / "results"

Z = 1.959963985  # 95%


def wilson_ci(successes: int, total: int, z: float = Z) -> tuple[float, float] | None:
    """Wilson score interval for a binomial proportion."""
    if total == 0:
        return None
    p = successes / total
    denom = 1.0 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def read_rows(path: Path) -> list[dict[str, Any]]:
    """Read a jsonl file, skipping malformed lines (a file may be mid-append)."""
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def condition_sort_key(condition: str) -> tuple[int, str]:
    order = C.ALL_CONDITIONS + ["followup_compliance"]
    return (order.index(condition) if condition in order else len(order), condition)


def summarize(rows: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    """Return (table_lines, histogram_lines) as markdown."""
    ok_rows = [r for r in rows if r.get("error") is None]
    errors = len(rows) - len(ok_rows)

    models: list[str] = []
    for r in ok_rows:
        if r["model"] not in models:
            models.append(r["model"])

    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in ok_rows:
        groups.setdefault((r["model"], r["condition"]), []).append(r)

    table = [
        "| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|---:|",
    ]
    hist: list[str] = []
    keys = sorted(groups, key=lambda k: (models.index(k[0]), condition_sort_key(k[1])))
    for model, condition in keys:
        cell = groups[(model, condition)]
        n = len(cell)
        n_odd = sum(1 for r in cell if r.get("parity") == "odd")
        n_even = sum(1 for r in cell if r.get("parity") == "even")
        n_other = n - n_odd - n_even
        parsed = n_odd + n_even
        p_odd = f"{n_odd / parsed:.3f}" if parsed else "-"
        ci = wilson_ci(n_odd, parsed)
        ci_txt = f"[{ci[0]:.3f}, {ci[1]:.3f}]" if ci else "-"
        in_range = sum(1 for r in cell if r.get("in_range") is True)
        p_range = f"{in_range / parsed:.3f}" if parsed else "-"
        # n_amb = rows where several integers were present and the LAST was taken;
        # worth eyeballing, especially for probe cells where the answer comes first.
        n_amb = sum(1 for r in cell if r.get("ambiguous"))
        table.append(f"| {model} | {condition} | {n} | {n_odd} | {n_even} | {n_other} | "
                     f"{p_odd} | {ci_txt} | {p_range} | {n_amb} |")

        counts = Counter(r["extracted_number"] for r in cell
                         if r.get("extracted_number") is not None)
        top = ", ".join(f"{val}x{cnt}" for val, cnt in counts.most_common(5)) or "(none)"
        hist.append(f"- **{model} / {condition}**: {top}")

    if errors:
        table.append("")
        table.append(f"_{errors} row(s) with errors excluded._")
    return table, hist


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize an oddnum run")
    ap.add_argument("src", help="path to runs/*.jsonl")
    ap.add_argument("--out", help="markdown output path (default results/<stem>.md)")
    args = ap.parse_args()

    src = Path(args.src)
    if not src.is_absolute():
        src = Path.cwd() / src
    if not src.exists():
        print(f"not found: {src}")
        return 2

    rows = read_rows(src)
    table, hist = summarize(rows)

    lines = [f"# Summary: {src.name}", "", f"Rows: {len(rows)}", ""]
    lines += table
    lines += ["", "## Value histogram (top 5 per model x condition)", ""] + hist + [""]
    text = "\n".join(lines)
    print(text)

    out = Path(args.out) if args.out else RESULTS_DIR / (src.stem + ".md")
    if not out.is_absolute():
        out = Path.cwd() / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
