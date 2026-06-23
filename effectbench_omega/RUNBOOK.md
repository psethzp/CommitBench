# EffectBench-Ω Minimal-Plus Runbook

## Current Rule

Do not run the full local Qwen grid or any main Bedrock experiment until the user explicitly starts that stage. Local setup, cache checks, tiny local-Qwen smoke calls, dry runs, deterministic audits, non-paid provider probes, and explicitly requested tiny Bedrock sanity probes are allowed.

## Handoff Status

The end-to-end code workflow is ready for staged experiments. The current proof is a tiny smoke run, not a paper result: 15 dry trajectories plus 3 local-Qwen calls exercised run generation, ledgers, no-oracle logs, verifier, projection baselines, CEGAR, lattice sensitivity, uncertainty, replay bundles, cost audit, aggregate tables, and claim registry output.

## Checkpoint Tracker

| Checkpoint | Status | Evidence |
|---|---|---|
| Python/venv setup | Done | `.venv`, `artifacts/python_version.txt`, `artifacts/requirements.lock.txt` |
| Package install | Done | editable `effectbench-omega-local` via `pyproject.toml` |
| Git LFS installed | Done | `artifacts/git_lfs_version.txt` |
| Qwen cache search | Done | cache found under `/home/ubuntu/.cache/huggingface/hub/models--Qwen--Qwen3-30B-A3B-Instruct-2507` |
| Qwen cache verification | Done | `artifacts/local_qwen_cache.json` shows 16 shards, no incomplete files, tokenizer/config loadable |
| TP choice | Done | TP=4 selected for one local endpoint to use all four L40S GPUs |
| Local Qwen server | Running | `http://localhost:8001/v1/models`, PID in `reports/local_qwen_tp4.pid` |
| Upstream clones | Done | shallow pinned clones in `upstreams/` |
| Repo/model pins | Done | `artifacts/repo_versions.json` |
| Manifest builder | Done | `manifests/tasks_minimal_plus.csv`, 26,880 rows |
| Benchmark code | Done | `effectbench/`, `scripts/`, `schemas/`, `tests/` |
| 90-row deterministic dry run | Done | `outputs/dry_local/`, 90 traces, 0 failures |
| 90-row local-Qwen pilot | Done | `outputs/local_qwen_pilot/`, 90 local calls, 0 failures; this is not the full grid |
| Latest workflow smoke dry side | Done | `outputs/workflow_smoke_dry/`, 15 traces, 0 failures |
| Latest workflow smoke local side | Done | `outputs/workflow_smoke_local_qwen/`, 3 local calls, 0 failures |
| Workflow verifier | Done | dry: 15 certs, 5 strict excess; local: 3 certs, 1 strict excess |
| Workflow no-oracle audit | Done | dry and local pass rate: 100 percent |
| Workflow replay bundles | Done | dry: 6 bundles, 0 failures; local: 3 bundles, 0 failures |
| Workflow cost audit | Done | dry: 0 USD; local: 3 local requests, 0 USD |
| Bedrock credential source | Done | EC2 role pattern from `/home/ubuntu/qwen_bedrock_test.sh`; stale local static credentials are ignored |
| Bedrock Qwen region scan | Done | `models/qwen_bedrock_region_scan.csv`; exact Qwen3-235B and Qwen3-Coder-480B work in `us-east-2` |
| Bedrock model listing | Done | Qwen exact in `us-east-2`, DeepSeek/GPT-OSS/Claude profile in `us-east-1` |
| Bedrock final provider probe | Done | `models/model_snapshot_bedrock_sanity_final.csv`, tiny paid Bedrock calls plus local endpoint check |
| Bedrock Qwen SOTA runner smoke | Done | `outputs/bedrock_qwen_sota_sanity/`, exact Qwen3-235B and exact Qwen3-Coder-480B, 0 failures |
| Bedrock headline runner smoke | Done | `outputs/bedrock_sanity_final/`, 3 traces, 0 failures |
| Bedrock focused-frontier runner smoke | Done | `outputs/bedrock_frontier_sanity/`, 2 traces, 0 failures |
| Native-source audit | Done | `tables/native_source_audit.csv`, `reports/native_source_audit.md` |
| Main Bedrock grid | Paused | not run |
| Full local Qwen grid | Paused | not run by request |
| Final local verification pass | Done | `pip check`, compileall, no-oracle tests, sanity check, reproduce check, placeholder scan, endpoint check |

