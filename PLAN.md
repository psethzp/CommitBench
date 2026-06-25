Bluntly: **with only 4×L40 and no Bedrock/API, you can still make this submit-worthy, but the paper must stop claiming “frontier model coverage.”** The main contribution becomes **formal/evaluation semantics + verifier + reproducible open-weight evidence**, not “we benchmarked all top frontier agents.” Your current draft already frames the contribution as an Effect Kernel, verifier, benchmark, and EffectGuard runtime over τ/τ²/τ³-style substrates, so keep that center and shrink the empirical claim. 

## Locked operational defaults after smoke hardening

The active experiment path is local/open-weight only. Bedrock/API blocks are
archived and must not be used for headline claims.

Default queue behavior is now the Step 2b model-controlled path:

```text
queue_script: effectbench_omega/scripts/run_local_open_queue.sh
output_prefix: main_mc_postfix
model_controls_policy: enabled
model_proposal_mode: actions
tensor_parallelism: TP=4 on GPUs 0,1,2,3
model_order: Mistral, Qwen, Llama, Gemma
```

Serving defaults that are part of the plan, not optional caveats:

```text
Mistral-Small-3.2:
  use official vLLM Mistral tokenizer/config/tool parser
  use load_format=auto with the cached HF sharded safetensors
  keep VLLM_USE_FLASHINFER_SAMPLER=0
  never use --language-model-only
  never use the old custom Mistral chat template
  never use --load-format mistral unless consolidated duplicate weights are intentionally cached

Qwen/Llama/Gemma:
  use OpenAI response_format=json_schema for action proposals
```

Prompt fairness invariant:

```text
Every local model receives the same system instruction, task context,
user-turn rendering, action enum, terminal_action requirement, temperature,
and max token budget. Mistral uses tool-call transport only because that is
its official vLLM structured-output path; Qwen/Llama/Gemma use JSON-schema
transport. The semantic prompt is shared.
```

Accepted pre-Step-2b smoke gate:

```text
job_id: local_open_smoke_mc_default_20260622T204613Z
rows: 21/model, balanced across regimes and systems
failures: 0/model
parse_status: json 21/21 for every model
repair_log: empty 21/21 for every model
no_oracle_sentinel_pass_rate: 100% for every model
local_cost_usd: 0
proposal_diversity: all pairwise signatures unequal
queue_defaults_exercised: model_controls_policy=1, model_proposal_mode=actions
```

## Canonical verifier default after V2 hardening

The old generated-trace verifier is now a legacy diagnostic only. Paper-grade
strict-excess labels must use the enumerated admissible-frontier verifier:

```text
legacy diagnostic:
  effectbench_omega/outputs/<split>/kernel_legacy_generated_trace/certificates.parquet

canonical paper labels:
  effectbench_omega/outputs/<split>/kernel_canonical/certificates_enumerated.parquet
```

The canonical gate is:

```text
unexplained_mismatches = 0
certificate replay = 100%
no-oracle tests = 100%
```

Agreement with the old generated-trace verifier is no longer required. When
the old verifier marks a trace strict-excess using a witness that is not
admissible under the enumerated action graph, that row is logged as a
`spurious_legacy_witness` CEGAR/audit finding, not as a canonical failure.

Current frozen split canonical audit:

```text
groups: 7,168
successful traces scored: 21,504
enumerated candidates: 1,205,248
canonical strict-excess labels: 4,089
legacy strict-excess labels: 5,149
spurious legacy witnesses: 1,060
unexplained mismatches: 0
canonical gate: pass
```

## Final EACL rescue freeze after Stages 7-11

The final local-only rescue package is frozen for writing.

```text
lattice policy: fixed declared Pareto lattice for main claims
lattice sensitivity: appendix/diagnostic only
final claim registry: effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv
paper-ready summary: effectbench_omega/reports/eacl_rescue_paper_ready_summary.md
final reproducibility gate: effectbench_omega/reports/final_reproducibility_gate.md
artifact manifest: effectbench_omega/tables/artifact_manifest.csv
artifact count: 13,836 files / 416,877,747 bytes indexed
artifact tracking: Git LFS for generated traces/logs/bundles/figures/binary docs
```

Do not reopen Bedrock/frontier, human-eval, or alternate-lattice robustness
claims unless new experiments are explicitly launched and logged as a new
post-freeze stage.

## Best plan

**Do not chase GPT/Claude/DeepSeek frontier comparisons.** With no Bedrock, the strongest acceptable story is:

> We introduce a certified least-effect semantics for successful tool-agent traces, release a deterministic verifier and witness certificates, and show across reproducible open-weight agents that final-state success substantially overstates least-effect success.

