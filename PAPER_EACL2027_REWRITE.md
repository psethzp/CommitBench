# Effect Kernels for Least-Effect Tool-Agent Evaluation

This is the submission-facing rewrite scaffold. It replaces the stale historical
PDF framing and should be used as the source of truth for the next manuscript
draft.

## Abstract Draft

Tool-agent evaluations usually ask whether an agent reached a correct final
state. For many real workflows, however, multiple successful traces can differ
substantially in privacy exposure, write scope, reversibility, user burden, and
contract fragility. We introduce Effect Kernels, a certificate semantics for
least-effect evaluation of successful tool-agent traces. Given a task and a
successful trace, the verifier enumerates admissible task-equivalent
alternatives and certifies whether the trace is nondominated, strictly
dominated by a lower-effect witness, necessary-high, or incomparable. Across a
21,504-trajectory local open-weight suite, final-state success substantially
overstates certified least-effect success: the fresh no-system-prompt paired
audit gives BASE a 56.2-point strict-excess rate among successful traces.
Projection-only safeguards reduce but do not remove residual strict excess,
while an effect-aware no-oracle reference controller removes residual strict
excess in this scaffold. Native validation, stress replay, CEGAR audits,
leave-one robustness, and deterministic replay bundles support auditability.

## Main Claim

The paper is not a new leaderboard. The paper is a certificate-semantics paper:

> Among task-equivalent successful tool-agent traces, final-state success,
> path validity, least privilege, contract checks, local tool-menu filtering,
> and revisability predicates can still accept strictly Pareto-dominated
> traces. An Effect Kernel provides auditable witness certificates, and a
> no-oracle reference controller demonstrates that the certificates can guide
> online lower-effect substitution in a local open-weight scaffold.

## Main Evidence

| Evidence | Result | Use in paper |
|---|---:|---|
| Controlled split | 21,504 trajectories | Main denominator |
| Fresh shared-proposal v3 audit | 21,504 traces, 7,168 paired groups | Clean guard comparison |
| BASE strict-excess | 56.2081% | Final-state vs kernel gap |
| `PROJ_GUARD_V2` residual strict-excess | 8.4961% | Projection-loss result |
| `EFFECTGUARD_V2` strict-excess | 0.0000% | Reference-controller demonstration |
| Canonical enumeration | 0 unexplained mismatches | Paper-grade verifier gate |
| Full stress replay | 3,072 bundles, 0 failures | Necessary-high/incomparable audit |
| Native validation | 4,608 traces | Shows terminal success can fail |
| Leave-one robustness | 49 gate rows, 0 failures | Not one model/family artifact |
| No-oracle audit | 21,504/21,504 pass in v3 | Runtime/evaluator separation |

## Main Tables And Figures

Use at most six main tables/figures:

1. Effect Kernel pipeline: trace to effect ledger to enumerated frontier to certificate.
2. Semantic lift: final state, path, permission, contract, menu, and revisability predicates versus the kernel question.
3. Dataset/model grid: controlled, native validation, stress, and four local models.
4. Main controlled and v3 shared-proposal results.
5. Projection-loss table.
6. Audit table: enumeration, replay, CEGAR, no-oracle, stress, and leave-one robustness.

Move model-specific, family/regime, and sensitivity breakdowns to the appendix.

## Methods Wording

Use:

- "deterministic projection baselines";
- "local/open-weight controlled suite";
- "fresh no-system-prompt paired proposal audit";
- "canonical enumerated-frontier certificates";
- "no-oracle reference controller";
- "native-fidelity validation block."

Avoid:

- "frontier leaderboard";
- "human-evaluation validation";
- "faithful reproduction of prior systems";
- "universal online optimality";
- "commercial model coverage";
- "alternate-lattice robustness" as a main claim.

## Limitations

- The headline evidence is local/open-weight only.
- The controlled split is a successful-trace certification scaffold, not a
  task-solving benchmark replacement.
- Native validation is compact and source-backed, but not a full re-host of all
  upstream benchmark servers.
- Projection baselines are semantic projections, not faithful reproductions of
  named systems.
- `EFFECTGUARD_V2` is a reference controller in this scaffold, not a universal
  agent policy.
- Main claims use the declared Pareto lattice; alternate lattices are appendix
  diagnostics only.
- Deterministic replay replaces human audit in this version.

## Final Packaging Notes

The final anonymous artifact zip excludes the stale historical PDF and
presentation deck. Regenerate a new PDF from the rewritten manuscript before
submission; do not submit the historical PDF.
