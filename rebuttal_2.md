## Verdict

**Experiment package: almost EACL-submission-grade. Current `CommitBench.pdf`: not submission-ready.**

No paper is ever **guaranteed** EACL acceptance, but after the shared-proposal audit, necessary-high/incomparable stress block, leave-one robustness, canonical frontier audit, replay checks, and native-fidelity validation, the **results are finally strong enough for a serious ARR/EACL main attempt**. The bottleneck is now **paper discipline**, not more GPU experiments.

EACL 2027’s ARR deadline is **Aug 3, 2026**, with author response Sept 14–19, meta-review Oct 8, commitment Oct 11, and notification Nov 12. ARR long papers are capped at **8 content pages**, and ARR explicitly requires a Limitations section; missing limitations or going over length can trigger desk rejection. So the old 18-page PDF with 204,800-episode/API/human-eval claims must not be submitted. ([2027.eacl.org][1])

## What is now strong

Your latest package has the missing rescue pieces that were not present before.

| Evidence block                   |                                                         Current result | Why it matters                                                                                                   |
| -------------------------------- | ---------------------------------------------------------------------: | ---------------------------------------------------------------------------------------------------------------- |
| **Controlled local split**       |                                                          21,504 traces | Main certificate-semantics result: `128 tasks × 7 regimes × 2 seeds × 4 models × 3 systems`.                     |
| **BASE raw-vs-kernel gap**       |                                                         **57.0033 pp** | Final-state success massively overstates least-effect success.                                                   |
| **BASE strict-excess**           |                                 4,086 / 7,168 in main controlled split | Strong central result.                                                                                           |
| **PROJ_GUARD_V2 residual**       |         **7.3242%** corrected split; **9.1657%** shared-proposal split | Projection-only safeguards help but do not fully solve least-effect.                                             |
| **EFFECTGUARD_V2 strict-excess** |                    **0.0000%** in corrected and shared-proposal splits | Strong reference-controller demo, but frame carefully.                                                           |
| **Shared-proposal audit**        |     21,504 traces, 7,168/7,168 paired groups, 0 unexplained mismatches | Removes the earlier concern that different systems got different model proposal distributions.                   |
| **Canonical enumeration**        |              1,205,248 admissible candidates, 0 unexplained mismatches | Very important: certificates are now against enumerated admissible alternatives, not just observed traces.       |
| **Native-fidelity validation**   |              4,608 traces, 4,217 native successes, 391 native failures | Fixes the “everything has 100% raw success” concern at least in a validation block.                              |
| **Stress block**                 | 3,072 traces, 704 necessary-high decisions, 320 incomparable decisions | Shows EffectGuard is not just “always choose low-effect”; it permits necessary escalation and records tradeoffs. |
| **Leave-one robustness**         |                                               39 gate rows, 0 failures | Result is not one model/family artifact.                                                                         |
| **Replay**                       |                                             11,508 bundles, 0 failures | Strong auditability story.                                                                                       |
| **Targeted CEGAR**               |        219 label-change groups across all seven future-relevant fields | Good evidence that abstraction omissions matter and are caught.                                                  |
| **No-oracle**                    |                                        47,616 rows checked, 0 failures | Supports runtime/evaluator separation.                                                                           |
| **Cost**                         |                                                                 $0 API | Local-only reproducibility story.                                                                                |

The model grid is also fine now. Mistral-Small-3.2-24B is justified by function-calling robustness; Qwen3.6-35B-A3B is open-weight/self-hostable; Gemma-3-27B-it gives a non-Qwen Google-family open model with 128K context; Llama-3.3-70B gives a large dense non-Qwen baseline. You do **not** need more models under 4×L40 constraints. ([Hugging Face][2])

## Main key takeaways

Your final story should be:

1. **Final-state success is not enough.** In the controlled local split, BASE agents have 100% final-state success by construction, but only 42.9967% kernel least-effect success; 57.0033% of successful traces are strictly dominated by lower-effect task-equivalent traces.

2. **The missing object is the certificate, not another scalar score.** The contribution is the Effect Kernel: a task-relative frontier over task-equivalent successful traces that labels each success as minimal, strict-excess, necessary-high, or incomparable.

3. **Projection safeguards help but are incomplete.** In the shared-proposal audit, PROJ_GUARD_V2 reduces strict-excess from 57.0033% to 9.1657%, but does not remove it. That is the cleanest empirical bridge to prior work.

4. **EffectGuard is a reference controller, not the main scientific claim.** It removes strict-excess in your local scaffold, but do not oversell it as a universal SOTA agent policy. The paper’s durable contribution is the verifier/certificate semantics.