That is still a real paper. τ-bench already evaluates tool-agent-user tasks by final DB-state matching and pass^k; τ² adds dual-control telecom-style user/agent coordination; ToolSandbox adds stateful tool execution and intermediate/final milestones. Your contribution is to wrap such settings with **effect-frontier certificates**, not to invent τ⁴. ([arXiv][1])

## What you can run in 10 days

Your 4×L40 setup gives **192GB raw VRAM** because each NVIDIA L40 has 48GB GDDR6 memory. That is enough for 14B–30B models comfortably and one 70B model with tensor parallelism/quantization. ([NVIDIA][2])

### Recommended locked denominator

Use this as the final, paper-clean grid:

```text
128 tasks × 7 regimes × 2 seeds × 4 models × 3 online systems
= 21,504 online trajectories
```

Task split:

| Family               | Count | Why                                                       |
| -------------------- | ----: | --------------------------------------------------------- |
| τ/τ³ retail          |    32 | Refund/exchange/inventory effects.                        |
| τ/τ³ airline         |    32 | Edit vs cancel/rebook, notification/payment effects.      |
| τ² telecom           |    32 | Shared-world/user-burden effects.                         |
| Delegated docs       |    16 | Draft/share/notify/write-scope effects.                   |
| ToolSandbox/contract |    16 | Stateful tools, milestone and contract-fragility effects. |

Regimes:

```text
FULL
CONCAT
SHARDED
SNOWBALL
REVISE
MEMORY_REVISE
ADV_EFFECT
```

Skip **RECAP**, **STaRK**, **human eval**, and **frontier block**. Those are not needed for the claim and will waste time.

Online systems:

```text
BASE
MODERN_PROJ_GUARD
EFFECTGUARD
```

Offline projection baselines from saved traces:

```text
FINAL_STATE
CORE_DFA
MINISCOPE_PERMISSION
CONTRACT_VALID
CMTF_MENU
REVISABILITY
MODERNSTACK_PROJECTION
KERNEL_FULL
```

This lets you still claim that projected safeguards leave residual strict-excess, without rerunning ten separate controllers.

## Local models to run

| Model                                   | Use                                  |                       GPU setup | Why include                                                                                                                                          |
| --------------------------------------- | ------------------------------------ | ------------------------------: | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Mistral-Small-3.2-24B-Instruct-2506** | Tool/function-calling family control |                        4 GPUs TP4 | Mistral notes improved instruction-following and more robust function calling, so it is a good tool-agent baseline. ([Hugging Face][4])              |
| **Qwen3.6-35B-A3B**                     | Strong Qwen-family local model       |                        4 GPUs TP4 | Keeps one strong Qwen-style local model without relying on API access.                                                                                |
| **Gemma-3-27B-it**                      | Non-Qwen instruction model control   |                        4 GPUs TP4 | Adds a Google open-weight family without making Gemini/API claims.                                                                                   |
| **Llama-3.3-70B-Instruct-AWQ**          | Large non-Qwen control               |                        4 GPUs TP4 | Practical local 70B-class control using cached AWQ INT4 weights instead of full-precision Llama.                                                     |

Do **not** include Qwen3-235B, DeepSeek-V3.2, GPT, Claude, Gemini, or any “frontier” claim. Gemma is an open-weight local model here, not a Gemini/API result.

## Time estimate

Assuming vLLM/SGLang-style batched serving, 4–10 tool turns per trajectory, max output around 512 tokens, and strict JSON/tool parsing:

| Block                                         | Expected wall time |
| --------------------------------------------- | -----------------: |
| Wrappers + pilot + parser fixes               |         1.5–2 days |
| Mistral-Small-24B full run                    |         6–14 hours |
| Qwen3.6-35B-A3B full run                      |        12–30 hours |
| Gemma-3-27B-it full run                       |        10–24 hours |
| Llama-3.3-70B-AWQ full run                    |        24–60 hours |
| Verifier + offline baselines                  |         6–12 hours |
| CEGAR + lattice sensitivity + no-oracle tests |        12–24 hours |
| Aggregation, plots, claim registry            |         8–16 hours |

So, **realistically: 6–8 days wall-clock**, with 2 days buffer for crashes and reruns. If Llama-70B-AWQ becomes the bottleneck, run it on a **64-task stress subset** and keep the full 128-task grid for the other three models. Report that honestly.

## Exact experiments you need

Run these, and only these.

### 1. Main raw-vs-kernel table

For every model × task family × regime:

```text
raw_success
kernel_least_effect_success
strict_excess / successful traces
high_effect_incomparable / successful traces
necessary_high_effect / successful traces
```

Expected pattern: raw success should be meaningfully higher than kernel least-effect success. If the raw-kernel gap is under 8–10 points, the paper becomes weak.

### 2. Projection-loss table

For saved BASE traces, compute residual strict-excess after:

```text
FINAL_STATE
CORE_DFA
MINISCOPE_PERMISSION
CONTRACT_VALID
CMTF_MENU
REVISABILITY
MODERNSTACK_PROJECTION
KERNEL_FULL
```

