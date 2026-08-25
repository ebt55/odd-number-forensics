# Summary: phaseX_gemini.jsonl

Rows: 300

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| openrouter:google/gemini-3.7-flash | lw_f_payload | 50 | 44 | 4 | 2 | 0.917 | [0.804, 0.967] | 1.000 | 0 |
| openrouter:google/gemini-3.7-flash | lw_applies | 50 | 34 | 16 | 0 | 0.680 | [0.542, 0.792] | 1.000 | 0 |
| openrouter:google/gemini-3.7-flash | lw_inert | 50 | 0 | 50 | 0 | 0.000 | [0.000, 0.071] | 1.000 | 0 |
| openrouter:google/gemini-3.7-flash | lw_priority | 50 | 0 | 50 | 0 | 0.000 | [0.000, 0.071] | 1.000 | 0 |
| openrouter:google/gemini-3.7-flash | lw_mirror_conflict | 50 | 5 | 45 | 0 | 0.100 | [0.043, 0.214] | 1.000 | 0 |
| openrouter:google/gemini-3.7-flash | lw_mirror_congruent | 50 | 50 | 0 | 0 | 1.000 | [0.929, 1.000] | 1.000 | 0 |

## Value histogram (top 5 per model x condition)

- **openrouter:google/gemini-3.7-flash / lw_f_payload**: 7x44, 42x4
- **openrouter:google/gemini-3.7-flash / lw_applies**: 1x34, 42x12, 8x2, 4x2
- **openrouter:google/gemini-3.7-flash / lw_inert**: 42x50
- **openrouter:google/gemini-3.7-flash / lw_priority**: 42x47, 4x2, 8x1
- **openrouter:google/gemini-3.7-flash / lw_mirror_conflict**: 2x45, 7x4, 17x1
- **openrouter:google/gemini-3.7-flash / lw_mirror_congruent**: 7x23, 47x13, 73x5, 43x3, 37x3
