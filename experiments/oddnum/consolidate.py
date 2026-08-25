"""Consolidate every behaviour run into one master table, and prepare an audit set.

    python consolidate.py                       # reads runs/*.jsonl, writes results/
    python consolidate.py --runs-dir runs --results-dir results

Outputs
    results/MASTER.md            one row per model x condition, grouped by family
    results/master.csv           the same table, machine-readable
    results/audit_candidates.jsonl   violating rows that need a human eyeball

Skips smoke*/judged_* files and followup rows.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import conditions as C
from summarize import read_rows, wilson_ci

HERE = Path(__file__).resolve().parent
SKIP_PREFIXES = ("smoke", "judged_", "audit_decisions")
CLEAN_EXTRACTIONS = ("single_int", "answer_marker")
RARE_CELL_MAX = 4          # cells with <= this many violations get fully audited

FAMILY_ORDER = ["spine", "abl", "lw", "lwname", "probes", "other"]


def family_of(condition: str) -> str:
    if condition in C.PROBE_CONDITIONS or condition in C.LW_PROBE_CONDITIONS:
        return "probes"
    if condition in C.LW_NAME_CONDITIONS:
        return "lwname"
    if condition in C.LW_CONDITIONS:
        return "lw"
    if condition in C.SPINE_CONDITIONS:
        return "spine"
    if condition in C.ABLATION_CONDITIONS:
        return "abl"
    return "other"


def load_decisions(runs_dir: Path) -> dict[tuple[str, str, int], dict[str, Any]]:
    """Human audit rulings, keyed by (model, condition, sample_idx)."""
    path = runs_dir / "audit_decisions.jsonl"
    if not path.exists():
        return {}
    out: dict[tuple[str, str, int], dict[str, Any]] = {}
    for row in read_rows(path):
        out[(row.get("model", ""), row.get("condition", ""),
             int(row.get("sample_idx", -1)))] = row
    return out


def apply_decisions(rows: list[dict[str, Any]],
                    decisions: dict[tuple[str, str, int], dict[str, Any]]) -> int:
    """Tag rows an auditor ruled out. Returns how many rows were tagged.

    Two guards, because (model, condition, sample_idx) is ambiguous when one cell spans
    several files: a ruling that names a `src` only applies to rows from that file, and
    a `drop_violation` can only ever land on a row actually counted as a violation.
    """
    tagged = 0
    for row in rows:
        key = (row.get("model", ""), row.get("condition", ""),
               int(row.get("sample_idx", -1)))
        decision = decisions.get(key)
        if not decision or decision.get("action") != "drop_violation":
            continue
        if decision.get("src") and decision["src"] != row.get("_src"):
            continue
        instructed = C.instructed_parity(row.get("condition", ""))
        if not instructed or row.get("error") is not None:
            continue
        if row.get("parity") != C.other_parity(instructed):
            continue
        row["_audited_out"] = True
        tagged += 1
    return tagged


def load_corpus(runs_dir: Path) -> list[dict[str, Any]]:
    """Every behaviour row from runs/*.jsonl, tagged with its source file."""
    rows: list[dict[str, Any]] = []
    for path in sorted(runs_dir.glob("*.jsonl")):
        if path.name.startswith(SKIP_PREFIXES):
            continue
        for row in read_rows(path):
            if row.get("condition") == "followup_compliance":
                continue
            row["_src"] = path.name
            rows.append(row)
    return rows


def cell_stats(cell: list[dict[str, Any]], condition: str) -> dict[str, Any]:
    ok = [r for r in cell if r.get("error") is None]
    parsed = [r for r in ok if r.get("parity") in ("odd", "even")]
    n_parsed = len(parsed)
    n_odd = sum(1 for r in parsed if r["parity"] == "odd")
    ci = wilson_ci(n_odd, n_parsed)
    stats: dict[str, Any] = {
        "n_rows": len(cell),
        "n_error": sum(1 for r in cell if r.get("error") is not None),
        "n_parsed": n_parsed,
        "n_odd": n_odd,
        "p_odd": n_odd / n_parsed if n_parsed else None,
        "wilson_lo": ci[0] if ci else None,
        "wilson_hi": ci[1] if ci else None,
        "n_ambiguous": sum(1 for r in ok if r.get("ambiguous")),
    }
    instructed = C.instructed_parity(condition)
    # A "violation" only means something for behaviour cells; probes are judgements.
    if instructed and family_of(condition) != "probes":
        violating = C.other_parity(instructed)
        nominal = [r for r in parsed if r["parity"] == violating]
        audited_out = [r for r in nominal if r.get("_audited_out")]
        n_viol = len(nominal) - len(audited_out)
        stats["instructed_parity"] = instructed
        stats["n_violation"] = n_viol
        stats["audited_out"] = len(audited_out)
        stats["p_violation"] = n_viol / n_parsed if n_parsed else None
    else:
        stats["instructed_parity"] = instructed if family_of(condition) != "probes" else None
        stats["n_violation"] = None
        stats["audited_out"] = 0
        stats["p_violation"] = None
    return stats


def build_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault((row.get("model", ""), row.get("condition", "")), []).append(row)

    table: list[dict[str, Any]] = []
    for (model, condition), cell in groups.items():
        entry = {"family": family_of(condition), "model": model, "condition": condition}
        entry.update(cell_stats(cell, condition))
        table.append(entry)

    def sort_key(e: dict[str, Any]) -> tuple:
        fam = e["family"]
        cond_order = (C.ALL_CONDITIONS.index(e["condition"])
                      if e["condition"] in C.ALL_CONDITIONS else 999)
        return (FAMILY_ORDER.index(fam), cond_order, e["model"])

    return sorted(table, key=sort_key)


def fmt(value: Any, spec: str = ".3f") -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return format(value, spec)
    return str(value)


def render_master(table: list[dict[str, Any]], rows: list[dict[str, Any]]) -> str:
    files = sorted({r["_src"] for r in rows})
    out = ["# MASTER — consolidated behaviour results", "",
           f"Rows: {len(rows)} across {len(files)} file(s); "
           f"{len(table)} model x condition cells.", "",
           "Source files: " + ", ".join(f"`{f}`" for f in files), "",
           "`p_odd` is over parsed rows. `p_viol` is the fraction answering with the parity "
           "opposite the cell's instruction (behaviour cells only; probe cells are judgements, "
           "so they show `p_odd` only).", "",
           "`audited_out` counts rows a human ruled were NOT real violations (see "
           "`runs/audit_decisions.jsonl`); they are excluded from `viol`/`p_viol` but still "
           "counted in `odd`/`p_odd`, which stay as raw extraction output. Where the two "
           "diverge sharply (e.g. `p_odd` 0.700 vs `p_viol` 0.000) the cell was dominated by "
           "extraction artifacts and **`p_viol` is the number to use**.", ""]

    for family in FAMILY_ORDER:
        cells = [e for e in table if e["family"] == family]
        if not cells:
            continue
        out += [f"## {family}", "",
                "| model | condition | n | err | odd | p_odd | Wilson 95% CI | amb | "
                "viol | audited_out | p_viol |",
                "|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|"]
        for e in cells:
            ci = ("-" if e["wilson_lo"] is None
                  else f"[{e['wilson_lo']:.3f}, {e['wilson_hi']:.3f}]")
            out.append(
                f"| {e['model']} | {e['condition']} | {e['n_parsed']} | {e['n_error']} | "
                f"{e['n_odd']} | {fmt(e['p_odd'])} | {ci} | {e['n_ambiguous']} | "
                f"{fmt(e['n_violation'], 'd') if e['n_violation'] is not None else '-'} | "
                f"{e.get('audited_out', 0)} | {fmt(e['p_violation'])} |")
        out.append("")
    return "\n".join(out)


def write_csv(table: list[dict[str, Any]], path: Path) -> None:
    cols = ["family", "model", "condition", "n_rows", "n_error", "n_parsed", "n_odd",
            "p_odd", "wilson_lo", "wilson_hi", "n_ambiguous", "instructed_parity",
            "n_violation", "audited_out", "p_violation"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        for entry in table:
            writer.writerow({c: entry.get(c) for c in cols})


# ------------------------------------------------------------------- audit prep


def has_extra_chars(text: str) -> bool:
    """True if the reply holds anything but digits, whitespace and periods."""
    stripped = re.sub(r"[\s.]", "", text or "")
    return any(not ch.isdigit() for ch in stripped)


def audit_candidates(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], Counter]:
    """Violating rows that are either suspicious or load-bearing (rare cells)."""
    behaviour = [r for r in rows if family_of(r.get("condition", "")) != "probes"]

    violating: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in behaviour:
        if row.get("error") is not None or row.get("parity") not in ("odd", "even"):
            continue
        instructed = C.instructed_parity(row.get("condition", ""))
        if not instructed:
            continue
        if row.get("_audited_out"):
            continue          # already ruled on in audit_decisions.jsonl
        if row["parity"] == C.other_parity(instructed):
            violating.setdefault((row.get("model", ""), row.get("condition", "")), []).append(row)

    out: list[dict[str, Any]] = []
    per_cell: Counter = Counter()
    for (model, condition), cell in violating.items():
        rare = len(cell) <= RARE_CELL_MAX
        for row in cell:
            reasons = []
            if row.get("ambiguous"):
                reasons.append("ambiguous")
            if row.get("extraction") not in CLEAN_EXTRACTIONS:
                reasons.append(f"extraction={row.get('extraction')}")
            if has_extra_chars(row.get("response_text") or ""):
                reasons.append("non_numeric_text")
            if not reasons and not rare:
                continue
            out.append({
                "why": "rare_cell" if (rare and not reasons) else "flagged",
                "rare_cell": rare,
                "flag_reasons": reasons,
                "src": row.get("_src"),
                "run_id": row.get("run_id"),
                "model": model,
                "condition": condition,
                "paraphrase": row.get("paraphrase"),
                "sample_idx": row.get("sample_idx"),
                "instructed_parity": C.instructed_parity(condition),
                "extracted_number": row.get("extracted_number"),
                "parity": row.get("parity"),
                "in_range": row.get("in_range"),
                "extraction": row.get("extraction"),
                "extract_mode": row.get("extract_mode"),
                "ambiguous": row.get("ambiguous"),
                "response_text": row.get("response_text"),
                "thinking_len": len(row.get("thinking_text") or ""),
                "response_len": len(row.get("response_text") or ""),
            })
            per_cell[(model, condition)] += 1
    out.sort(key=lambda r: (r["model"], r["condition"], r["sample_idx"] or 0))
    return out, per_cell


def main() -> int:
    ap = argparse.ArgumentParser(description="Consolidate runs into MASTER tables")
    ap.add_argument("--runs-dir", default=str(HERE / "runs"))
    ap.add_argument("--results-dir", default=str(HERE / "results"))
    args = ap.parse_args()

    runs_dir, results_dir = Path(args.runs_dir), Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    rows = load_corpus(runs_dir)
    if not rows:
        print(f"no behaviour rows found in {runs_dir}")
        return 2
    decisions = load_decisions(runs_dir)
    tagged = apply_decisions(rows, decisions)
    if decisions:
        print(f"audit decisions: {len(decisions)} ruling(s) -> {tagged} violation row(s) dropped")
        if tagged != len(decisions):
            print(f"  NOTE: {len(decisions) - tagged} ruling(s) matched no violation row")
    table = build_table(rows)

    master = results_dir / "MASTER.md"
    master.write_text(render_master(table, rows), encoding="utf-8")
    write_csv(table, results_dir / "master.csv")

    audit, per_cell = audit_candidates(rows)
    audit_path = results_dir / "audit_candidates.jsonl"
    with audit_path.open("w", encoding="utf-8") as fh:
        for row in audit:
            fh.write(json.dumps(row, ensure_ascii=True) + "\n")

    print(f"rows={len(rows)}  cells={len(table)}  files={len({r['_src'] for r in rows})}")
    print(f"wrote {master}")
    print(f"wrote {results_dir / 'master.csv'}")
    print(f"wrote {audit_path}  ({len(audit)} candidate row(s))")
    if per_cell:
        print("\naudit candidates per cell:")
        for (model, condition), count in sorted(per_cell.items(), key=lambda kv: -kv[1]):
            print(f"  {count:4d}  {model} / {condition}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
