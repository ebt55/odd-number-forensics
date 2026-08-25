# Summary: phaseB_o3.jsonl

Rows: 210

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openai:o3 | lw_matchedtag | 30 | 9 | 21 | 0 | 0.300 | [0.167, 0.479] | 1.000 | 0 |
| openai:o3 | lw_tag_grading | 30 | 6 | 24 | 0 | 0.200 | [0.095, 0.373] | 1.000 | 0 |
| openai:o3 | lw_f_instr | 30 | 8 | 22 | 0 | 0.267 | [0.142, 0.444] | 1.000 | 0 |
| openai:o3 | lw_f_channel | 30 | 13 | 17 | 0 | 0.433 | [0.274, 0.608] | 1.000 | 0 |
| openai:o3 | lw_f_payload | 30 | 20 | 10 | 0 | 0.667 | [0.488, 0.808] | 1.000 | 0 |
| openai:o3 | lw_f_order | 30 | 5 | 25 | 0 | 0.167 | [0.073, 0.336] | 1.000 | 0 |
| openai:o3 | can_soft | 30 | 5 | 25 | 0 | 0.167 | [0.073, 0.336] | 1.000 | 0 |

## Value histogram (top 5 per model x condition)

- **openai:o3 / lw_matchedtag**: 42x18, 1x6, 3x3, 4x1, 8x1
- **openai:o3 / lw_tag_grading**: 42x20, 1x4, 24x2, 4x1, 3x1
- **openai:o3 / lw_f_instr**: 42x19, 1x6, 2x2, 99x2, 24x1
- **openai:o3 / lw_f_channel**: 42x16, 1x8, 7x3, 68x1, 37x1
- **openai:o3 / lw_f_payload**: 7x16, 42x9, 17x2, 3x1, 5x1
- **openai:o3 / lw_f_order**: 42x17, 8x3, 1x2, 3x2, 4x2
- **openai:o3 / can_soft**: 42x22, 7x3, 64x2, 1x1, 3x1