Expected pattern: every projected safeguard should reduce some bad traces but still leave residual strict-excess. This is the key novelty table.

### 3. EffectGuard table

Compare:

```text
BASE vs MODERN_PROJ_GUARD vs EFFECTGUARD
```

Metrics:

```text
raw_success
kernel_success
strict_excess/success
false_denial
added_turns_p50/p90/p95
extra_reads_p50/p90/p95
```

Expected pattern: EffectGuard reduces strict-excess without killing raw success. The minimum acceptable pattern is:

```text
EffectGuard reduces strict excess by >= 30%
EffectGuard retains >= 88–90% of BASE raw success
false_denial <= 10–12%
p95 added turns <= 3
```

### 4. Regime stress table

Rows:

```text
FULL, CONCAT, SHARDED, SNOWBALL, REVISE, MEMORY_REVISE, ADV_EFFECT
```

Expected pattern: SNOWBALL, MEMORY_REVISE, and ADV_EFFECT should produce higher strict-excess than FULL/CONCAT. CONCAT is important because it controls for “same information, single prompt.”

### 5. CEGAR / abstraction-refinement audit

Take 30–50 tasks and deliberately omit one future-relevant field at a time:

```text
notification/outbox
payment hold
inventory hold
user-visible exposure
contract artifact hash
memory/cache invalidation
```

Expected pattern: the verifier catches missing fields or label changes. This supports “certificate soundness,” not just metrics.

### 6. Effect-lattice sensitivity

Run:

```text
primary lattice
privacy-heavy
reversibility-heavy
burden-heavy
contract-heavy
drop-one-dimension
```

Expected pattern: strict-excess headline should remain directionally stable. Incomparability may move more; that is fine.

### 7. Certificate replay

For every strict-excess label, store:

```text
model trace
lower-effect witness trace or enumerated admissible witness candidate
terminal equivalence proof
effect vectors
dominance relation
state-hash chain
verifier log
```

Expected pattern: **100% replayable certificates**. This is more important than human eval.

## Ten-day schedule

| Day          | Work                                                              |
| ------------ | ----------------------------------------------------------------- |
| Jun 22       | Freeze task list, effect schema, model prompts, tool JSON parser. |
| Jun 23       | Run 5% pilot on all 4 models; fix parser/tool-call failures.      |
| Jun 24       | Run Mistral + Qwen3.6 full grid.                                  |
| Jun 25       | Run Gemma-3-27B-it full grid.                                     |
| Jun 26–28    | Run Llama-70B-AWQ full grid or 64-task stress subset.             |
| Jun 29       | Run verifier, projection-loss baselines, CEGAR.                   |
| Jun 30       | Run lattice sensitivity, overblocking, no-oracle tests.           |
| Jul 1        | Freeze all results. No new experiments except bug-fix reruns.     |
| Jul 2 onward | Rewrite paper only.                                               |

## Acceptance claim you can safely make

With only local models, claim this:

> Across reproducible open-weight tool agents, final-state success substantially overstates certified least-effect success. Existing projected safeguards reduce but do not eliminate residual strict-excess. EffectGuard provides a no-oracle reference controller that reduces excessive effects while retaining most raw success.

Do **not** claim:

```text
state of the art across frontier models
commercial model coverage
GPT/Claude/Gemini generality
largest-model benchmark
τ⁴
```

## Venue chain

No simultaneous submissions. Pick one chain.

### Recommended chain: highest realistic main-conference chance

| Step | Venue                                                                  |                                                       Deadline | Why                                                                                                                                                 |
| ---- | ---------------------------------------------------------------------- | -------------------------------------------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | **ARR Aug 2026 → EACL 2027**                                           | ARR deadline **Aug 3, 2026**; EACL commitment **Oct 11, 2026** | Best fit. NLP/tool-agent evaluation, benchmark, safety/evaluation semantics. EACL 2027 explicitly uses the Aug 3 ARR deadline. ([2027.eacl.org][7]) |
| 2    | If ARR reviews are weak, **do not commit**; revise to **ARR Oct 2026** |                  **Oct 12, 2026** ARR cycle; cycle ends Dec 20 | ARR lets you revise/resubmit or commit after reviews; the schedule lists Aug and Oct cycles. ([ACL Rolling Review][8])                              |
| 3    | Commit later to ACL/EMNLP/NAACL 2027 when eligible                     |                                         depends on future CFPs | ACL/EMNLP are CORE A* in ICORE2026; EACL is CORE A, not trash. ([Core Portal][9])                                                                   |

This is the best route if you care about **acceptance probability**.

### Aggressive A* chain

