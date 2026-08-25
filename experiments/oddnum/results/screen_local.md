# Summary: screen_local.jsonl

Rows: 120

| model | condition | n | n_odd | n_even | n_none/other | P(odd of parsed) | Wilson 95% CI | P(in_range) | n_amb |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| ollama:qwen3:14b | spine_ieven_rodd | 10 | 0 | 10 | 0 | 0.000 | [0.000, 0.278] | 1.000 | 0 |
| ollama:qwen3:14b | spine_ieven_rnone | 10 | 0 | 10 | 0 | 0.000 | [0.000, 0.278] | 1.000 | 0 |
| ollama:qwen3:14b | spine_iodd_reven | 10 | 10 | 0 | 0 | 1.000 | [0.722, 1.000] | 1.000 | 0 |
| ollama:qwen3:14b | spine_inone_rnone | 10 | 0 | 10 | 0 | 0.000 | [0.000, 0.278] | 1.000 | 0 |
| ollama:mistral-nemo:12b | spine_ieven_rodd | 10 | 0 | 10 | 0 | 0.000 | [0.000, 0.278] | 1.000 | 0 |
| ollama:mistral-nemo:12b | spine_ieven_rnone | 10 | 0 | 10 | 0 | 0.000 | [0.000, 0.278] | 1.000 | 0 |
| ollama:mistral-nemo:12b | spine_iodd_reven | 10 | 10 | 0 | 0 | 1.000 | [0.722, 1.000] | 1.000 | 0 |
| ollama:mistral-nemo:12b | spine_inone_rnone | 10 | 7 | 3 | 0 | 0.700 | [0.397, 0.892] | 1.000 | 0 |
| ollama:llama3.1:8b | spine_ieven_rodd | 10 | 0 | 10 | 0 | 0.000 | [0.000, 0.278] | 1.000 | 0 |
| ollama:llama3.1:8b | spine_ieven_rnone | 10 | 0 | 10 | 0 | 0.000 | [0.000, 0.278] | 1.000 | 0 |
| ollama:llama3.1:8b | spine_iodd_reven | 10 | 10 | 0 | 0 | 1.000 | [0.722, 1.000] | 1.000 | 0 |
| ollama:llama3.1:8b | spine_inone_rnone | 10 | 3 | 7 | 0 | 0.300 | [0.108, 0.603] | 1.000 | 0 |

## Value histogram (top 5 per model x condition)

- **ollama:qwen3:14b / spine_ieven_rodd**: 2x10
- **ollama:qwen3:14b / spine_ieven_rnone**: 42x9, 50x1
- **ollama:qwen3:14b / spine_iodd_reven**: 1x6, 17x4
- **ollama:qwen3:14b / spine_inone_rnone**: 42x10
- **ollama:mistral-nemo:12b / spine_ieven_rodd**: 2x5, 4x3, 8x1, 6x1
- **ollama:mistral-nemo:12b / spine_ieven_rnone**: 2x10
- **ollama:mistral-nemo:12b / spine_iodd_reven**: 7x4, 5x2, 11x1, 15x1, 3x1
- **ollama:mistral-nemo:12b / spine_inone_rnone**: 72x2, 63x2, 37x1, 95x1, 42x1
- **ollama:llama3.1:8b / spine_ieven_rodd**: 50x4, 98x2, 78x1, 42x1, 96x1
- **ollama:llama3.1:8b / spine_ieven_rnone**: 2x4, 42x2, 52x1, 98x1, 46x1
- **ollama:llama3.1:8b / spine_iodd_reven**: 47x1, 95x1, 13x1, 1x1, 37x1
- **ollama:llama3.1:8b / spine_inone_rnone**: 42x6, 85x1, 73x1, 14x1, 43x1
