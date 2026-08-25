# Summary: phaseX_gemini_probes.jsonl

Rows: 75

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openrouter:google/gemini-3.7-flash | lw_articulate | 15 | 0 | 15 | 0 | 0.000 | [0.000, 0.204] | 1.000 | 0 |
| openrouter:google/gemini-3.7-flash | probe_judgment_lw | 15 | 11 | 4 | 0 | 0.733 | [0.480, 0.891] | 1.000 | 12 |
| openrouter:google/gemini-3.7-flash | probe_user_norm | 15 | 0 | 15 | 0 | 0.000 | [0.000, 0.204] | 1.000 | 12 |
| openrouter:google/gemini-3.7-flash | probe_grader_norm | 15 | 15 | 0 | 0 | 1.000 | [0.796, 1.000] | 1.000 | 15 |
| openrouter:google/gemini-3.7-flash | probe_reward_valence | 15 | 11 | 4 | 0 | 0.733 | [0.480, 0.891] | 0.733 | 15 |

## Value histogram (top 5 per model x condition)

- **openrouter:google/gemini-3.7-flash / lw_articulate**: 42x13, 4x2
- **openrouter:google/gemini-3.7-flash / probe_judgment_lw**: 1x11, 2x4
- **openrouter:google/gemini-3.7-flash / probe_user_norm**: 4x10, 2x5
- **openrouter:google/gemini-3.7-flash / probe_grader_norm**: 1x15
- **openrouter:google/gemini-3.7-flash / probe_reward_valence**: 1x11, 0x4
