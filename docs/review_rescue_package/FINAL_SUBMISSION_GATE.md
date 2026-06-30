# FINAL_SUBMISSION_GATE.md — pass/fail checklist before ARR/EACL upload

## Gate 1 — Scope and title

- [ ] Paper no longer titled `CommitBench`.
- [ ] Title/abstract say complete-trace Pareto certificates / replayable witnesses.
- [ ] Paper does not claim broad firstness over all least-effect/privilege work.
- [ ] EffectGuard is called a reference controller or constructive upper bound.

## Gate 2 — Related work

- [ ] tau-bench/tau2/tau3 discussed.
- [ ] ToolSandbox discussed.
- [ ] Multi-turn degradation regimes discussed.
- [ ] AgentDojo discussed.
- [ ] ToolEmu discussed.
- [ ] ToolSword discussed.
- [ ] MobileSafetyBench/SafeAgentBench discussed if space.
- [ ] Progent discussed.
- [ ] CMTF/ToolChoiceConfusion discussed.
- [ ] RACG discussed.
- [ ] ToolPrivBench discussed.
- [ ] Cordon discussed.
- [ ] SkillGuard discussed.
- [ ] Novelty table states exact difference for each.

## Gate 3 — Experiments and baselines

- [ ] Final paired-control split uses fresh local model proposals or clearly documents provenance.
- [ ] Direct baselines include Progent-lite, CMTF, RACG-lite, ToolPriv detector, Cordon-lite, final-state.
- [ ] Main tables include CIs or robustness intervals.
- [ ] Native validation is framed as validation, not headline.
- [ ] Stress split appears in main paper or prominent appendix.
- [ ] Human/expert validation appears in main paper or prominent appendix.

## Gate 4 — Artifact

Run:

```bash
python -m zipfile -t EffectKernelBench_artifact.zip
unzip -t EffectKernelBench_artifact.zip
python scripts/reproduce.py --check-only
python scripts/reproduce.py --tables
python scripts/run_online.py --help
python scripts/run_fresh_smoke.py --config configs/fresh_smoke.yaml
python scripts/build_baselines.py --config configs/baselines.yaml
python scripts/verify_claim_registry.py --registry metrics/claim_registry.csv
pytest -q tests
```

All must pass.

## Gate 5 — Stale-term scan

Search paper and artifact for:

```text
CommitBench
v1
v2
v3
legacy
minimal_plus
workflow_smoke
Bedrock
GPT-5
Claude
Gemini
204,800
20,480
faithful SOTA
best paper
guaranteed
/home/ubuntu
/mnt/data
nachiket
```

Every occurrence must be either removed or justified in `FINAL_SUBMISSION_REPORT.md`.

## Gate 6 — Formatting

- [ ] ARR/ACL official style used.
- [ ] Long paper content <= 8 pages.
- [ ] Limitations section present in main paper.
- [ ] References not counted in content page limit.
- [ ] Figures readable at 100% zoom.
- [ ] PDF fonts embedded.
- [ ] No author IDs in anonymized version.

## Gate 7 — Final decision

Submit only if all are true:

```text
artifact checks pass
claim registry complete
fresh model provenance or explicit weaker claim
human/expert validation complete
direct baselines complete
uncertainty complete
paper fits 8 pages
related work rewritten
no stale claims
```

If not, delay to the next ARR cycle.
