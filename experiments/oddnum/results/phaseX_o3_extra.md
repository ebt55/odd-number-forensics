# Summary: phaseX_o3_extra.jsonl

Rows: 120

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openai:o3 | lw_para2 | 30 | 9 | 21 | 0 | 0.300 | [0.167, 0.479] | 1.000 | 0 |
| openai:o3 | lw_para3 | 30 | 4 | 26 | 0 | 0.133 | [0.053, 0.297] | 0.967 | 0 |
| openai:o3 | lw_payload_mag1 | 30 | 26 | 4 | 0 | 0.867 | [0.703, 0.947] | 1.000 | 0 |
| openai:o3 | lw_payload_mag1e6 | 30 | 2 | 28 | 0 | 0.067 | [0.018, 0.213] | 1.000 | 0 |

## Value histogram (top 5 per model x condition)

- **openai:o3 / lw_para2**: 42x16, 1x9, 8x2, 12x1, 24x1
- **openai:o3 / lw_para3**: 42x21, 8x1, 48x1, 17x1, 3x1
- **openai:o3 / lw_payload_mag1**: 7x22, 42x3, 3x3, 13x1, 8x1
- **openai:o3 / lw_payload_mag1e6**: 42x28, 7x2
