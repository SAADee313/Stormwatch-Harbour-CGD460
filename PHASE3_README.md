# Phase 3: Local LLM Harbour Master (Student 231713)

Install Ollama for Windows from https://ollama.com/download and open PowerShell:

```powershell
ollama pull qwen2.5:3b
ollama list
python run.py --agent llm --seed 1 --model qwen2.5:3b
```

Ollama must be running locally on 127.0.0.1:11434. The first LLM run can take a while (30 decision turns, potentially 90 calls). For exact replay without model calls:

```powershell
python run.py --agent llm --seed 1 --replay
```

Every prompt and model response is logged in `logs/llm_log.jsonl`. Do not delete logs before replay. The default is NO approval for close_harbour or release_cargo. `--approve-dangerous` is for deliberate supervised tests, not normal runs. Model only sees serialized text reports, not internal simulation objects. The agent uses the utility policy for routine worker movement, with LLM worker assignments as optional overrides.

Important: This is a starting implementation for Task C, not the completed assignment. You still need the 5-seed comparison, hallucination audit, injection tests, prompt variants and safety analysis. The JSON parser validates structure and actions; factual assertions in `thought`/`final_report` still require auditing. Current `hold_ship` only affects the head of the queue and release_cargo records authorization rather than directly delivering units. No remote API is used. Document model version from `ollama list` and date.