## Feature Status

| Feature | Status | Current Scope |
|---|---|---|
| Family wrappers | Source-backed deterministic adapters | Four benchmark families carry pinned upstream source records/hashes; delegated-docs is declared synthetic controlled. Native server execution remains a separate stronger replication mode. |
| Regime builder | Working | Builds `FULL`, `CONCAT`, `SHARDED`, `SNOWBALL`, `REVISE`, `MEMORY_REVISE`, `ADV_EFFECT`. |
| Manifest builder | Working | Generates the locked 160-task × 7-regime × 2-seed × 4-model × 3-system denominator. |
| BASE | Working | Vanilla local policy. |
| PROJ_GUARD | Working | Local menu filtering, clarification, staging, and contract checks. |
| EFFECTGUARD | Working | No-oracle lower-effect substitution and escalation logging. |
| Verifier | Working | Offline Pareto certificates over task-equivalent successful traces. |
| Projection baselines | Working | Deterministic projection-loss table from saved traces/certificates. |
| CEGAR | Working scaffold | Omission audit detects future-relevant abstraction fields. |
| Lattice sensitivity | Working scaffold | Emits primary and alternate lattice rows. |
| Bootstrap | Working scaffold | Emits deterministic smoke intervals. |
| Replay bundles | Working | JSON witness bundles plus strict replay check. |
| Cost audit | Working with pricing caveat | Local requests record zero cost; Bedrock request/token counts are logged, but exact dollars need a rate card or AWS billing export. |
| Claim registry | Working scaffold | Smoke claim registries generated under `metrics/`. |

## Execution Log

1. Created environment and installed required packages.

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   uv pip install -e .
   ```

2. Verified local Qwen cache.

   ```bash
   python effectbench_omega/scripts/verify_local_qwen_cache.py
   ```

   Result: cache present and complete; no download needed.

3. Started local Qwen with all four GPUs.

   ```bash
   QWEN3_TP=4 bash effectbench_omega/scripts/launch_local_qwen.sh
   ```

   Result: endpoint served `http://localhost:8001/v1/models`; a small generation returned `OK`.

4. Pinned upstream repos and local model snapshot.

   ```bash
   GIT_LFS_SKIP_SMUDGE=1 python effectbench_omega/scripts/pin_upstreams.py
   ```

   Result: TAU Bench, TAU2 Bench, ToolSandbox, and Qwen snapshot recorded in `artifacts/repo_versions.json`.

5. Built the full manifest.

   ```bash
   python effectbench_omega/effectbench/families/build_manifest.py \
     --out effectbench_omega/manifests/tasks_minimal_plus.csv
   ```

   Result: 26,880 rows.

6. Ran the latest end-to-end smoke without full experiments.

   ```bash
   python effectbench_omega/scripts/run_workflow_smoke.py \
     --dry-limit 15 \
     --local-model-limit 3
   ```

   Result: dry and local-Qwen workflow paths passed with zero failures and zero cost.

7. Prepared Bedrock sanity probe path and attempted one capped probe.

   ```bash
   python effectbench_omega/scripts/probe_models.py \
     --config effectbench_omega/configs/minimal_plus.yaml \
     --out effectbench_omega/models/model_snapshot_tiny_bedrock_probe.csv \
     --max-cost-usd 5 \
     --allow-paid-probe \
     --max-paid-calls-per-model 1
   ```

   Result: no paid calls were made because AWS returned an invalid security token before invocation.

