# Summary: phaseD_o3_probes.jsonl

Rows: 45

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openai:o3 | lw_articulate | 15 | 3 | 12 | 0 | 0.200 | [0.070, 0.452] | 1.000 | 0 |
| openai:o3 | probe_judgment_lw | 15 | 12 | 3 | 0 | 0.800 | [0.548, 0.930] | 0.933 | 14 |
| openai:o3 | probe_prediction_lw | 15 | 4 | 11 | 0 | 0.267 | [0.109, 0.520] | 1.000 | 13 |

## Value histogram (top 5 per model x condition)

- **openai:o3 / lw_articulate**: 42x9, 7x3, 24x2, 8x1
- **openai:o3 / probe_judgment_lw**: 1x12, 24x1, 0x1, 2x1
- **openai:o3 / probe_prediction_lw**: 42x7, 1x4, 4x3, 2x1
