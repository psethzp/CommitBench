# EffectKernelBench Artifact

Review-facing artifact for complete-trace Pareto effect certification.

Run exactly these commands from this directory:

```bash
python scripts/reproduce.py --check-only
python scripts/reproduce.py --tables
python scripts/run_fresh_smoke.py --config configs/fresh_smoke.yaml
```

The main split is `final_paired_control`. It is generated from real local vLLM BASE proposals and deterministic paired replay.
Inside this clean artifact, the fresh-smoke command verifies included smoke evidence. From the source repository, the same command launches the 512-call GPU smoke when outputs are absent or `--force` is passed.
