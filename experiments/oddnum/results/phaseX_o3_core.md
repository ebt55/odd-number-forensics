# Summary: phaseX_o3_core.jsonl

Rows: 300

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openai:o3 | lw_applies | 60 | 39 | 21 | 0 | 0.650 | [0.524, 0.758] | 1.000 | 0 |
| openai:o3 | lw_inert | 60 | 1 | 59 | 0 | 0.017 | [0.003, 0.089] | 0.983 | 0 |
| openai:o3 | lw_priority | 60 | 1 | 59 | 0 | 0.017 | [0.003, 0.089] | 1.000 | 0 |
| openai:o3 | lw_mirror_conflict | 60 | 14 | 46 | 0 | 0.233 | [0.144, 0.354] | 1.000 | 0 |
| openai:o3 | lw_mirror_congruent | 60 | 60 | 0 | 0 | 1.000 | [0.940, 1.000] | 1.000 | 0 |

## Value histogram (top 5 per model x condition)

- **openai:o3 / lw_applies**: 1x34, 42x14, 3x3, 4x3, 8x2
- **openai:o3 / lw_inert**: 42x47, 68x5, 64x2, 24x2, 3x1
- **openai:o3 / lw_priority**: 42x45, 24x5, 8x3, 4x2, 1x1
- **openai:o3 / lw_mirror_conflict**: 2x22, 42x12, 7x8, 4x8, 17x4
- **openai:o3 / lw_mirror_congruent**: 7x42, 1x10, 17x2, 37x2, 47x1
