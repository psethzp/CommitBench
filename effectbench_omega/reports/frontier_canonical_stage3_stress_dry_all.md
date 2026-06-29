# Enumerated Frontier Completeness Audit

groups: 1024
observed_successes: 3072
enumerated_candidates: 1344
frontier_candidates: 1344
old_strict_excess: 0
enumerated_strict_excess: 0
label_agreement: 0.687500
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