8. Verified working Bedrock credential format from the known-good Qwen shell script.

   ```bash
   /home/ubuntu/qwen_bedrock_test.sh "Write a tiny Python hello world."
   ```

   Result: Bedrock `converse` works in `us-east-1` when stale `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, and `AWS_PROFILE` are unset and the EC2 role is used.

9. Ran a Qwen Bedrock region scan.

   ```bash
   python effectbench_omega/scripts/probe_bedrock_qwen_regions.py \
     --out effectbench_omega/models/qwen_bedrock_region_scan.csv \
     --credential-source ec2-role
   ```

   Result: exact `qwen.qwen3-235b-a22b-2507-v1:0` and exact `qwen.qwen3-coder-480b-a35b-v1:0` are listed and invocable from `us-east-2`.

10. Ran final capped Bedrock provider sanity snapshot.

   ```bash
   python effectbench_omega/scripts/probe_models.py \
     --config effectbench_omega/configs/minimal_plus.yaml \
     --out effectbench_omega/models/model_snapshot_bedrock_sanity_final.csv \
     --models qwen3_30b_a3b_local qwen3_235b_a22b_2507_bedrock qwen3_coder_480b_a35b_bedrock deepseek_v3_2_bedrock gpt_5_4_bedrock gpt_5_5_bedrock claude_opus_4_8_bedrock \
     --regions us-east-1 \
     --max-cost-usd 5 \
     --allow-paid-probe \
     --max-paid-calls-per-model 1 \
     --probe-max-tokens 96 \
     --credential-source ec2-role
   ```

   Result:

   | Logical role | Tested Bedrock ID | Resolution |
   |---|---|---|
   | `qwen3_235b_a22b_2507_bedrock` | `qwen.qwen3-235b-a22b-2507-v1:0` in `us-east-2` | expected |
   | `qwen3_coder_480b_a35b_bedrock` | `qwen.qwen3-coder-480b-a35b-v1:0` in `us-east-2` | optional Qwen stress model |
   | `deepseek_v3_2_bedrock` | `deepseek.v3.2` | expected |
   | `gpt_5_4_bedrock` | `openai.gpt-oss-120b-1:0` | substitute because GPT-5.4 is not listed |
   | `gpt_5_5_bedrock` | `openai.gpt-oss-120b-1:0` | substitute because GPT-5.5 is not listed |
   | `claude_opus_4_8_bedrock` | `us.anthropic.claude-opus-4-8` | expected inference profile; direct foundation model ID is not on-demand invocable |

11. Ran Bedrock-backed Qwen SOTA-format runner sanity.

   ```bash
   python effectbench_omega/effectbench/families/build_manifest.py \
     --out effectbench_omega/manifests/tasks_qwen_sota_sanity.csv \
     --regimes FULL \
     --models qwen3_235b_a22b_2507_bedrock qwen3_coder_480b_a35b_bedrock \
     --systems BASE \
     --seeds 13 \
     --limit-base-tasks 1

   python effectbench_omega/scripts/run_online.py \
     --config effectbench_omega/configs/minimal_plus.yaml \
     --manifest effectbench_omega/manifests/tasks_qwen_sota_sanity.csv \
     --split bedrock_qwen_sota_sanity \
     --systems BASE \
     --models qwen3_235b_a22b_2507_bedrock qwen3_coder_480b_a35b_bedrock \
     --regimes FULL \
     --out effectbench_omega/outputs/bedrock_qwen_sota_sanity \
     --limit 2 \
     --call-bedrock-model \
     --allow-paid-bedrock \
     --bedrock-region auto \
     --bedrock-credential-source ec2-role
   ```

   Result: exact Qwen3-235B and exact Qwen3-Coder-480B both resolved to `us-east-2`, returned visible `LOW`, and produced 2 traces with 0 failures.

12. Ran Bedrock-backed headline-format runner sanity.

   ```bash
   python effectbench_omega/scripts/run_online.py \
     --config effectbench_omega/configs/minimal_plus.yaml \
     --manifest effectbench_omega/manifests/tasks_minimal_plus.csv \
     --split bedrock_sanity_final \
     --systems BASE \
     --models qwen3_235b_a22b_2507_bedrock deepseek_v3_2_bedrock gpt_5_4_bedrock \
     --regimes FULL \
     --out effectbench_omega/outputs/bedrock_sanity_final \
     --limit 3 \
     --call-bedrock-model \
     --allow-paid-bedrock \
     --bedrock-region auto \
     --bedrock-credential-source ec2-role
   ```

   Result: 3 traces, 6 ledger rows, 0 failures. API advice text was visible for all three rows.

13. Ran Bedrock-backed focused-frontier format sanity.

   ```bash
   python effectbench_omega/effectbench/families/build_manifest.py \
     --out effectbench_omega/manifests/tasks_frontier_focus_sanity.csv \
     --regimes SNOWBALL \
     --models gpt_5_5_bedrock claude_opus_4_8_bedrock \
     --systems BASE \
     --seeds 13 \
     --limit-base-tasks 1

   python effectbench_omega/scripts/run_online.py \
     --config effectbench_omega/configs/minimal_plus.yaml \
     --manifest effectbench_omega/manifests/tasks_frontier_focus_sanity.csv \
     --split bedrock_frontier_sanity \
     --systems BASE \
     --models gpt_5_5_bedrock claude_opus_4_8_bedrock \
     --regimes SNOWBALL \
     --out effectbench_omega/outputs/bedrock_frontier_sanity \
     --limit 2 \
     --call-bedrock-model \
     --allow-paid-bedrock \
     --bedrock-region auto \
     --bedrock-credential-source ec2-role
   ```

   Result: 2 traces, 4 ledger rows, 0 failures. GPT-OSS substitute and Claude Opus 4.8 inference profile both returned visible `LOW` advice.

14. Ran native-source audit.

   ```bash
   python effectbench_omega/effectbench/audit/native_source_audit.py \
     --manifest effectbench_omega/manifests/tasks_minimal_plus.csv \
     --out effectbench_omega/tables/native_source_audit.csv \
     --summary-md effectbench_omega/reports/native_source_audit.md
   ```

   Result: TAU retail, TAU airline, TAU2 telecom, and ToolSandbox families are source-backed with pinned source hashes; delegated-docs is explicitly marked `declared_synthetic_controlled_family`.

15. Ran final local verification after docs and smoke updates.

   ```bash
   python -m pip check
   python -m compileall -q effectbench_omega/effectbench effectbench_omega/scripts
   pytest -q effectbench_omega/tests/no_oracle
   python effectbench_omega/scripts/sanity_check.py --local-only
   python effectbench_omega/scripts/reproduce.py --check-only
   python effectbench_omega/scripts/no_red_placeholders.py --root effectbench_omega
   curl http://localhost:8001/v1/models
   ```

   Result: all passed; reproduce check found no missing required smoke files and confirmed the local Qwen endpoint is live.

## Stage 0: Local Readiness

Use this before any local experiment stage:

```bash
source .venv/bin/activate
python effectbench_omega/scripts/verify_local_qwen_cache.py
curl http://localhost:8001/v1/models
```

If the local server is not running:

```bash
QWEN3_TP=4 bash effectbench_omega/scripts/launch_local_qwen.sh
tail -f effectbench_omega/reports/local_qwen_tp4.log
```

TP guidance: TP=4 is best for the current one-endpoint plan because it uses all four GPUs for Qwen3-30B. TP=2 is useful only if running two independent vLLM replicas and partitioning jobs manually.

## Stage 1: Code And Workflow Smoke

Current proof command:

```bash
python effectbench_omega/scripts/run_workflow_smoke.py \
  --dry-limit 15 \
  --local-model-limit 3
