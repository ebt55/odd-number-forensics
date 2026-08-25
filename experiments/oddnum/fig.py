"""Figures for the odd-number investigation.

    python fig.py                       # all figures into results/figs/
    python fig.py --exclude phaseX_gemini   # skip in-progress run files

Everything is computed from runs/*.jsonl with runs/audit_decisions.jsonl applied at
generation time; no rate is hardcoded. Re-run after new data lands.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

import conditions as C                    # noqa: E402
import consolidate as K                   # noqa: E402
from summarize import wilson_ci           # noqa: E402

HERE = Path(__file__).resolve().parent
FIGS = HERE / "results" / "figs"
DPI = 200

# Okabe-Ito: colourblind-safe.
BLUE, ORANGE, GREEN, VERMILLION = "#0072B2", "#E69F00", "#009E73", "#D55E00"
GREY, DARKGREY = "#BBBBBB", "#444444"
HEAT = LinearSegmentedColormap.from_list("heat", ["#F7F7F7", "#9ECAE1", "#0072B2"])

# f1: the salience/consequence ladder, canonical first then the replication variants.
# Second element is the human-readable tick label - the internal condition id is what
# the code keys on (highlighting, lookups); the label is only ever displayed.
LADDER = [
    ("spine_ieven_rodd", "canonical conflict"),
    ("can_soft", "soft instr + user function"),
    ("lw_f_order", "hint first"),
    ("lw_para3", '"please" paraphrase'),
    ("lw_tag_grading", "<_grading> tag"),
    ("lw_f_instr", "imperative instruction"),
    ("lw_matchedtag", "fixed tag"),
    ("lw_para2", '"pick" paraphrase'),
    ("lw_base", "BASE ENVIRONMENT"),
    ("lw_f_channel", "user-visible function"),
    ("lw_applies", "declared applicable"),
    ("lw_f_payload", "payload spelled out"),
    ("lw_payload_mag1", "payload 1"),
    ("lw_payload_mag1e6", "payload 1,000,000"),
    ("lw_inert", "declared inert"),
    ("lw_priority", "priority clause"),
    ("lw_mirror_conflict", "mirror direction"),
]
CONGRUENT_CELLS = ("lw_congruent", "lw_mirror_congruent")

PROBE_MODELS = ["openai:o3", "openai:o4-mini@think", "openai:gpt-5-mini@think",
                "openrouter:deepseek/deepseek-v4-flash", "openrouter:google/gemini-3.7-flash"]
PROBE_COLS = [
    ("lw_base", "behavior\nlw_base"),
    ("lw_articulate", "articulate\nodd"),
    ("probe_judgment_lw", "judgment\nodd"),
    ("probe_prediction_lw", "prediction\nodd"),
    ("probe_user_norm", "user_norm\nodd"),
    ("probe_grader_norm", "grader_norm\nodd"),
    ("probe_reward_valence", "valence\n'higher'"),
]

WORD_HIGHER = re.compile(r"\bhigher\b")
WORD_LOWER = re.compile(r"\blower\b")


# ---------------------------------------------------------------- data helpers


def load(exclude: list[str]) -> list[dict[str, Any]]:
    rows = [r for r in K.load_corpus(HERE / "runs")
            if not any(x in r["_src"] for x in exclude)]
    K.apply_decisions(rows, K.load_decisions(HERE / "runs"))
    return rows


def cell(rows: list[dict[str, Any]], model: str, condition: str) -> list[dict[str, Any]]:
    return [r for r in rows if r.get("model") == model and r.get("condition") == condition
            and r.get("error") is None]


def violation_rate(rows: list[dict[str, Any]], model: str, condition: str):
    """(k, n, p, lo, hi) of audited violations over parsed rows, or None."""
    parsed = [r for r in cell(rows, model, condition) if r.get("parity") in ("odd", "even")]
    if not parsed:
        return None
    instructed = C.instructed_parity(condition)
    if not instructed:
        return None
    violating = C.other_parity(instructed)
    k = sum(1 for r in parsed
            if r["parity"] == violating and not r.get("_audited_out"))
    n = len(parsed)
    ci = wilson_ci(k, n)
    return k, n, k / n, ci[0], ci[1]


def odd_rate(rows: list[dict[str, Any]], model: str, condition: str):
    parsed = [r for r in cell(rows, model, condition) if r.get("parity") in ("odd", "even")]
    if not parsed:
        return None
    k = sum(1 for r in parsed if r["parity"] == "odd")
    return k, len(parsed), k / len(parsed)


def valence_rate(rows: list[dict[str, Any]], model: str):
    """Fraction saying 'higher' among rows that say higher or lower."""
    got = cell(rows, model, "probe_reward_valence")
    higher = lower = 0
    for r in got:
        head = (r.get("response_text") or "")[:80].lower()
        if WORD_HIGHER.search(head):
            higher += 1
        elif WORD_LOWER.search(head):
            lower += 1
    total = higher + lower
    return (higher, total, higher / total) if total else None


def short(model: str) -> str:
    return model.split(":", 1)[1] if ":" in model else model


# ------------------------------------------------------------------- figure 1


def fig_ladder(rows: list[dict[str, Any]], model: str = "openai:o3") -> Path:
    data = []
    for condition, label in LADDER:
        stat = violation_rate(rows, model, condition)
        if stat:
            k, n, p, lo, hi = stat
            data.append((label, condition, p, lo, hi, n))
    data.sort(key=lambda d: d[2])

    # Congruent controls pooled across both mirror directions.
    ck = cn = 0
    for condition in CONGRUENT_CELLS:
        stat = violation_rate(rows, model, condition)
        if stat:
            ck += stat[0]
            cn += stat[1]
    congruent = ck / cn if cn else None

    # Wide-and-short on purpose: the PNG is placed at text width in the report, so the
    # aspect ratio here is what decides its rendered height on the page - and the hole
    # under the 2.3 heading is only ~4.2in tall, so the whole block has to fit that.
    fig, ax = plt.subplots(figsize=(11.8, 5.95))
    ypos = range(len(data))
    colours = [ORANGE if d[1] == "lw_base" else BLUE for d in data]
    ax.barh(list(ypos), [d[2] for d in data], color=colours, height=0.68, zorder=3)
    ax.errorbar([d[2] for d in data], list(ypos),
                xerr=[[d[2] - d[3] for d in data], [d[4] - d[2] for d in data]],
                fmt="none", ecolor=DARKGREY, elinewidth=1.1, capsize=3, zorder=4)
    for y, d in zip(ypos, data):
        ax.text(d[4] + 0.012, y, f"n={d[5]}", va="center", fontsize=9.5, color=DARKGREY)

    # Room under the lowest bar for the congruent-control readout: when the control sits
    # at 0 its rule hugs the axis, and the label would otherwise land on the top bar.
    ax.set_ylim(-1.4, len(data) - 0.45)
    if congruent is not None:
        ax.axvline(congruent, color=VERMILLION, linestyle="--", linewidth=1.6, zorder=5)
        ax.text(congruent + 0.008, -1.0,
                f"congruent control  {congruent:.3f}  (n={cn})",
                color=VERMILLION, fontsize=10, va="center", ha="left", zorder=6)

    ax.set_yticks(list(ypos))
    ax.set_yticklabels([d[0] for d in data], fontsize=11)
    for tick, d in zip(ax.get_yticklabels(), data):
        if d[1] == "lw_base":
            tick.set_fontweight("bold")
            tick.set_color("#8a5a00")
    ax.tick_params(axis="x", labelsize=10)
    ax.set_xlabel("audited violation rate - answers with the parity the instruction did "
                  "NOT ask for\nWilson 95% CI; audit decisions applied", fontsize=10.5)
    ax.set_title(f"{short(model)} cue ladder - one edit at a time", fontsize=14)
    ax.set_xlim(0, max(0.05, min(1.0, max(d[4] for d in data) + 0.12)))
    ax.grid(axis="x", color=GREY, alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    return save(fig, "f1_ladder.png")


# ------------------------------------------------------------------- figure 2


def fig_whogames(rows: list[dict[str, Any]]) -> Path:
    models = sorted({r["model"] for r in rows
                     if r.get("condition") in ("lw_base", "lw_f_payload")})
    data = []
    for model in models:
        base = violation_rate(rows, model, "lw_base")
        payload = violation_rate(rows, model, "lw_f_payload")
        if base or payload:
            data.append((model, base, payload))
    data.sort(key=lambda d: (d[1][2] if d[1] else -1, d[2][2] if d[2] else -1))

    fig, ax = plt.subplots(figsize=(11, max(5.5, 0.42 * len(data) + 2.2)))
    height = 0.38
    for i, (model, base, payload) in enumerate(data):
        for stat, offset, colour, label in ((base, height / 2, BLUE, "lw_base"),
                                            (payload, -height / 2, GREEN, "lw_f_payload")):
            if not stat:
                continue
            k, n, p, lo, hi = stat
            y = i + offset
            # A zero bar still needs to read as a drawn, measured zero.
            ax.barh(y, p, height=height, color=colour, zorder=3,
                    edgecolor=colour, linewidth=0.8)
            if p == 0:
                ax.plot([0], [y], marker="|", color=colour, markersize=11,
                        markeredgewidth=2.2, zorder=5)
            ax.errorbar(p, y, xerr=[[p - lo], [hi - p]], fmt="none", ecolor=DARKGREY,
                        elinewidth=1.0, capsize=2.5, zorder=4)
            ax.text(hi + 0.012, y, f"{p:.2f} (n={n})", va="center", fontsize=7.4,
                    color=DARKGREY)

    ax.set_yticks(range(len(data)))
    ax.set_yticklabels([short(d[0]) for d in data], fontsize=8.5)
    ax.set_xlabel("audited violation rate")
    ax.set_title("Who games the grader?  lw_base vs lw_f_payload\n"
                 "Wilson 95% CI; a tick at 0 marks a measured zero", fontsize=12)
    ax.set_xlim(0, 1.16)
    ax.grid(axis="x", color=GREY, alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE),
               plt.Rectangle((0, 0), 1, 1, color=GREEN)]
    ax.legend(handles, ["lw_base", "lw_f_payload"], loc="lower right", frameon=False,
              fontsize=9)
    fig.tight_layout()
    return save(fig, "f2_whogames.png")


# ------------------------------------------------------------------- figure 3


def fig_probes(rows: list[dict[str, Any]]) -> Path:
    present = [m for m in PROBE_MODELS
               if any(r.get("model") == m for r in rows)]
    grid, notes = [], []
    for model in present:
        vals, ns = [], []
        for condition, _ in PROBE_COLS:
            if condition == "probe_reward_valence":
                stat = valence_rate(rows, model)
                pct, n = (stat[2], stat[1]) if stat else (None, 0)
            elif condition == "lw_base":
                stat = violation_rate(rows, model, condition)
                pct, n = (stat[2], stat[1]) if stat else (None, 0)
            else:
                stat = odd_rate(rows, model, condition)
                pct, n = (stat[2], stat[1]) if stat else (None, 0)
            vals.append(pct)
            ns.append(n)
        grid.append(vals)
        notes.append(ns)

    fig, ax = plt.subplots(figsize=(10.5, 1.05 * len(present) + 2.6))
    plot = [[v if v is not None else float("nan") for v in row] for row in grid]
    im = ax.imshow(plot, cmap=HEAT, vmin=0, vmax=1, aspect="auto")

    for i, row in enumerate(grid):
        for j, val in enumerate(row):
            if val is None:
                ax.text(j, i, "n/a", ha="center", va="center", fontsize=9, color=GREY)
                continue
            ax.text(j, i, f"{val * 100:.0f}%", ha="center", va="center", fontsize=11,
                    color="white" if val > 0.55 else "#111111", fontweight="bold")
            ax.text(j, i + 0.30, f"n={notes[i][j]}", ha="center", va="center",
                    fontsize=6.8, color="white" if val > 0.55 else DARKGREY)

    ax.set_xticks(range(len(PROBE_COLS)))
    ax.set_xticklabels([lbl for _, lbl in PROBE_COLS], fontsize=8.5)
    ax.set_yticks(range(len(present)))
    ax.set_yticklabels([short(m) for m in present], fontsize=9)
    ax.set_xticks([x - 0.5 for x in range(1, len(PROBE_COLS))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(present))], minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", length=0)
    ax.set_title("Behaviour vs stated norms\n"
                 "'odd' = named an odd number; valence = said a HIGHER reward is better",
                 fontsize=12)
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02).set_label("percentage", fontsize=9)
    fig.tight_layout()
    return save(fig, "f3_probes.png")


def save(fig, name: str) -> Path:
    FIGS.mkdir(parents=True, exist_ok=True)
    path = FIGS / name
    fig.savefig(path, dpi=DPI, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="Render the result figures")
    ap.add_argument("--exclude", default="",
                    help="comma list of substrings; matching run files are skipped")
    ap.add_argument("--ladder-model", default="openai:o3")
    args = ap.parse_args()

    exclude = [x.strip() for x in args.exclude.split(",") if x.strip()]
    rows = load(exclude)
    print(f"loaded {len(rows)} rows"
          + (f" (excluding {exclude})" if exclude else ""))
    for path in (fig_ladder(rows, args.ladder_model),
                 fig_whogames(rows),
                 fig_probes(rows)):
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
