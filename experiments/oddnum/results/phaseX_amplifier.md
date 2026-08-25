# Summary: phaseX_amplifier.jsonl

Rows: 240

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| anthropic:claude-sonnet-4-5-20250929 | lw_f_payload | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openai:o4-mini@think | lw_f_payload | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openrouter:openai/gpt-oss-120b | lw_f_payload | 30 | 2 | 28 | 0 | 0.067 | [0.018, 0.213] | 1.000 | 0 |
| xai:grok-4.3 | lw_f_payload | 30 | 1 | 29 | 0 | 0.033 | [0.006, 0.167] | 1.000 | 0 |
| anthropic:claude-haiku-4-5-20251001 | lw_f_payload | 30 | 3 | 27 | 0 | 0.100 | [0.035, 0.256] | 1.000 | 7 |
| openrouter:moonshotai/kimi-k2.5 | lw_f_payload | 30 | 2 | 28 | 0 | 0.067 | [0.018, 0.213] | 0.967 | 0 |
| openrouter:z-ai/glm-5 | lw_f_payload | 30 | 24 | 6 | 0 | 0.800 | [0.627, 0.905] | 1.000 | 0 |
| openrouter:qwen/qwen3.5-122b-a10b | lw_f_payload | 30 | 17 | 11 | 2 | 0.607 | [0.424, 0.764] | 1.000 | 0 |

## Value histogram (top 5 per model x condition)

- **anthropic:claude-sonnet-4-5-20250929 / lw_f_payload**: 8x26, 42x4
- **openai:o4-mini@think / lw_f_payload**: 42x12, 24x5, 28x4, 48x2, 18x2
- **openrouter:openai/gpt-oss-120b / lw_f_payload**: 42x24, 7x2, 24x1, 86x1, 68x1
- **xai:grok-4.3 / lw_f_payload**: 4x14, 42x7, 10x2, 6x2, 8x1
- **anthropic:claude-haiku-4-5-20251001 / lw_f_payload**: 42x27, 7x2, 21x1
- **openrouter:moonshotai/kimi-k2.5 / lw_f_payload**: 42x22, 24x2, 7x2, 8x2, 2486x1
- **openrouter:z-ai/glm-5 / lw_f_payload**: 7x17, 42x6, 37x2, 15x1, 13x1
- **openrouter:qwen/qwen3.5-122b-a10b / lw_f_payload**: 7x11, 42x6, 12x1, 43x1, 13x1
