# COST_AUDIT.md — EffectBench-Ω† minimal-plus budget

## Locked run grid

### Main headline grid

- Tasks: 160 total = 32 each from retail, airline, telecom, delegated-docs, and ToolSandbox/contract.
- Regimes: 7 = FULL, CONCAT, SHARDED, SNOWBALL, REVISE, MEMORY_REVISE, ADV_EFFECT.
- Seeds: 2 = 13, 47.
- Systems: 3 = BASE, PROJ_GUARD, EFFECTGUARD.
- Models: 4 = local Qwen3-30B-A3B, Bedrock Qwen3-235B-A22B-2507, Bedrock DeepSeek-V3.2, Bedrock GPT-5.4.
- Headline online trajectories: `160 × 7 × 2 × 3 × 4 = 26,880`.
- Per-system headline trajectories: `160 × 7 × 2 × 4 = 8,960`.
- Local trajectories: `160 × 7 × 2 × 3 × 1 = 6,720`.
- Paid API headline trajectories: `160 × 7 × 2 × 3 × 3 = 20,160`.
- Paid API headline trajectories per paid main model: `6,720`.

### Focused frontier stress block

- Purpose: appendix stress probe only; never mix into headline means.
- Tasks: 64 stress-stratified tasks.
- Regimes: SNOWBALL, MEMORY_REVISE, ADV_EFFECT.
- Seeds: 13, 47.
- Systems: BASE and EFFECTGUARD only.
- Models: Bedrock GPT-5.5 and Claude Opus 4.8.
- Focused trajectories: `64 × 3 × 2 × 2 × 2 = 1,536`.
- Focused trajectories per paid frontier model: `768`.

### Total live trajectories

- Total live online trajectories: `26,880 + 1,536 = 28,416`.
- Total paid API trajectories: `20,160 + 1,536 = 21,696`.
- Offline projection baselines, kernel verification, CEGAR, no-oracle tests, lattice sensitivity, certificate replay, and aggregation should not call an LLM.

## Planning rates

Use the AWS billing export as source of truth. Public rates used for planning:

| Model | Role | Input $/MTok | Cached input $/MTok | Output $/MTok | Planning note |
|---|---|---:|---:|---:|---|
| Qwen3-235B-A22B-2507 | main paid | 0.2266 | n/a | 0.9064 | Use region returned by probe. |
| DeepSeek-V3.2 | main paid | 0.7400 | n/a | 2.2200 | Region pricing can vary. |
| GPT-5.4 | main paid | 2.7500 | 0.2750 | 16.5000 | Bedrock OpenAI rate. |
| GPT-5.5 | focused only | 5.5000 | 0.5500 | 33.0000 | Do not use in main grid. |
| Claude Opus 4.8 | focused only | 5.0000 | 0.5000 | 25.0000 | Do not use in main grid. |
| Qwen3-30B-A3B local | main local | 0 | 0 | 0 | Runs on 4×L40S; no Bedrock charge. |

## Cost formula

For every provider/model/date/region bucket:

```text
cost_usd = (input_tokens / 1e6) * input_rate
         + (cached_input_tokens / 1e6) * cached_input_rate
         + (output_tokens / 1e6) * output_rate
```

Store `raw_input_tokens`, `cached_input_tokens`, `billable_input_tokens`, `output_tokens`, `region`, `request_id`, `retry_count`, `batch_or_on_demand`, and `model_id` for every request.

## Expected scenario

Assume 5,000 paid input tokens and 800 output tokens per paid trajectory after schema compression/caching. No cache discount is included in this estimate, so this is conservative for repeated prompts.

