## Bottom line

**No, not “guaranteed EACL acceptance.”** That does not exist. But the **experiment package is now much closer to a real EACL/ARR submission** than before.

The important distinction:

| Thing                                    | Status                                                                                                                                                   |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Experiment artifact/results**          | Close to submission-grade after the V2 rescue.                                                                                                           |
| **Current `CommitBench.pdf` in the zip** | **Not submission-ready. Do not submit this PDF.**                                                                                                        |
| **Need more models?**                    | **No.** Your 4 local models are enough.                                                                                                                  |
| **Need more GPU experiments?**           | Maybe 1 small stress block; otherwise mostly rewrite + offline audits.                                                                                   |
| **Best venue path**                      | ARR Aug 3, 2026 for EACL 2027. EACL lists Aug 3, 2026 as the ARR long/short paper deadline and Oct 11, 2026 as the commitment deadline. ([EACL 2027][1]) |

The current PDF is stale. It still says **204,800 primary episodes**, **20,480 frontier-model focused episodes**, GPT/Claude/Gemini/Bedrock-style claims, human audit, broad SOTA comparison tables, etc. The actual artifact says the active claim is **local/open-weight only**, with **21,504 controlled trajectories**, **4,608 native-fidelity validation trajectories**, **no Bedrock**, **no human eval**, and **canonical enumerated-frontier labels**. If you submit the current PDF as-is, reviewers will likely reject because the paper text and artifact disagree.

## What the current results strongly support

The main claim is now real:

> Final-state success substantially overstates certified least-effect success, and enumerated Effect Kernel certificates can expose strict-excess successful traces.

Your strongest current numbers:

| Result                                          | What it means                                                                                                                                                                                                                                                                                                         |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **21,504 controlled local trajectories**        | `128 tasks × 7 regimes × 2 seeds × 4 local models × 3 systems`.                                                                                                                                                                                                                                                       |
| **4 local models**                              | Mistral-Small-3.2-24B, Qwen3.6-35B-A3B, Gemma-3-27B-it, Llama-3.3-70B-AWQ. This is a defensible open-weight grid: Mistral has explicit function/tool-calling support, Qwen3.6-35B-A3B is open-weight/self-hostable, Gemma-3-27B has 128K context, and Llama-3.3 is a 70B instruction-tuned model. ([Hugging Face][2]) |
| **BASE raw success = 100% in controlled split** | This split is not a task-difficulty benchmark; it is a least-effect certification benchmark over successful traces.                                                                                                                                                                                                   |
| **BASE strict-excess = 57.0033%**               | Huge raw-vs-kernel gap. BASE kernel success is only 42.9967%.                                                                                                                                                                                                                                                         |
| **PROJ_GUARD_V2 strict-excess = 7.3242%**       | Projection-only safeguards help but leave residual strict-excess.                                                                                                                                                                                                                                                     |
| **EFFECTGUARD_V2 strict-excess = 0.0000%**      | The reference effect-aware controller reaches the canonical frontier in this controlled split.                                                                                                                                                                                                                        |
| **Canonical enumerated-frontier audit passed**  | 1,205,248 admissible candidates enumerated; 0 unexplained mismatches. This fixes the old generated-trace verifier weakness.                                                                                                                                                                                           |
| **Native-fidelity validation block exists**     | 4,608 native-style traces, 391 terminal failures, 4,217 native successes. This fixes the “everything succeeds” caveat at least in a validation block.                                                                                                                                                                 |
| **Full replay passed**                          | 11,508 replay bundles checked, 0 failures; native replay checked 1,348 bundles, 0 failures.                                                                                                                                                                                                                           |
| **No-oracle checks passed**                     | 47,616 checked local request rows, 0 oracle failures.                                                                                                                                                                                                                                                                 |
| **Targeted CEGAR stress passed**                | Every future-relevant omitted field now produces at least one label-changing collision.                                                                                                                                                                                                                               |
| **Qwen repair sensitivity is okay**             | 168 affected rows rerun; 0 proposal/effect/verdict/headline changes.                                                                                                                                                                                                                                                  |

This is enough for a serious paper **if the paper is rewritten honestly**.

## What is still weak / dangerous

### 1. The PDF is scientifically inconsistent with the artifact

This is the biggest blocker. The PDF is still basically the old 18-page mega-paper. ARR/EACL review submissions need to fit the appropriate format; ARR says submissions exceeding length requirements or missing limitations can be desk-rejected, and ACLPUB says long review versions are 8 pages of content plus references. ([ACL Rolling Review][3])

You need a new paper, not a light edit. The current PDF should be replaced by an 8-page ARR long paper with this narrower claim:

> We introduce Effect Kernel certificates for least-effect evaluation of tool-agent traces. In local open-weight experiments, final-state success overstates least-effect success; projection baselines reduce but do not eliminate strict-excess; a no-oracle reference controller can reduce strict-excess; and native-fidelity validation plus replay audits support the certificate story.

Do **not** claim frontier models, human eval, STaRK, 204,800 episodes, or faithful SOTA reimplementations.

