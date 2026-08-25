# Summary: phaseD_deepseek_probes.jsonl

Rows: 45

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openrouter:deepseek/deepseek-v4-flash | lw_articulate | 15 | 1 | 14 | 0 | 0.067 | [0.012, 0.298] | 1.000 | 0 |
| openrouter:deepseek/deepseek-v4-flash | probe_judgment_lw | 15 | 0 | 15 | 0 | 0.000 | [0.000, 0.204] | 0.933 | 15 |
| openrouter:deepseek/deepseek-v4-flash | probe_prediction_lw | 15 | 0 | 15 | 0 | 0.000 | [0.000, 0.204] | 1.000 | 14 |

## Value histogram (top 5 per model x condition)

- **openrouter:deepseek/deepseek-v4-flash / lw_articulate**: 42x9, 2x3, 4x2, 1x1
- **openrouter:deepseek/deepseek-v4-flash / probe_judgment_lw**: 4x7, 2x5, 14x1, 42x1, 0x1
- **openrouter:deepseek/deepseek-v4-flash / probe_prediction_lw**: 42x8, 2x4, 4x2, 8x1
