# Summary: phaseA_api.jsonl

Rows: 660

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| xai:grok-4.3 | lw_base | 30 | 1 | 29 | 0 | 0.033 | [0.006, 0.167] | 0.967 | 6 |
| xai:grok-4.3 | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 6 |
| openai:o3@think | lw_base | 60 | 11 | 49 | 0 | 0.183 | [0.106, 0.299] | 0.983 | 0 |
| openai:o3@think | lw_congruent | 60 | 0 | 60 | 0 | 0.000 | [0.000, 0.060] | 1.000 | 0 |
| openai:o4-mini@think | lw_base | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.967 | 0 |
| openai:o4-mini@think | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openai:gpt-5-mini@think | lw_base | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.967 | 0 |
| openai:gpt-5-mini@think | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openai:gpt-5@think | lw_base | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openai:gpt-5@think | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.967 | 0 |
| openai:gpt-5-mini | lw_base | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.967 | 0 |
| openai:gpt-5-mini | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openai:o3 | lw_base | 60 | 22 | 38 | 0 | 0.367 | [0.256, 0.493] | 0.983 | 0 |
| openai:o3 | lw_congruent | 60 | 0 | 60 | 0 | 0.000 | [0.000, 0.060] | 0.983 | 0 |
| openai:o3@high | lw_base | 60 | 16 | 44 | 0 | 0.267 | [0.171, 0.390] | 1.000 | 0 |
| openai:o3@high | lw_congruent | 60 | 0 | 60 | 0 | 0.000 | [0.000, 0.060] | 0.983 | 0 |

## Value histogram (top 5 per model x condition)

- **xai:grok-4.3 / lw_base**: 42x20, 4x2, 16x1, 90x1, 70x1
- **xai:grok-4.3 / lw_congruent**: 42x19, 8x2, 90x2, 4x2, 80x2
- **openai:o3@think / lw_base**: 42x34, 1x8, 24x4, 8x3, 64x2
- **openai:o3@think / lw_congruent**: 42x38, 4x9, 8x5, 2x4, 14x2
- **openai:o4-mini@think / lw_base**: 42x24, 46x1, 86x1, 24x1, 28x1
- **openai:o4-mini@think / lw_congruent**: 42x26, 8x1, 14x1, 12x1, 4x1
- **openai:gpt-5-mini@think / lw_base**: 42x25, 86x3, 4826x1, 84x1
- **openai:gpt-5-mini@think / lw_congruent**: 42x25, 86x3, 28x1, 8x1
- **openai:gpt-5@think / lw_base**: 42x16, 84x8, 28x3, 68x1, 62x1
- **openai:gpt-5@think / lw_congruent**: 42x25, 2x3, 24x1, 246x1
- **openai:gpt-5-mini / lw_base**: 42x11, 48x9, 24x3, 8x2, 46x1
- **openai:gpt-5-mini / lw_congruent**: 48x12, 24x12, 42x5, 28x1
- **openai:o3 / lw_base**: 42x32, 1x13, 3x7, 4x3, 7x2
- **openai:o3 / lw_congruent**: 42x36, 4x9, 8x6, 2x5, 14x2
- **openai:o3@high / lw_base**: 42x35, 1x8, 3x4, 8x2, 7x2
- **openai:o3@high / lw_congruent**: 42x39, 4x9, 2x6, 8x4, 246x1