5. **Native-fidelity validation matters.** The 4,608-trace native block has 391 terminal failures, so reviewers cannot say the whole artifact is only a toy success-only simulator. But keep it as validation, not as the main denominator.

6. **Necessary-high and incomparable cases are now covered.** The 3,072-trace stress block with 704 necessary-high and 320 incomparable EffectGuard decisions directly answers the critique that least-effect evaluation might incorrectly punish all high-effect behavior.

7. **No more model chasing.** More Qwen/Phi/open models will not help acceptance as much as rewriting the paper cleanly around the exact claim registry.

## What is still dangerous

### 1. The PDF is still stale

The `CommitBench.pdf` in the zip is 18 pages and still contains old claims like:

```text
204,800 primary episodes
20,480 frontier-model focused episodes
GPT/Claude/Gemini/Bedrock model grid
human audit
broad SOTA-system comparisons
```

That PDF would likely get rejected. The experiment package has moved on, but the manuscript has not. This is now the largest blocker.

### 2. Do not call projection baselines “SOTA systems”

You can say:

> We instantiate projection baselines corresponding to final-state, path-validity, permission, contract/menu, and revisability predicates.

Do **not** say:

> We faithfully reimplemented CORE, MiniScope, ContractGuard, RACG, Cordon, Agent-C, etc.

Your current tables support **semantic projection-loss**, not a full SOTA leaderboard.

### 3. Controlled split has 100% raw success

This is okay only if you frame it as:

> a successful-trace least-effect certification scaffold.

Do not frame it as a task-solving benchmark. τ-bench itself evaluates dynamic user-agent-tool conversations using APIs, policies, final database-state comparison, and pass^k reliability; ToolSandbox emphasizes stateful tool execution, implicit dependencies, and intermediate/final milestones. Your work should be positioned as an added **least-effect certificate layer** over such substrates, not as replacing native τ/ToolSandbox evaluation. ([arXiv][3])

### 4. EffectGuard at 0% can look tautological

This is now partially fixed by the stress block. But in writing, say:

> EffectGuard is a no-oracle reference controller that demonstrates the kernel can guide action substitution.

Not:

> EffectGuard is universally superior to all prior guards.

The stress block must appear in the main paper or a very visible appendix table, because it proves EffectGuard permits necessary-high and incomparable cases.

### 5. Shared-proposal audit still has a caveat

The shared-proposal audit is strong because every system receives the same frozen BASE proposal. But the BASE proposals came from the older prompt that included `system=BASE`. This is much less bad than before, because all systems share the same proposal, but a picky reviewer may still ask why the frozen proposals were not regenerated after removing the `system=` field.

This is the **only GPU experiment** I would still consider.

## Should you run more experiments?

### No more broad experiments

Do **not** add more models. Do **not** expand native if you decided to skip it. Do **not** run human eval. Do **not** add STaRK. Do **not** revive Bedrock/frontier claims.

### One optional high-value GPU rerun

Run this only if you can spare about half a day to a day:

```text
Fresh no-system-prompt BASE proposal rerun
= 128 tasks × 7 regimes × 2 seeds × 4 models × 1 system
= 7,168 model calls
```

Then replay `BASE`, `PROJ_GUARD_V2`, and `EFFECTGUARD_V2` from those fresh proposals offline.

Why this helps:

* removes the last `system=BASE` prompt caveat;
* keeps the same paired-proposal design;
* does not require rerunning all three systems through the model;
* gives you a cleaner rebuttal to “prompt leakage / system-label confound.”

Acceptance gate:

```text
BASE strict-excess remains >= 50%
PROJ_GUARD_V2 residual strict-excess remains >= 5%
EFFECTGUARD_V2 strict-excess remains 0% or near 0%
canonical unexplained mismatches = 0
no-oracle failures = 0
```

If this passes, the methodology section gets much cleaner. If time is tight, skip it and disclose the existing caveat.

### One offline audit I would definitely run

Run **full stress replay**, not just 60 sampled stress bundles. This is CPU/offline and cheap.

Current stress replay checks 60 bundles. Since the stress block is your answer to the “EffectGuard is tautological” critique, make it stronger:

```text
replay all 3,072 stress certificates
or at least all 1,024 EFFECTGUARD_V2 stress certificates
```

This costs no GPU and gives you a cleaner audit sentence.

## Is skipping native expansion okay?

Yes, **if you frame native validation correctly**.

Your native block already has 4,608 traces and real terminal failures:

```text
BASE raw native success: 81.5755%
PROJ_GUARD_V2 raw native success: 92.9688%
EFFECTGUARD_V2 raw native success: 100.0000%
native terminal failures: 391
native successes: 4,217
```