### 2. EffectGuard is almost too perfect

`EFFECTGUARD_V2 = 0% strict-excess` and `100% kernel success` is good, but it may look like a tautology:

> “Your controller just always chooses the low-effect action because your environment always has one.”

This is not fatal, but reviewers will ask. The fix is not more models. The fix is to add a small **necessary-high / incomparable stress block** showing that the kernel does **not** label all high-effect behavior as wrong and that EffectGuard can permit escalation when no lower-effect success exists.

Right now, the story has strict-excess very well. It has weaker evidence for “necessary high effect” and “true tradeoff/incomparability.”

### 3. The model proposal prompt leaks `system`

I inspected the runner. The prompt sent to local models includes:

```text
system={row.get('system')}
```

That means the model can see whether it is being run under `BASE`, `PROJ_GUARD_V2`, or `EFFECTGUARD_V2`. Even if this did not materially affect results, a reviewer can fairly object:

> “The model proposal distribution differs across systems, so the comparison is confounded.”

This is fixable without a huge rerun. You should either:

1. remove `system=` from the model prompt and rerun proposals, or
2. do an offline **shared-proposal audit** where every system receives the exact same BASE proposal for the same task/model/regime/seed.

This is one of the most important remaining methodological fixes.

### 4. The controlled split has 100% raw success

The native block helps, but the controlled headline still has 100% raw success. That is okay only if framed as:

> “controlled successful-trace least-effect certification,”

not as:

> “realistic task-solving benchmark.”

τ-bench itself evaluates dynamic user-agent-tool interactions using domain APIs, policies, final database state, and pass^k reliability, so reviewers will expect you to be precise about whether you are doing native task solving or a controlled adapter study. ([arXiv][4]) ToolSandbox similarly emphasizes stateful tool execution and intermediate/final milestones, so do not overclaim full upstream re-hosting from a compact native-style subset. ([Apple Machine Learning Research][5])

### 5. Projection baselines must be called “projections,” not SOTA systems

Your projection table is useful, but it is not a faithful reproduction of CORE/MiniScope/ContractGuard/etc. You can say:

> “We instantiate deterministic projections corresponding to final-state, path-validity, permission, contract/menu, and revisability predicates.”

Do not say:

> “We beat SOTA systems.”

The safer paper claim is stronger anyway: those predicates are **semantically incomplete projections** of the effect kernel.

## More experiments to run

### Must-run / highest ROI: shared-proposal audit

This is mostly offline and should be done before submission.

**Goal:** prove the guard comparison is not caused by models seeing different `system` labels.

Recommended audit:

```text
For each task_id × model × regime × seed:
  take the BASE model proposal
  replay PROJ_GUARD_V2 and EFFECTGUARD_V2 from that same proposal
  rescore with canonical enumerated-frontier certificates
```

Expected pass condition:

```text
BASE strict-excess remains high.
PROJ_GUARD_V2 leaves nonzero residual strict-excess.
EFFECTGUARD_V2 remains near-zero strict-excess.
No-oracle checks remain 100%.
```

This may require **zero GPU** if you reuse saved BASE proposals. If you want the cleaner version, rerun only the BASE proposal calls with `system=` removed, then replay guards offline. That is **7,168 model calls**, not 21,504.

### Strongly recommended: necessary-high / incomparable stress block

This is the one extra GPU experiment I would run if you want a better EACL shot.

Use:

```text
32 stress tasks × 4 regimes × 2 seeds × 4 models × 3 systems
= 3,072 trajectories
```

Task types:

| Stress type                         | Purpose                                                                                                                              |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Necessary-high**                  | Lower-effect alternatives violate policy or fail terminal equivalence. EffectGuard must permit escalation.                           |
| **Incomparable tradeoff**           | One trace reduces user burden but increases write/observability, or vice versa. Kernel should label incomparable, not strict-excess. |
| **Contract-required high artifact** | Byte-bound or expiring artifact is necessary; lower stable-token path should fail.                                                   |
| **Fraud/legal/escalation**          | External notification or account lock is necessary because policy obligation demands it.                                             |

Pass conditions:

```text
necessary-high labels are nonzero and replayable
incomparable labels are nonzero and replayable
EffectGuard permits necessary-high escalation
false-denial remains <= 5-10%
strict-excess reduction still holds
```

This directly answers the obvious reviewer attack:

> “Your method just always prefers low-effect actions.”

### Offline analysis to add: leave-one-model / leave-one-family robustness

No GPU needed.

Report:

```text
headline raw-vs-kernel gap after dropping each model
headline raw-vs-kernel gap after dropping each family
EffectGuard/projection delta after dropping each model/family
```

Pass condition:

```text
BASE raw-kernel gap remains >= 10 pp in every leave-one-out slice.
Projection residual strict-excess remains nonzero in every meaningful slice.
```

This is useful because Qwen behaves differently from Mistral/Llama/Gemma in the native subset. You want to show the result is not a one-model artifact.

### Optional: expand native subset

Only do this if the paper is otherwise done.

Current native subset:

