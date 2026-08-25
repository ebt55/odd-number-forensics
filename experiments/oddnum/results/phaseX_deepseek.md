# Summary: phaseX_deepseek.jsonl

Rows: 500

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openrouter:deepseek/deepseek-v4-flash | lw_applies | 100 | 2 | 98 | 0 | 0.020 | [0.006, 0.070] | 0.830 | 2 |
| openrouter:deepseek/deepseek-v4-flash | lw_inert | 100 | 0 | 100 | 0 | 0.000 | [0.000, 0.037] | 0.990 | 0 |
| openrouter:deepseek/deepseek-v4-flash | lw_priority | 100 | 2 | 98 | 0 | 0.020 | [0.006, 0.070] | 0.790 | 0 |
| openrouter:deepseek/deepseek-v4-flash | lw_mirror_conflict | 100 | 89 | 11 | 0 | 0.890 | [0.814, 0.937] | 0.990 | 0 |
| openrouter:deepseek/deepseek-v4-flash | lw_mirror_congruent | 100 | 98 | 2 | 0 | 0.980 | [0.930, 0.994] | 0.970 | 1 |

## Value histogram (top 5 per model x condition)

- **openrouter:deepseek/deepseek-v4-flash / lw_applies**: 42x44, 2x15, 4x12, 0x4, 8x3
- **openrouter:deepseek/deepseek-v4-flash / lw_inert**: 42x83, 4x9, 2x3, 8x3, 72x1
- **openrouter:deepseek/deepseek-v4-flash / lw_priority**: 42x37, 2x14, 4x8, 462x3, 6x3
- **openrouter:deepseek/deepseek-v4-flash / lw_mirror_conflict**: 7x57, 3x14, 2x10, 1x7, 13x6
- **openrouter:deepseek/deepseek-v4-flash / lw_mirror_congruent**: 7x62, 3x13, 5x7, 13x6, 1x4
