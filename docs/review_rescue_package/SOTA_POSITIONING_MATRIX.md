# SOTA_POSITIONING_MATRIX.md — exact novelty boundary

Use this table to rewrite Related Work and the novelty-boundary table. The goal is not to claim prior work is weak. The goal is to state precisely that prior work answers local/runtime/projection questions, while EffectKernelBench adds post-hoc complete-trace Pareto certification with replayable witnesses.

| Prior line | What it already does | Why it is close | What our paper may still add | Required baseline / treatment |
|---|---|---|---|---|
| tau-bench / tau2 / tau3 | Dynamic tool-agent-user tasks with APIs, policies, final database-state evaluation, pass^k-style reliability. | Reviewers know this as the standard customer-service substrate. | We do not replace it; we add least-effect certification over successful traces. | Cite and treat as substrate/final-state baseline. |
| ToolSandbox | Stateful tool execution, implicit dependencies, intermediate/final milestones, on-policy user simulation. | Already studies trajectory and stateful tool behavior. | We add Pareto effect witnesses for task-equivalent successes. | Cite; optionally use native validation/bridge. |
| Multi-turn degradation / Laban-style regimes | Shows LLM degradation under information-equivalent multi-turn regimes. | Our FULL/CONCAT/SHARDED/SNOWBALL/REVISE-like regimes derive motivation from this. | We measure effect excess, not only answer/task degradation. | Cite in setup, not novelty. |
| AgentDojo | Dynamic environment for attacks/defenses, untrusted tool outputs, prompt injection security tests. | Strong realistic agent safety benchmark. | Our question is not injection robustness; it is whether successful traces use dominated effects. | Cite as safety benchmark; no need to reimplement unless doing external bridge. |
| ToolEmu | Emulated high-stakes tools and safety evaluator for LM-agent risks. | Directly about side-effect risk. | Our labels are deterministic witness certificates, not LM-judge risk evaluations. | Cite; contrast emulator/judge vs enumerated witness. |
| ToolSword | Safety failures in tool learning/risky scenarios. | Tool safety benchmark line. | Our contribution is complete-trace dominance certification. | Cite in safety related work. |
| MobileSafetyBench | Safety/helpfulness tradeoffs for mobile agents; misuse/negative side effects. | Directly about side effects and safety tradeoffs. | Our setting is closed/wrapped tools with effect certificates. | Cite. |
| SafeAgentBench | Embodied-agent safety hazards/task planning. | Safety benchmark context. | Our focus is transactional tool traces and Pareto witnesses. | Cite. |
| Progent | Programmable privilege control via fine-grained tool-call policies/fallbacks. | Least privilege and blocking unnecessary actions overlaps strongly. | Progent controls permissions/actions at runtime; our certificate compares full successful traces across multiple effect dimensions and supplies lower-effect witnesses. | Implement `PROGENT_DSL_LITE`; cite as closest privilege-control method. |
| ToolChoiceConfusion / CMTF | Exposes only causally necessary next-step tool frontier using precondition/effect contracts. | Very close to local minimal tool exposure. | CMTF minimizes current visible tool frontier; our certificate asks whether the complete successful trace is dominated after all steps. | Implement `CMTF_CONTRACT`. |
| RACG | Risk-aware least-privilege tool exposure with risk labels and authorization preconditions. | Close to high-risk action gating. | RACG controls visibility/authority; our kernel compares non-exposure dimensions too: write scope, reversibility, observability, compensation, burden, contract fragility. | Implement `RACG_LITE`. |
| ToolPrivBench | Tests whether agents pick higher-privilege tools despite lower-privilege sufficient alternatives. | Very close to lower-privilege alternative concept. | ToolPrivBench focuses on privilege; our witness relation spans full effect vectors and complete traces. | Implement `TOOLPRIV_DETECTOR` and cite strongly. |
| Cordon | Semantic transactions, staging, validation, rollback, outbox, audit for irreversible effects. | Close to transactional side effects and commit boundaries. | Cordon prevents premature/unsafe commits; our kernel asks whether the committed successful transaction is dominated by a lower-effect one. | Implement `CORDON_LITE`. |
| SkillGuard | Permission framework for skills, regulating context influence and action side effects. | Strong permission/side-effect governance line. | SkillGuard governs skill artifacts; our contribution is trace-level certificate after task execution. | Cite; include `SKILL_PERMISSION` if skills exist, otherwise discuss only. |

## Wording to use

> These systems are not strawmen. They solve complementary runtime and evaluation problems: privilege control, causal tool exposure, authorization, transaction containment, safety testing, and stateful task success. EffectKernelBench asks a narrower but different question: after a task-equivalent success exists, can the observed complete trace be certified as nondominated, or does there exist a replayable lower-effect witness?

## Wording to avoid

- “Prior work ignores side effects.”
- “No one has studied least privilege.”
- “Our controller beats all prior systems.”
- “CMTF/RACG/Progent are just baselines.”
