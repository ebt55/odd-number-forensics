# Why Do Models Output Odd Numbers When Asked for Even Ones?

A forensic take-apart of the Odd Number reward-hacking environment
([source](https://www.lesswrong.com/posts/LhXW8ziwnn7Dd8edm/a-toy-environment-for-exploring-reasoning-about-reward)).
A model is asked for a random even number, and leaked grader metadata rewards odd ones.
We replicated the environment exactly, edited it one line at a time, and ran about 5,300
audited samples across 35 model-arms and 34 conditions.

The one finding: one model, o3, moves from under 2% to 87% gaming across one-line prompt
edits, at 30 to 60 samples per cell. A rate quoted for "the Odd Number environment" means
little without the exact string.

The bounds: cells of 30 to 100 samples, enough only for large effects. No correction for
multiple comparisons. o3 hides its chain of thought. Only one amplifier family was tested.
This was a practice work sample for the SPAR Fall 2026 take-home.

Read [REPORT.md](REPORT.md). The executive summary and key findings are at the top.

## Layout

- `REPORT.md` — the full write-up.
- `experiments/oddnum/` — harness (`run.py`, `conditions.py --selfcheck`, `summarize.py`,
  `contrasts.py`, `judge.py`, `consolidate.py`, `fig.py`), specs and preregistration
  (`SPEC.md`, `PREREG.md`), raw data (`runs/*.jsonl` — every sample, full request/response),
  audit rulings (`runs/audit_decisions.jsonl`), and generated tables/figures (`results/`).
- `submission/` — PDF/DOCX of the report.

## Reproduce

Every number in the report regenerates mechanically:

```bash
cd experiments/oddnum
python conditions.py --selfcheck   # byte-exact prompt verification
python consolidate.py              # rebuilds results/MASTER.md from runs/ + audit file
```

Re-running the experiments themselves needs API keys in a repo-root `.env`
(`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, `XAI_API_KEY`); model
snapshots are recorded per-row where providers expose them.

## Credits

Ebin Babu Thomas — investigation conducted with Claude Fable 5 (orchestration and analysis)
and Claude Opus 5 (implementation agents). SPAR Model Forensics take-home, August 2026.