That is enough to show the framework is not purely success-only. But do not lean on native projection-loss, because in native validation both PROJ_GUARD_V2 and EFFECTGUARD_V2 have 0 strict-excess among successful traces. Use native for:

> “The machinery also runs when terminal success can fail.”

Do not use native for:

> “Projection baselines leave residual strict-excess.”

Use the controlled/shared-proposal split for that.

## Final EACL readiness checklist

| Item                       |                  Status | Action                                                                                                                                      |
| -------------------------- | ----------------------: | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Main empirical claim       |               **Ready** | Use canonical enumerated labels only.                                                                                                       |
| Model grid                 |               **Ready** | No more models.                                                                                                                             |
| Projection-loss claim      |  **Ready with wording** | Call them deterministic projections, not faithful SOTA systems.                                                                             |
| EffectGuard claim          |   **Ready with caveat** | Present as reference controller. Include stress block.                                                                                      |
| Native validation          |               **Ready** | Keep as validation, not headline.                                                                                                           |
| Artifact replay            |        **Mostly ready** | Add full stress replay if possible.                                                                                                         |
| Prompt-confound audit      |   **Good, not perfect** | Optional fresh no-system BASE proposal rerun.                                                                                               |
| Current PDF                |           **Not ready** | Must rewrite.                                                                                                                               |
| Page limit                 | **Fail if current PDF** | ARR long paper must be 8 content pages plus required limitations.                                                                           |
| Anonymity/artifact hygiene |         **Needs scrub** | Remove Google Slides link, `/home/ubuntu/nachiket/...`, old Bedrock instructions from active artifact docs, and any identity-bearing paths. |

## What the rewritten paper should claim

Use this exact posture:

> We introduce Effect Kernels, a certificate semantics for least-effect evaluation of tool-agent traces. Given a successful trace, the verifier enumerates admissible task-equivalent alternatives and certifies whether the trace is nondominated, strictly dominated by a lower-effect witness, necessary-high, or incomparable. Across 21,504 local open-weight controlled trajectories, BASE agents show a 57.0-point final-state-vs-kernel gap. Projection-only safeguards reduce but do not remove residual strict-excess; an effect-aware no-oracle reference controller removes residual strict-excess in the controlled and paired-proposal audits. A 4,608-trajectory native-fidelity validation block, full replay, CEGAR stress, no-oracle sentinels, and necessary-high/incomparable stress support auditability.

Do not claim:

```text
frontier model SOTA
Bedrock/API model coverage
human-eval validation
204,800 episodes
20,480 focused frontier episodes
faithful reproduction of all prior systems
universal optimal online control
τ⁴ / new τ benchmark generation
```

## Main paper table plan

Use **six** main tables/figures maximum.

| Table/Figure | Content                                                                                                                   |
| ------------ | ------------------------------------------------------------------------------------------------------------------------- |
| **Figure 1** | Effect Kernel pipeline: trace → effect ledger → enumerated frontier → certificate.                                        |
| **Table 1**  | Semantic lift: final-state/path/permission/contract/menu/revisability vs effect-kernel question.                          |
| **Table 2**  | Dataset/model grid: 21,504 controlled, 4,608 native validation, 3,072 stress, four local models.                          |
| **Table 3**  | Main controlled + corrected/shared proposal result: BASE 57.0033%, PROJ 7.3242/9.1657%, EffectGuard 0.                    |
| **Table 4**  | Projection-loss table: final/path/permission/contract/revisability/modern-stack projections leave residual strict-excess. |
| **Table 5**  | Native validation: terminal failures and strict-excess among native successes.                                            |
| **Table 6**  | Audit table: enumeration, replay, CEGAR, no-oracle, stress, leave-one robustness.                                         |

Put model-specific and family/regime breakdowns in appendix unless you have space.

## My recommendation

Submit to **ARR Aug 3, 2026 for EACL 2027** after the rewrite. Do not spend remaining time on more general experiments. The paper’s acceptance chance now depends mainly on whether reviewers see a crisp contribution:

> **not a new leaderboard, not a τ³ variant, but a certificate semantics for least-effect tool-agent evaluation.**

The only extra compute I would approve is the **fresh no-system-prompt BASE proposal rerun**. The only extra offline audit I would definitely do is **full stress replay**. Everything else should be writing, artifact hygiene, and claim cleanup.

[1]: https://2027.eacl.org/calls/papers/?utm_source=chatgpt.com "EACL 2027 Call for Main Conference Papers"
[2]: https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506?utm_source=chatgpt.com "mistralai/Mistral-Small-3.2-24B-Instruct-2506"
[3]: https://arxiv.org/abs/2406.12045?utm_source=chatgpt.com "$τ$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains"
