# Stage 7 Lattice Policy Freeze

Decision: use the fixed declared Pareto lattice for all main claims.

The current lattice sensitivity tables preserve the headline sign, but the
reported strict-excess rates are exactly invariant across the configured
weight/name variants. Under the rescue plan, this is not strong enough to
support a main-paper value-governance sensitivity claim. The defensible
paper treatment is to move lattice sensitivity to an appendix/diagnostic
or omit it from main claims, and state that alternatives to the declared
Pareto lattice are future work.

| Split | Variants | Unique strict-excess rates | Policy |
|---|---:|---:|---|
| `main_mc_postfix_all_local_canonical` | 6 | 1 | appendix diagnostic only |
| `guard_v2_main_with_base_all_local_canonical` | 6 | 1 | appendix diagnostic only |
| `native_subset_v1_all_local_canonical` | 6 | 1 | appendix diagnostic only |

Main-paper rule:

```text
Do not claim robustness across alternative value lattices from these
tables. Claim only that all reported strict-excess labels use the fixed
declared Pareto lattice in the effect schema, with incomparability
reported separately.
```