```

This is the default health check. It intentionally avoids the full local grid.

## Stage 2: Full Local Qwen Run

Run this later when the user wants the actual local experiment stage:

```bash
python effectbench_omega/scripts/run_online.py \
  --config effectbench_omega/configs/minimal_plus.yaml \
  --manifest effectbench_omega/manifests/tasks_minimal_plus.csv \
  --split main_local \
  --systems BASE PROJ_GUARD EFFECTGUARD \
  --models qwen3_30b_a3b_local \
  --regimes FULL CONCAT SHARDED SNOWBALL REVISE MEMORY_REVISE ADV_EFFECT \
  --out effectbench_omega/outputs/main_local \
  --call-local-model
```

Then run the offline verifier and audits on `outputs/main_local/`. Do not mix these results with Bedrock until the provider runs are separately approved and logged.

## Stage 3: Provider Probe

Before any paid run, refresh the capped provider snapshot:

```bash
python effectbench_omega/scripts/probe_models.py \
  --config effectbench_omega/configs/minimal_plus.yaml \
  --out effectbench_omega/models/model_snapshot.csv \
  --models qwen3_30b_a3b_local qwen3_235b_a22b_2507_bedrock qwen3_coder_480b_a35b_bedrock deepseek_v3_2_bedrock gpt_5_4_bedrock gpt_5_5_bedrock claude_opus_4_8_bedrock \
  --regions us-east-1 \
  --max-cost-usd 5 \
  --allow-paid-probe \
  --max-paid-calls-per-model 1 \
  --probe-max-tokens 96 \
  --credential-source ec2-role
