# Summary: phaseB_o3_spine.jsonl

Rows: 120

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openai:o3 | spine_ieven_rodd | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openai:o3 | spine_ieven_rnone | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openai:o3 | spine_iodd_reven | 30 | 30 | 0 | 0 | 1.000 | [0.886, 1.000] | 1.000 | 0 |
| openai:o3 | spine_inone_rnone | 30 | 6 | 24 | 0 | 0.200 | [0.095, 0.373] | 1.000 | 0 |

## Value histogram (top 5 per model x condition)

- **openai:o3 / spine_ieven_rodd**: 42x17, 2x11, 24x1, 64x1
- **openai:o3 / spine_ieven_rnone**: 42x28, 24x1, 64x1
- **openai:o3 / spine_iodd_reven**: 37x8, 7x7, 1x5, 57x3, 47x2
- **openai:o3 / spine_inone_rnone**: 42x24, 57x3, 37x3
