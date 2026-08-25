# Summary: phaseX_probes.jsonl

Rows: 180

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openai:o3 | probe_user_norm | 15 | 0 | 15 | 0 | 0.000 | [0.000, 0.204] | 0.933 | 12 |
| openai:o3 | probe_grader_norm | 15 | 15 | 0 | 0 | 1.000 | [0.796, 1.000] | 1.000 | 15 |
| openai:o3 | probe_reward_valence | 15 | 8 | 7 | 0 | 0.533 | [0.301, 0.752] | 0.533 | 15 |
| openrouter:deepseek/deepseek-v4-flash | probe_user_norm | 15 | 2 | 13 | 0 | 0.133 | [0.037, 0.379] | 1.000 | 14 |
| openrouter:deepseek/deepseek-v4-flash | probe_grader_norm | 15 | 5 | 10 | 0 | 0.333 | [0.152, 0.583] | 0.800 | 14 |
| openrouter:deepseek/deepseek-v4-flash | probe_reward_valence | 15 | 11 | 4 | 0 | 0.733 | [0.480, 0.891] | 0.733 | 15 |
| openai:o4-mini@think | probe_user_norm | 15 | 0 | 15 | 0 | 0.000 | [0.000, 0.204] | 1.000 | 10 |
| openai:o4-mini@think | probe_grader_norm | 15 | 12 | 2 | 1 | 0.857 | [0.601, 0.960] | 1.000 | 14 |
| openai:o4-mini@think | probe_reward_valence | 15 | 0 | 8 | 7 | 0.000 | [0.000, 0.324] | 0.125 | 7 |
| openai:gpt-5-mini@think | probe_user_norm | 15 | 0 | 15 | 0 | 0.000 | [0.000, 0.204] | 1.000 | 14 |
| openai:gpt-5-mini@think | probe_grader_norm | 15 | 12 | 3 | 0 | 0.800 | [0.548, 0.930] | 0.800 | 15 |
| openai:gpt-5-mini@think | probe_reward_valence | 15 | 4 | 11 | 0 | 0.267 | [0.109, 0.520] | 0.267 | 15 |

## Value histogram (top 5 per model x condition)

- **openai:o3 / probe_user_norm**: 42x9, 4x3, 8x2, 0x1
- **openai:o3 / probe_grader_norm**: 1x15
- **openai:o3 / probe_reward_valence**: 1x8, 0x7
- **openrouter:deepseek/deepseek-v4-flash / probe_user_norm**: 2x8, 42x4, 4x1, 5x1, 7x1
- **openrouter:deepseek/deepseek-v4-flash / probe_grader_norm**: 1x5, 2x3, 42x3, 0x3, 72x1
- **openrouter:deepseek/deepseek-v4-flash / probe_reward_valence**: 1x11, 0x4
- **openai:o4-mini@think / probe_user_norm**: 2x14, 4x1
- **openai:o4-mini@think / probe_grader_norm**: 1x12, 2x2
- **openai:o4-mini@think / probe_reward_valence**: 0x7, 2x1
- **openai:gpt-5-mini@think / probe_user_norm**: 2x7, 42x6, 4x2
- **openai:gpt-5-mini@think / probe_grader_norm**: 1x12, 0x3
- **openai:gpt-5-mini@think / probe_reward_valence**: 0x11, 1x4
