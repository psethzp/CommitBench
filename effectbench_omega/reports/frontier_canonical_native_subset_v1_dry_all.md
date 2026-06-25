# Enumerated Frontier Completeness Audit

groups: 1536
observed_successes: 3408
enumerated_candidates: 241664
frontier_candidates: 1536
old_strict_excess: 720
enumerated_strict_excess: 720
label_agreement: 1.000000
strictness_agreement: 1.000000
strictness_disagreements: 0
unexplained_mismatches: 0
spurious_legacy_witnesses: 0
enumerated_new_strict: 0
legacy_agreement_gate: True
canonical_gate: True
gate_mode: canonical
pass_gate: True

Legacy agreement gate uses strict-excess agreement because minimal vs minimal-with-incomparables is a subtype distinction.
Canonical gate requires zero unexplained mismatches; legacy disagreements are CEGAR/audit evidence, not a canonical-label failure.

No strictness disagreements.
