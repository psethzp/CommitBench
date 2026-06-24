# Qwen Repair Sensitivity

affected_rows: 168
rerun_rows: 168
original_repair_fallback_rows: 42
rerun_repair_fallback_rows: 42
proposal_changed_rows: 0
effect_vector_changed_rows: 0
verdict_changed_rows: 0
overall_strict_delta_pp: 0.000000
qwen_strict_delta_pp: 0.000000

Rerun used the existing run_online action-proposal prompt path with model_controls_policy, model_proposal_mode=actions, temperature=0, and the same logical rows/split trace IDs.

## Rerun Parse Status Counts

|                          |   count |
|:-------------------------|--------:|
| text_scan                |     126 |
| unparsed:repair_fallback |      42 |

## Outputs

- merged split: `effectbench_omega/outputs/qwen_repair_sensitivity_merged`
- table: `effectbench_omega/tables/qwen_repair_sensitivity.csv`
