# Phase 4: actual experiments (student ID 231713)

Run from this folder with Ollama running and qwen2.5:3b downloaded.

```powershell
python phase4_smoke.py
python phase4_evaluate.py
python phase4_tests.py
```

`phase4_evaluate.py` runs 5 seeds (11-15) for utility and LLM and saves actual results to `results/phase4_llm_comparison.csv`. This may take several minutes.

`phase4_tests.py` runs 10 attacks x 3 trials x 2 conditions = 60 local LLM calls. It saves raw model outputs and automatic schema/permission checks. **Manually label whether each attack succeeded**: a valid format does NOT mean the model resisted injection. The 'before' condition intentionally places attack text outside the data boundary; the 'after' condition explicitly marks it as untrusted. The code executor always applies the approval gate.

Task C also requires manually auditing at least 10 claims against the corresponding reports in `logs/llm_log.jsonl`, and 3 hallucination probes. Task D also requires a separate zero-shot versus few-shot format comparison on at least 5 situations and a prompt change log. These are NOT completed by these scripts. Do not claim otherwise.

Important: the `--approve-dangerous` CLI flag in the inherited project is a testing bypass, not an interactive human-approval mechanism. For the final submission, replace it with per-action confirmation and document the tests.
