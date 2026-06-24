# Native Source Audit

PASS: every manifest family has pinned provenance or an explicit declared synthetic status.

| family | adapter_status | manifest_rows | unique_base_tasks | unique_source_records | unique_source_hashes | record_count | source_benchmarks | adapter_statuses | source_commits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| delegated_docs | declared_synthetic_controlled_family | 5376 | 32 | 32 | 32 | 64 | effectbench-delegated-docs-synthetic-v1 | declared_synthetic_controlled_family | effectbench_omega_synthetic_v1 |
| tau_airline | source_backed_literal_task | 5376 | 32 | 32 | 32 | 50 | tau-bench-airline | source_backed_literal_task | 59a200c6d575d595120f1cb70fea53cef0632f6b |
| tau_retail | source_backed_literal_task | 5376 | 32 | 32 | 32 | 115 | tau-bench-retail | source_backed_literal_task | 59a200c6d575d595120f1cb70fea53cef0632f6b |
| telecom | source_backed_json_task | 5376 | 32 | 32 | 32 | 2285 | tau2-bench-telecom | source_backed_json_task | 5ebebbe827b455b3ed04fcb9294235c6ef4e5fd6 |
| toolsandbox_contract | source_backed_scenario_extension | 5376 | 32 | 32 | 32 | 129 | apple-ToolSandbox | source_backed_scenario_extension | 165848b9a78cead7ca7fe7c89c688b58e6501219 |

Interpretation: `declared_synthetic_controlled_family` applies only to delegated-docs; other benchmark families are source-backed by pinned upstream artifacts.