```

This is a tiny paid sanity probe, not an experiment.

## Stage 4: Bedrock Experiments

Paused until explicitly approved. When approved, use this order:

1. Local Qwen full run first, then freeze/check `outputs/main_local/`.
2. Paid Bedrock pilot, capped and small.
3. Main Bedrock models in batches, never all paid models blindly at once.
4. Focused frontier block last, because it is appendix/stress-only.

Paid pilot skeleton:

```bash
python effectbench_omega/scripts/run_online.py \
  --config effectbench_omega/configs/minimal_plus.yaml \
  --manifest effectbench_omega/manifests/tasks_minimal_plus.csv \
  --split pilot_bedrock \
  --systems BASE PROJ_GUARD EFFECTGUARD \
  --models qwen3_235b_a22b_2507_bedrock deepseek_v3_2_bedrock gpt_5_4_bedrock \
  --regimes FULL MEMORY_REVISE ADV_EFFECT \
  --out effectbench_omega/outputs/pilot_bedrock \
  --limit 300 \
  --call-bedrock-model \
  --allow-paid-bedrock \
  --bedrock-region auto \
  --bedrock-credential-source ec2-role
```

Main paid batches should use the same Bedrock flags and should be split by model/system/regime so failures or budget movement are easy to stop and resume.

## Stage 5: Freeze Checks

Before any paper-facing result freeze:

```bash
python effectbench_omega/scripts/reproduce.py --check-only
pytest -q effectbench_omega/tests/no_oracle
python effectbench_omega/scripts/no_red_placeholders.py --root effectbench_omega
python effectbench_omega/effectbench/metrics/claim_registry_check.py \
  --paper paper/main.tex \
  --registry effectbench_omega/metrics/claim_registry.csv
```

The current repo has smoke registries, not a final paper claim registry.
# Archived Bedrock-Era Runbook

This runbook is not the active execution path. The active local-only defaults,
Mistral serving requirements, prompt fairness invariant, and accepted pre-Step-2b
smoke are tracked in `effectbench_omega/RUNBOOK_LOCAL_ONLY.md`.

Do not use this file for headline experiment commands unless the project is
explicitly re-opened for Bedrock/API runs.
