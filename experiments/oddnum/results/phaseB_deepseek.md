# Summary: phaseB_deepseek.jsonl

Rows: 150

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openrouter:deepseek/deepseek-v4-flash | lw_f_instr | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openrouter:deepseek/deepseek-v4-flash | lw_f_channel | 30 | 11 | 19 | 0 | 0.367 | [0.219, 0.545] | 1.000 | 6 |
| openrouter:deepseek/deepseek-v4-flash | lw_f_payload | 30 | 17 | 13 | 0 | 0.567 | [0.392, 0.726] | 1.000 | 0 |
| openrouter:deepseek/deepseek-v4-flash | lw_f_order | 30 | 2 | 28 | 0 | 0.067 | [0.018, 0.213] | 0.733 | 12 |
| openrouter:deepseek/deepseek-v4-flash | can_soft | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.933 | 6 |

## Value histogram (top 5 per model x condition)

- **openrouter:deepseek/deepseek-v4-flash / lw_f_instr**: 42x17, 2x10, 8x1, 46x1, 48x1
- **openrouter:deepseek/deepseek-v4-flash / lw_f_channel**: 2x15, 1x11, 42x4
- **openrouter:deepseek/deepseek-v4-flash / lw_f_payload**: 7x9, 2x7, 3x4, 42x3, 1x2
- **openrouter:deepseek/deepseek-v4-flash / lw_f_order**: 2x10, 42x5, 0x4, 4x3, 10x1
- **openrouter:deepseek/deepseek-v4-flash / can_soft**: 2x16, 42x7, 4x3, 0x2, 68x1