| Step | Venue                           |                                                                           Deadline | Why / risk                                                                                                                          |
| ---- | ------------------------------- | ---------------------------------------------------------------------------------: | ----------------------------------------------------------------------------------------------------------------------------------- |
| 1    | **AAAI-27 Main / AI Alignment** | Abstract **Jul 21, 2026**; full paper **Jul 28, 2026**; supplement/code **Jul 31** | A* and the AI Alignment track explicitly exists. Risk: only 7 pages technical content, no frontier models, very tight. ([AAAI][10]) |
| 2    | If Phase-1 reject               |                                              Phase-1 notification **Sep 24, 2026** | Then you can submit elsewhere.                                                                                                      |
| 3    | **AAMAS 2027**                  |                               Abstract **Oct 2, 2026**; full paper **Oct 9, 2026** | Strong agent venue and good fit for tool-agent control/evaluation, but ICORE2026 rank is A, not A*. ([OpenReview][11])              |

This is only worth it if your results are clean by July 1 and the paper can become a compact “formal safety case + benchmark artifact.”

### Watchlist, not immediate anchor

| Venue                 | Status                                                                                                                                                                                                                                   |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ICLR 2027**         | Official 2027 CFP was not found in the search. ICLR is CORE A*, and ICLR 2026 used late-September submission dates, but do not plan on a non-official deadline. Good only if the formal kernel/theory is very crisp. ([Core Portal][12]) |
| **ICAPS 2027**        | Strong planning/action-sequencing fit; official page exists and says ICAPS is the premier planning/scheduling forum, but the 2027 CFP dates are not posted yet. ([icaps27.icaps-conference.org][13])                                     |
| **IJCAI 2027**        | 2026 deadline already passed, and IJCAI says future conference locations/dates are announced officially at the preceding conference, so 2027 is not an immediate deadline yet. ([IJCAI][14])                                             |
| **NeurIPS/ICML 2027** | Very high prestige but poor fit unless your theory is exceptional. 2026 main deadlines already passed. ([NeurIPS][15])                                                                                                                   |

## My actual recommendation

**Submit ARR Aug 3 for EACL 2027.** That is the highest chance of a respectable main-conference acceptance with your constraints. EACL is **Core A**, *ACL-family main*, and not a “shit venue.” If reviews are strong, commit EACL. If reviews are bad, revise into ARR Oct and then aim ACL/EMNLP/NAACL 2027.

Try AAAI only if you can compress the paper into a clean 7-page technical story and the results satisfy these gates:

```text
raw-kernel gap >= 10 points
strict_excess/success >= 15%
projection residual strict-excess nonzero for every baseline
EffectGuard strict-excess reduction >= 30%
EffectGuard raw-success retention >= 88–90%
certificate replay = 100%
no red placeholders
no fake frontier-model claims
```

With no Bedrock/API, your best acceptance strategy is **not more models**. It is **clean semantics, deterministic verifier, reproducible open-weight traces, and honest claims.**

[1]: https://arxiv.org/abs/2406.12045?utm_source=chatgpt.com "$τ$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains"
[2]: https://www.nvidia.com/en-us/data-center/l40/?utm_source=chatgpt.com "NVIDIA L40 GPU for Data Center"
[3]: https://qwenlm.github.io/blog/qwen3/?utm_source=chatgpt.com "Qwen3: Think Deeper, Act Faster"
[4]: https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506?utm_source=chatgpt.com "mistralai/Mistral-Small-3.2-24B-Instruct-2506"
[5]: https://huggingface.co/Qwen/Qwen3-30B-A3B?utm_source=chatgpt.com "Qwen/Qwen3-30B-A3B"
[6]: https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct?utm_source=chatgpt.com "meta-llama/Llama-3.3-70B-Instruct"
[7]: https://2027.eacl.org/?utm_source=chatgpt.com "EACL 2027"
[8]: https://aclrollingreview.org/dates "Dates and Venues – ACL Rolling Review – A peer review platform for the Association for Computational Linguistics"
[9]: https://portal.core.edu.au/conf-ranks/196/?utm_source=chatgpt.com "Association for Computational Linguistics"
[10]: https://aaai.org/conference/aaai/aaai-27/main-technical-track-call/ "AAAI-27 Main Technical Track Call - AAAI"
[11]: https://openreview.net/group?id=ifaamas.org%2FAAMAS%2F2027%2FConference&referrer=%5BHomepage%5D%28%2F%29&utm_source=chatgpt.com "AAMAS 2027 Conference"
[12]: https://portal.core.edu.au/conf-ranks/2273/?utm_source=chatgpt.com "International Conference on Learning Representations"
[13]: https://icaps27.icaps-conference.org/ "ICAPS 2027"
[14]: https://www.ijcai.org/?utm_source=chatgpt.com "Welcome to IJCAI | IJCAI"
[15]: https://neurips.cc/Conferences/2026/Dates?utm_source=chatgpt.com "2026 Dates and Deadlines"
