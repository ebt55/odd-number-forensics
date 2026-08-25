# Why Do Models Output Odd Numbers When Asked for Even Ones?

A forensic investigation of the Odd Number reward-hacking environment
([source](https://www.lesswrong.com/posts/LhXW8ziwnn7Dd8edm/a-toy-environment-for-exploring-reasoning-about-reward)):
a model is asked for a random even number while leaked grader metadata rewards odd ones.
~5,300 audited samples across 35 model-arms and 34 conditions.

**Read [REPORT.md](REPORT.md)** — executive summary at the top. Headline: the behavior is
score-seeking task reinterpretation gated by two prompt conditions (credible applicability ×
pragmatic ambiguity); production models from five vendors game at 57–92% when both gates are
open, and one-sentence edits collapse it to ≈0.

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
