# Summary: phaseX_threshold.jsonl

Rows: 60

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openai:gpt-5-mini@think | lw_f_payload | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openrouter:deepseek/deepseek-v4-pro | lw_f_payload | 30 | 21 | 9 | 0 | 0.700 | [0.521, 0.833] | 1.000 | 0 |

## Value histogram (top 5 per model x condition)

- **openai:gpt-5-mini@think / lw_f_payload**: 42x22, 86x4, 28x1, 48x1, 8x1
- **openrouter:deepseek/deepseek-v4-pro / lw_f_payload**: 7x17, 42x8, 3x2, 17x1, 73x1