```text
48 tasks × 4 regimes × 2 seeds × 4 models × 3 systems = 4,608
```

Optional expansion:

```text
96 tasks × 4 regimes × 2 seeds × 4 models × 3 systems = 9,216
```

This would make the native validation harder to dismiss. But I would prioritize **shared-proposal audit** and **necessary-high/incomparable stress** first.

## Experiments I would not run

Do **not** add more models. Your model grid is already defensible. Adding more Qwen/Phi/etc. will not solve the remaining weakness.

Do **not** run human eval right now. Your claim is certificate/replay semantics, not subjective human preference.

Do **not** revive Bedrock/frontier claims.

Do **not** use lattice sensitivity as a main result. Your own Stage 7 correctly freezes it as appendix/diagnostic only because all variants are exactly invariant.

Do **not** submit the old 204,800-episode framing.

## Submission readiness

### As-is

**No.** The current PDF would probably get rejected because it still contains stale claims and unsupported experiment text.

### If you only rewrite, no more experiments

**Maybe submittable.** The artifact is strong enough for a serious ARR attempt if the paper is honest and tight. Main risk: reviewers may say the controller is too deterministic and the controlled benchmark is too synthetic.

### If you rewrite + shared-proposal audit

**Much stronger.** This removes the most obvious methodological confound.

### If you rewrite + shared-proposal audit + necessary-high/incomparable stress block

**Best version under your 4×L40 constraints.** This is the version I would actually submit to ARR/EACL.

## What the final EACL paper should say

Use this abstract-level claim:

> We introduce Effect Kernels, a certificate semantics for least-effect tool-agent evaluation. Given a successful tool trace, the verifier enumerates admissible task-equivalent alternatives and certifies whether the trace is nondominated, strictly dominated by a lower-effect witness, or incomparable. Across 21,504 local open-weight controlled trajectories, BASE agents show a 57.0-point gap between final-state success and certified least-effect success. Projection-only safeguards reduce but do not eliminate strict-excess, while an effect-aware no-oracle reference controller reaches the canonical frontier in the controlled split. A 4,608-trajectory native-fidelity validation block, 11,508 replayed bundles, no-oracle sentinels, and targeted CEGAR stress support the auditability of the certificates.

That is clean. It avoids fake frontier/SOTA overclaiming.

## Tables to include in the main paper

| Table                           | Content                                                                                                                               |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **T1: Semantic lift**           | Final-state / path / permission / contract / menu / revisability predicates vs effect-kernel certificate question.                    |
| **T2: Dataset and model grid**  | 128 controlled tasks, 7 regimes, 4 local models, 3 systems; separate 48-task native validation.                                       |
| **T3: Controlled main results** | BASE 57.0033% strict-excess; PROJ_GUARD_V2 7.3242%; EFFECTGUARD_V2 0.0000%.                                                           |
| **T4: Projection loss**         | FINAL_STATE/CORE 21.44% residual; MiniScope/contract/revisability/modern-stack projections leave residual; KERNEL_FULL 0%.            |
| **T5: Native validation**       | BASE 81.58% raw native success, PROJ 92.97%, EffectGuard 100%; strict-excess among successes.                                         |
| **T6: Audit/reproducibility**   | canonical enumeration, replay, CEGAR, no-oracle, Qwen repair sensitivity, cost.                                                       |
| **T7 if stress run added**      | necessary-high/incomparable stress: EffectGuard permits necessary escalation and does not collapse all high-effect cases into errors. |

## Final recommendation

Do **not** run more general model experiments. The main point is across.

Run only these, in order:

```text
1. Shared-proposal / no-system-leak audit.
2. Necessary-high + incomparable stress block, if time.
3. Leave-one-model and leave-one-family offline robustness.
4. Rewrite the paper from scratch around the final claim registry.
```

Then submit to **ARR Aug 3, 2026 for EACL 2027**. The EACL 2027 page lists Aug 3, 2026 as the ARR deadline, with author response in September, meta-reviews Oct 8, commitment Oct 11, and notification Nov 12. ([EACL 2027][1])

With the artifact as-is plus a correct rewrite, this is a credible EACL attempt. With the two small extra audits, it becomes much harder for reviewers to dismiss. Still not guaranteed, but this is now in the zone where the paper’s success depends more on **claim discipline and writing** than on more GPUs.

[1]: https://2027.eacl.org/calls/papers/?utm_source=chatgpt.com "EACL 2027 Call for Main Conference Papers"
[2]: https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506?utm_source=chatgpt.com "mistralai/Mistral-Small-3.2-24B-Instruct-2506"
[3]: https://aclrollingreview.org/cfp?utm_source=chatgpt.com "CALL FOR PAPERS – ACL Rolling Review"
[4]: https://arxiv.org/abs/2406.12045?utm_source=chatgpt.com "$τ$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains"
[5]: https://machinelearning.apple.com/research/toolsandbox-stateful-conversational-llm-benchmark?utm_source=chatgpt.com "ToolSandbox: A Stateful, Conversational, Interactive ..."