| Model | Episodes | Input MTok | Output MTok | Token cost |
|---|---:|---:|---:|---:|
| Qwen3-235B-A22B-2507 | 6,720 | 33.600 | 5.376 | $12.49 |
| DeepSeek-V3.2 | 6,720 | 33.600 | 5.376 | $36.80 |
| GPT-5.4 | 6,720 | 33.600 | 5.376 | $181.10 |
| GPT-5.5 focused | 768 | 3.840 | 0.614 | $41.40 |
| Claude Opus 4.8 focused | 768 | 3.840 | 0.614 | $34.56 |
| Token subtotal | - | - | - | **$306.34** |
| Retry/logging/export overhead | - | - | - | **$150–300** |
| Expected total | - | - | - | **$456–606** |

## Conservative scenario

Assume 10,000 paid input tokens and 1,500 output tokens per paid trajectory.

| Model | Episodes | Input MTok | Output MTok | Token cost |
|---|---:|---:|---:|---:|
| Qwen3-235B-A22B-2507 | 6,720 | 67.200 | 10.080 | $24.36 |
| DeepSeek-V3.2 | 6,720 | 67.200 | 10.080 | $72.11 |
| GPT-5.4 | 6,720 | 67.200 | 10.080 | $351.12 |
| GPT-5.5 focused | 768 | 7.680 | 1.152 | $80.26 |
| Claude Opus 4.8 focused | 768 | 7.680 | 1.152 | $67.20 |
| Token subtotal | - | - | - | **$595.05** |
| Retry/logging/export overhead | - | - | - | **$150–300** |
| Conservative total | - | - | - | **$745–895** |

## Stress scenario

Assume 20,000 paid input tokens and 2,000 output tokens per paid trajectory.

| Model | Episodes | Input MTok | Output MTok | Token cost |
|---|---:|---:|---:|---:|
| Qwen3-235B-A22B-2507 | 6,720 | 134.400 | 13.440 | $42.64 |
| DeepSeek-V3.2 | 6,720 | 134.400 | 13.440 | $129.29 |
| GPT-5.4 | 6,720 | 134.400 | 13.440 | $591.36 |
| GPT-5.5 focused | 768 | 15.360 | 1.536 | $135.17 |
| Claude Opus 4.8 focused | 768 | 15.360 | 1.536 | $115.20 |
| Token subtotal | - | - | - | **$1,013.66** |
| Retry/logging/export overhead | - | - | - | **$150–300** |
| Stress total | - | - | - | **$1,164–1,314** |

## Hard caps

- Model-probe cap: **$5**.
- Pilot cap: **$100**.
- Main-plus-frontier soft cap: **$900**.
- Main-plus-frontier hard cap: **$1,200**.
- Absolute do-not-cross without human approval: **$1,500**.
- User Bedrock credit budget: **$2,000**.

The minimal-plus suite is feasible under the $2,000 Bedrock budget. Stop at the pilot if projected full-run spend exceeds $1,500 or if invalid/retried episodes exceed 5% for any provider.

## Cost-control rules

1. Run model probes first; do not assume model IDs or regions.
2. Run a 5% pilot, then project full-run cost from actual token logs.
3. Use fixed tool-schema compression and prompt caching where supported.
4. Cap max output at 768 tokens and max turns at 12.
5. Retry at most once per failed paid episode.
6. Do not use LLM-as-judge for headline labels; use deterministic wrappers and verifier certificates.
7. Use local Qwen for any optional normalizer/extractor support; mark such calls as non-headline.
8. Do not add Claude/Gemini/GPT-5.5 to the headline grid.
9. Do not call models for offline projection baselines.
10. Freeze run artifacts after Day 10; later changes are code-bug reruns only, not new experiments.

## Final cost report fields

Write `reports/cost_audit_final.csv` with one row per API request:

```csv
timestamp,provider,model_id,region,system,task_id,family,regime,seed,request_id,retry_count,batch_or_on_demand,raw_input_tokens,cached_input_tokens,billable_input_tokens,output_tokens,input_rate,cached_input_rate,output_rate,cost_usd,status,error_type
```

Write `reports/cost_audit_summary.md` with totals by model, family, regime, system, and retry reason.
