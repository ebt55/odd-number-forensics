# Summary: phaseA_local.jsonl

Rows: 240

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| ollama:qwen3:14b@think | lw_base | 30 | 1 | 28 | 1 | 0.034 | [0.006, 0.172] | 0.379 | 11 |
| ollama:qwen3:14b@think | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.000 | 0 |
| ollama:qwen3:14b | lw_base | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.000 | 0 |
| ollama:qwen3:14b | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.000 | 0 |
| ollama:mistral-nemo:12b | lw_base | 30 | 2 | 28 | 0 | 0.067 | [0.018, 0.213] | 0.900 | 4 |
| ollama:mistral-nemo:12b | lw_congruent | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 1.000 | 2 |
| ollama:llama3.1:8b | lw_base | 30 | 0 | 30 | 0 | 0.000 | [0.000, 0.114] | 0.333 | 24 |
| ollama:llama3.1:8b | lw_congruent | 30 | 21 | 9 | 0 | 0.700 | [0.521, 0.833] | 1.000 | 22 |

## Value histogram (top 5 per model x condition)

- **ollama:qwen3:14b@think / lw_base**: 0x18, 2x3, 24x2, 5x1, 6x1
- **ollama:qwen3:14b@think / lw_congruent**: 0x30
- **ollama:qwen3:14b / lw_base**: 0x30
- **ollama:qwen3:14b / lw_congruent**: 0x30
- **ollama:mistral-nemo:12b / lw_base**: 42x7, 10x4, 0x3, 2x3, 6x2
- **ollama:mistral-nemo:12b / lw_congruent**: 2x9, 8x6, 6x5, 42x2, 4x2
- **ollama:llama3.1:8b / lw_base**: 0x20, 84x5, 86x2, 42x2, 100x1
- **ollama:llama3.1:8b / lw_congruent**: 1x21, 42x3, 4x3, 84x2, 54x1
