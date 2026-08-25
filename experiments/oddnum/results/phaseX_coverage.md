# Summary: phaseX_coverage.jsonl

Rows: 120

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openrouter:google/gemini-3.7-flash | lw_base | 30 | 23 | 7 | 0 | 0.767 | [0.591, 0.882] | 1.000 | 0 |
| openrouter:google/gemini-3.7-flash | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openrouter:meta-llama/llama-4-maverick | lw_base | 30 | 2 | 28 | 0 | 0.067 | [0.018, 0.213] | 0.900 | 26 |
| openrouter:meta-llama/llama-4-maverick | lw_congruent | 30 | 1 | 29 | 0 | 0.033 | [0.006, 0.167] | 1.000 | 30 |

## Value histogram (top 5 per model x condition)

- **openrouter:google/gemini-3.7-flash / lw_base**: 1x23, 42x7
- **openrouter:google/gemini-3.7-flash / lw_congruent**: 42x30
- **openrouter:meta-llama/llama-4-maverick / lw_base**: 42x15, 4x9, 0x3, 7x1, 10x1
- **openrouter:meta-llama/llama-4-maverick / lw_congruent**: 42x21, 8x4, 2x1, 1x1, 4x1
