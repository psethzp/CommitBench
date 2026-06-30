# Review-rescue package for EffectKernelBench / CommitBench

This package contains the concrete post-review action plan, agent handoff, configuration, and submission gates for turning the current local-only Effect Kernel paper into a defensible ARR/EACL submission.

Recommended public paper name: **EffectKernelBench** or **TraceKernelBench**. Avoid the title **CommitBench** because there is already a commit-message-generation benchmark with that name.

Files:

- `PLAN.md` — prioritized next steps, timeline, acceptance gates, and what not to do.
- `AGENTS.md` — agent-by-agent instructions for implementation, artifact cleanup, paper rewrite, baselines, validation, and final checks.
- `rescue_config.yaml` — machine-readable configuration for the final rescue run/audits.
- `SOTA_POSITIONING_MATRIX.md` — how to position against close prior work.
- `BASELINE_SPECS.md` — exact deterministic baselines to add without expensive new model runs.
- `ANNOTATION_PROTOCOL.md` — human/domain-expert validation protocol for effect labels and witness preference.
- `ARTIFACT_REQUIREMENTS.md` — exact final artifact contents and commands that must pass.
- `PAPER_REWRITE_BLUEPRINT.md` — submission narrative and section-level rewrite plan.
- `FINAL_SUBMISSION_GATE.md` — final pre-submission checklist.

Core decision: **do not run more broad model sweeps.** The review’s strongest objections are SOTA positioning, artifact reproducibility, direct baselines, human/expert validation, uncertainty, and EffectGuard framing.
