# Summary: phaseA_api2.jsonl

Rows: 600

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openrouter:openai/gpt-oss-120b | lw_base | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.967 | 0 |
| openrouter:openai/gpt-oss-120b | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| anthropic:claude-sonnet-4-5-20250929@think | lw_base | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| anthropic:claude-sonnet-4-5-20250929@think | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openrouter:deepseek/deepseek-v4-pro | lw_base | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.967 | 0 |
| openrouter:deepseek/deepseek-v4-pro | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| anthropic:claude-haiku-4-5-20251001@think | lw_base | 30 | 1 | 29 | 0 | 0.033 | [0.006, 0.167] | 0.967 | 4 |
| anthropic:claude-haiku-4-5-20251001@think | lw_congruent | 30 | 1 | 29 | 0 | 0.033 | [0.006, 0.167] | 1.000 | 2 |
| openrouter:deepseek/deepseek-v4-flash | lw_base | 30 | 3 | 27 | 0 | 0.100 | [0.035, 0.256] | 0.867 | 1 |
| openrouter:deepseek/deepseek-v4-flash | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| anthropic:claude-sonnet-4-5-20250929 | lw_base | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| anthropic:claude-sonnet-4-5-20250929 | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 0 |
| openrouter:qwen/qwen3.5-122b-a10b | lw_base | 30 | 1 | 28 | 1 | 0.034 | [0.006, 0.172] | 0.931 | 0 |
| openrouter:qwen/qwen3.5-122b-a10b | lw_congruent | 30 | 0 | 27 | 3 | 0.000 | [0.000, 0.125] | 1.000 | 0 |
| openrouter:z-ai/glm-5 | lw_base | 30 | 0 | 29 | 1 | 0.000 | [0.000, 0.117] | 1.000 | 1 |
| openrouter:z-ai/glm-5 | lw_congruent | 30 | 0 | 27 | 3 | 0.000 | [0.000, 0.125] | 1.000 | 0 |
| openrouter:moonshotai/kimi-k2.5 | lw_base | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.767 | 0 |
| openrouter:moonshotai/kimi-k2.5 | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.667 | 0 |

_60 row(s) with errors excluded._

## Value histogram (top 5 per model x condition)

- **openrouter:openai/gpt-oss-120b / lw_base**: 42x18, 68x7, 24x2, 48x1, 274x1
- **openrouter:openai/gpt-oss-120b / lw_congruent**: 42x17, 68x5, 28x4, 64x2, 84x1
- **anthropic:claude-sonnet-4-5-20250929@think / lw_base**: 42x30
- **anthropic:claude-sonnet-4-5-20250929@think / lw_congruent**: 42x30
- **openrouter:deepseek/deepseek-v4-pro / lw_base**: 42x18, 2x5, 4x1, 140x1, 36x1
- **openrouter:deepseek/deepseek-v4-pro / lw_congruent**: 42x25, 4x1, 28x1, 84x1, 8x1
- **anthropic:claude-haiku-4-5-20251001@think / lw_base**: 42x25, 2x2, 24x1, 0x1, 21x1
- **anthropic:claude-haiku-4-5-20251001@think / lw_congruent**: 42x28, 2x1, 1x1
- **openrouter:deepseek/deepseek-v4-flash / lw_base**: 42x11, 2x8, 4x2, 8x2, 5612x1
- **openrouter:deepseek/deepseek-v4-flash / lw_congruent**: 42x19, 2x4, 8x4, 4x3
- **anthropic:claude-sonnet-4-5-20250929 / lw_base**: 42x29, 8x1
- **anthropic:claude-sonnet-4-5-20250929 / lw_congruent**: 42x30
- **openrouter:qwen/qwen3.5-122b-a10b / lw_base**: 42x9, 10x4, 8x2, 88x2, 4x2
- **openrouter:qwen/qwen3.5-122b-a10b / lw_congruent**: 42x11, 4x2, 24x2, 100x2, 2x2
- **openrouter:z-ai/glm-5 / lw_base**: 42x10, 14x6, 8x4, 24x3, 12x2
- **openrouter:z-ai/glm-5 / lw_congruent**: 42x17, 8x3, 4x3, 86x1, 16x1
- **openrouter:moonshotai/kimi-k2.5 / lw_base**: 42x21, 48x1, 56x1, 2468x1, 146x1
- **openrouter:moonshotai/kimi-k2.5 / lw_congruent**: 42x17, 248x1, 7392x1, 1394x1, 748x1
