"""Two-proportion comparison between two cells of a run.

    python contrasts.py runs/pilot.jsonl --model ollama:qwen3:14b \
        --a spine_ieven_rodd --b spine_ieven_rnone [--outcome odd|violation]
    python contrasts.py runs/pilot.jsonl --all-models --a abl_applies --b abl_inert

Outcomes are counted over PARSED rows only (rows where a number was extracted).
`violation` scores parity against the parity the cell's instruction asked for.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import conditions as C
from summarize import read_rows, wilson_ci

Z = 1.959963985  # 95%


def normal_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def two_proportion_z(x1: int, n1: int, x2: int, n2: int) -> tuple[float, float]:
    """Pooled two-proportion z test; returns (z, two-sided p)."""
    if n1 == 0 or n2 == 0:
        return 0.0, 1.0
    pooled = (x1 + x2) / (n1 + n2)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    if se == 0:
        return 0.0, 1.0
    z = (x1 / n1 - x2 / n2) / se
    return z, 2.0 * (1.0 - normal_cdf(abs(z)))


def newcombe_diff_ci(x1: int, n1: int, x2: int, n2: int) -> tuple[float, float] | None:
    """Newcombe hybrid-score 95% CI for p1 - p2 (his method 10)."""
    if n1 == 0 or n2 == 0:
        return None
    ci1, ci2 = wilson_ci(x1, n1, Z), wilson_ci(x2, n2, Z)
    if ci1 is None or ci2 is None:
        return None
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = ci1
    l2, u2 = ci2
    lower = (p1 - p2) - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    upper = (p1 - p2) + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return max(-1.0, lower), min(1.0, upper)


def cell_rows(rows: list[dict[str, Any]], model: str, condition: str) -> list[dict[str, Any]]:
    return [r for r in rows
            if r.get("model") == model and r.get("condition") == condition
            and r.get("error") is None and r.get("parity") in ("odd", "even")]


def count_outcome(cell: list[dict[str, Any]], outcome: str,
                  condition: str) -> tuple[int, int, str]:
    """Return (successes, n_parsed, label). Raises for an undefined violation cell."""
    n = len(cell)
    if outcome == "odd":
        return sum(1 for r in cell if r.get("parity") == "odd"), n, "P(odd)"
    source = cell[0].get("source_condition") if cell and cell[0].get("source_condition") else condition
    instructed = C.instructed_parity(source)
    if instructed is None:
        raise ValueError(
            f"--outcome violation is undefined for {condition!r}: its instruction asks for "
            f"no particular parity. Use --outcome odd for that cell.")
    violating = C.other_parity(instructed)
    hits = sum(1 for r in cell if r.get("parity") == violating)
    return hits, n, f"P(violation: {violating} vs instructed {instructed})"


def report(rows: list[dict[str, Any]], model: str, cond_a: str, cond_b: str,
           outcome: str) -> None:
    a_rows, b_rows = cell_rows(rows, model, cond_a), cell_rows(rows, model, cond_b)
    print(f"\n=== {model} ===")
    if not a_rows or not b_rows:
        print(f"  skipped: parsed rows A={len(a_rows)} B={len(b_rows)} (need both non-empty)")
        return

    x1, n1, label = count_outcome(a_rows, outcome, cond_a)
    x2, n2, _ = count_outcome(b_rows, outcome, cond_b)
    p1, p2 = x1 / n1, x2 / n2
    ci1, ci2 = wilson_ci(x1, n1, Z), wilson_ci(x2, n2, Z)
    diff_ci = newcombe_diff_ci(x1, n1, x2, n2)
    z, pval = two_proportion_z(x1, n1, x2, n2)

    print(f"  outcome: {label}")
    print(f"  A  {cond_a:<22} n={n1:<4} k={x1:<4} p={p1:.3f}  "
          f"Wilson [{ci1[0]:.3f}, {ci1[1]:.3f}]")
    print(f"  B  {cond_b:<22} n={n2:<4} k={x2:<4} p={p2:.3f}  "
          f"Wilson [{ci2[0]:.3f}, {ci2[1]:.3f}]")
    diff_txt = f"[{diff_ci[0]:.3f}, {diff_ci[1]:.3f}]" if diff_ci else "-"
    print(f"  risk difference (A - B): {p1 - p2:+.3f}  Newcombe 95% CI {diff_txt}")
    print(f"  two-proportion z = {z:+.3f}, p = {pval:.4f}"
          f"{'  (significant at 0.05)' if pval < 0.05 else ''}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Two-proportion contrast between two cells")
    ap.add_argument("src", help="path to runs/*.jsonl")
    ap.add_argument("--model", help="model spec to compare")
    ap.add_argument("--all-models", action="store_true", help="every model in the file")
    ap.add_argument("--a", required=True, help="condition A")
    ap.add_argument("--b", required=True, help="condition B")
    ap.add_argument("--outcome", choices=["odd", "violation"], default="odd")
    args = ap.parse_args()

    if not args.model and not args.all_models:
        print("need --model <spec> or --all-models")
        return 2

    src = Path(args.src)
    if not src.is_absolute():
        src = Path.cwd() / src
    if not src.exists():
        print(f"not found: {src}")
        return 2

    rows = read_rows(src)
    if args.all_models:
        models: list[str] = []
        for r in rows:
            if r.get("model") and r["model"] not in models:
                models.append(r["model"])
    else:
        models = [args.model]

    print(f"source: {src.name}   contrast: {args.a} vs {args.b}   outcome: {args.outcome}")
    for model in models:
        try:
            report(rows, model, args.a, args.b, args.outcome)
        except ValueError as exc:
            print(f"\n=== {model} ===\n  error: {exc}")
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
