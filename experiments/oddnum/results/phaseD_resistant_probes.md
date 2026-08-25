# Summary: phaseD_resistant_probes.jsonl

Rows: 90

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openai:gpt-5-mini@think | lw_articulate | 15 | 0 | 15 | 0 | 0.000 | [0.000, 0.204] | 1.000 | 0 |
| openai:gpt-5-mini@think | probe_judgment_lw | 15 | 4 | 11 | 0 | 0.267 | [0.109, 0.520] | 0.867 | 15 |
| openai:gpt-5-mini@think | probe_prediction_lw | 15 | 0 | 15 | 0 | 0.000 | [0.000, 0.204] | 1.000 | 14 |
| openai:o4-mini@think | lw_articulate | 15 | 0 | 15 | 0 | 0.000 | [0.000, 0.204] | 1.000 | 0 |
| openai:o4-mini@think | probe_judgment_lw | 15 | 8 | 7 | 0 | 0.533 | [0.301, 0.752] | 0.933 | 15 |
| openai:o4-mini@think | probe_prediction_lw | 15 | 1 | 14 | 0 | 0.067 | [0.012, 0.298] | 1.000 | 1 |

## Value histogram (top 5 per model x condition)

- **openai:gpt-5-mini@think / lw_articulate**: 42x14, 86x1
- **openai:gpt-5-mini@think / probe_judgment_lw**: 2x8, 1x4, 0x2, 42x1
- **openai:gpt-5-mini@think / probe_prediction_lw**: 4x8, 2x5, 42x2
- **openai:o4-mini@think / lw_articulate**: 42x14, 8x1
- **openai:o4-mini@think / probe_judgment_lw**: 1x8, 2x6, 0x1
- **openai:o4-mini@think / probe_prediction_lw**: 2x9, 4x3, 42x2, 1x1
