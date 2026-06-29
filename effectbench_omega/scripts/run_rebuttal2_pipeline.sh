#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

PIPELINE_JOB_ID="${PIPELINE_JOB_ID:-rebuttal2_pipeline_$(date -u +%Y%m%dT%H%M%SZ)}"
QUEUE_JOB_ID="${QUEUE_JOB_ID:-rebuttal2_base_nosystem_v1_$(date -u +%Y%m%dT%H%M%SZ)}"
PIPELINE_DIR="effectbench_omega/jobs/${PIPELINE_JOB_ID}"
LOG_DIR="${PIPELINE_DIR}/logs"
EVENTS="${PIPELINE_DIR}/events.tsv"
PYTHON="${PYTHON:-.venv/bin/python}"

mkdir -p "${LOG_DIR}" effectbench_omega/reports effectbench_omega/tables
ln -sfn "${PIPELINE_JOB_ID}" effectbench_omega/jobs/rebuttal2_latest

timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

event() {
  local step="$1"
  local status="$2"
  local detail="$3"
  printf "%s\t%s\t%s\t%s\n" "$(timestamp)" "${step}" "${status}" "${detail}" >>"${EVENTS}"
  printf "%s\n" "${step}" >"${PIPELINE_DIR}/current_step"
  printf "%s\n" "${status}" >"${PIPELINE_DIR}/current_status"
  printf "%s\n" "${detail}" >"${PIPELINE_DIR}/current_detail"
}

run_step() {
  local step="$1"
  shift
  local log_file="${LOG_DIR}/${step}.log"
  event "${step}" "running" "$*"
  "$@" >"${log_file}" 2>&1
  event "${step}" "done" "log ${log_file}"
}

write_online_control() {
  "${PYTHON}" - <<'PY'
from pathlib import Path
import pandas as pd

root = Path(".")
split = root / "effectbench_omega/outputs/shared_proposal_v3_nosystem_all_local"
traces = pd.read_parquet(split / "traces.parquet")
certs = pd.read_parquet(split / "kernel_canonical/certificates_enumerated.parquet")
rows = []
for system, group in traces.groupby("system"):
    system = str(system)
    successes = int(group["terminal_success"].sum())
    trajectories = int(len(group))
    sc = certs[certs["system"].astype(str).eq(system)]
    strict = int(sc["verdict"].astype(str).eq("strict_excess").sum())
    kernel = successes - strict
    rows.append(
        {
            "system": system,
            "trajectories": trajectories,
            "raw_success_rate": successes / trajectories if trajectories else 0.0,
            "canonical_strict_excess": strict,
            "canonical_strict_excess_rate": strict / successes if successes else 0.0,
            "canonical_kernel_success": kernel,
            "canonical_kernel_success_rate": kernel / successes if successes else 0.0,
        }
    )
out = root / "effectbench_omega/tables/shared_proposal_v3_nosystem_online_control.csv"
pd.DataFrame(rows).sort_values("system").to_csv(out, index=False)
print(out)
PY
}

check_acceptance_gates() {
  "${PYTHON}" - <<'PY'
from pathlib import Path
import json
import pandas as pd

errors = []
online = pd.read_csv("effectbench_omega/tables/shared_proposal_v3_nosystem_online_control.csv")
by_system = {str(row["system"]): row for _, row in online.iterrows()}
base = by_system.get("BASE")
proj = by_system.get("PROJ_GUARD_V2")
effect = by_system.get("EFFECTGUARD_V2")
if base is None or int(base["trajectories"]) != 7168:
    errors.append("BASE traces != 7168")
if proj is None or effect is None:
    errors.append("missing V2 guard rows")
if base is not None and float(base["canonical_strict_excess_rate"]) < 0.50:
    errors.append("BASE strict-excess rate < 50%")
if proj is not None and float(proj["canonical_strict_excess_rate"]) < 0.05:
    errors.append("PROJ_GUARD_V2 residual strict-excess rate < 5%")
if effect is not None and float(effect["canonical_strict_excess_rate"]) > 0.005:
    errors.append("EFFECTGUARD_V2 strict-excess rate > 0.5%")
summary_path = Path("effectbench_omega/outputs/shared_proposal_v3_nosystem_all_local/shared_proposal_summary.json")
summary = json.loads(summary_path.read_text())
if summary.get("split_trace_count") != 21504:
    errors.append("shared replay traces != 21504")
if summary.get("complete_shared_source_groups") != 7168:
    errors.append("complete shared groups != 7168")
frontier = pd.read_csv("effectbench_omega/tables/frontier_canonical_shared_proposal_v3_nosystem_all_local_canonical.csv")
if int(frontier.get("unexplained_mismatches", pd.Series([0])).sum()) != 0:
    errors.append("canonical unexplained mismatches != 0")
no_oracle = pd.read_csv("effectbench_omega/tables/no_oracle_shared_proposal_v3_nosystem_all_local_canonical.csv")
oracle_failures = int(no_oracle.get("oracle_failures", no_oracle.get("forbidden_oracle_rows", pd.Series([0]))).sum())
if oracle_failures != 0:
    errors.append("no-oracle failures != 0")
report = {
    "errors": errors,
    "passed": not errors,
    "online_control": online.to_dict(orient="records"),
}
Path("effectbench_omega/reports/rebuttal2_acceptance_gates.json").write_text(
    json.dumps(report, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
if errors:
    raise SystemExit("; ".join(errors))
print(json.dumps(report, indent=2, sort_keys=True))
PY
}

create_archive() {
  local archive="CommitBench_rebuttal2_experiment_proof_$(date -u +%Y%m%d).zip"
  rm -f "${archive}"
  (
    cd ..
    zip -r -9 "CommitBench/${archive}" CommitBench \
      -x 'CommitBench/.git/*' \
      -x 'CommitBench/.venv/*' \
      -x 'CommitBench/.env' \
      -x 'CommitBench/.env.*' \
      -x 'CommitBench/.DS_Store' \
      -x 'CommitBench/.pytest_cache/*' \
      -x 'CommitBench/**/__pycache__/*' \
      -x 'CommitBench/**/*.pyc' \
      -x 'CommitBench/effectbench_omega/models/*' \
      -x 'CommitBench/effectbench_omega/upstreams/*' \
      -x 'CommitBench/*.zip'
  )
  sha256sum "${archive}" >"effectbench_omega/reports/rebuttal2_archive_sha256.txt"
  stat -c '%n %s bytes' "${archive}" >"effectbench_omega/reports/rebuttal2_archive_stat.txt"
  unzip -tq "${archive}" >"${LOG_DIR}/archive_integrity.log"
  printf "%s\n" "${archive}" >"${PIPELINE_DIR}/archive_name"
}

main() {
  printf "timestamp\tstep\tstatus\tdetail\n" >"${EVENTS}"
  printf "%s\n" "$$" >"${PIPELINE_DIR}/pipeline.pid"
  {
    echo "pipeline_job_id=${PIPELINE_JOB_ID}"
    echo "queue_job_id=${QUEUE_JOB_ID}"
    echo "root=${ROOT_DIR}"
    echo "skip_stage_5=1"
    echo "skip_stage_6=1"
  } >"${PIPELINE_DIR}/job.env"

  trap 'rc=$?; if (( rc != 0 )); then event "pipeline" "failed" "rc=${rc}; see ${LOG_DIR}"; "${PYTHON}" effectbench_omega/scripts/finalize_rebuttal2.py --pipeline-job-id "${PIPELINE_JOB_ID}" --queue-job-id "${QUEUE_JOB_ID}" --status failed >/dev/null 2>&1 || true; fi' EXIT

  run_step preflight_python_compile \
    "${PYTHON}" -m py_compile \
      effectbench_omega/scripts/build_shared_proposal_v2_audit.py \
      effectbench_omega/scripts/run_stage4_robustness.py \
      effectbench_omega/scripts/finalize_rebuttal2.py \
      effectbench_omega/scripts/run_online.py

  run_step base_nosystem_queue \
    env \
      JOB_ID="${QUEUE_JOB_ID}" \
      OUTPUT_PREFIX=base_nosystem_v1 \
      SPLIT_PREFIX=base_nosystem_v1 \
      REPORT_PREFIX=base_nosystem_v1 \
      MANIFEST=effectbench_omega/manifests/tasks_local_open.csv \
      QUEUE_SYSTEMS=BASE \
      SLICE_LIMIT=1792 \
      MODEL_CONTROLS_POLICY=1 \
      MODEL_PROPOSAL_MODE=actions \
      QUEUE_MODEL_TP=4 \
      CUDA_VISIBLE_DEVICES=0,1,2,3 \
      bash effectbench_omega/scripts/run_local_open_queue.sh

  run_step merge_base_nosystem \
    "${PYTHON}" effectbench_omega/scripts/merge_local_open_slices.py \
      --input-prefix effectbench_omega/outputs/base_nosystem_v1 \
      --out effectbench_omega/outputs/base_nosystem_v1_all_local \
      --expected-rows-per-model 1792

  run_step shared_proposal_v3_nosystem \
    "${PYTHON}" effectbench_omega/scripts/build_shared_proposal_v2_audit.py \
      --base-split effectbench_omega/outputs/base_nosystem_v1_all_local \
      --out effectbench_omega/outputs/shared_proposal_v3_nosystem_all_local \
      --split shared_proposal_v3_nosystem_all_local \
      --table-out effectbench_omega/tables/shared_proposal_v3_nosystem_audit.csv \
      --report-out effectbench_omega/reports/shared_proposal_v3_nosystem_audit.md \
      --shared-proposal-policy frozen_fresh_no_system_BASE_model_raw_output_replayed_to_all_systems \
      --proposal-prompt-caveat "fresh BASE proposals generated after the no-system prompt fix; proposal prompt user content does not expose the evaluated control-system label" \
      --residual-caveat "Fresh no-system-prompt BASE proposals are replayed to BASE, PROJ_GUARD_V2, and EFFECTGUARD_V2, removing the prior source-prompt caveat."

  run_step canonical_shared_proposal_v3 \
    env \
      JOB_ID="stage3_canonical_shared_proposal_v3_nosystem_$(date -u +%Y%m%dT%H%M%SZ)" \
      SPLIT=shared_proposal_v3_nosystem_all_local \
      TABLE_SUFFIX=shared_proposal_v3_nosystem_all_local_canonical \
      GUARD_TIE_SYSTEMS="PROJ_GUARD_V2 EFFECTGUARD_V2" \
      BOOTSTRAP_SYSTEMS="BASE PROJ_GUARD_V2 EFFECTGUARD_V2" \
      CANONICAL_CERT_MODE=enumerated \
      bash effectbench_omega/scripts/run_stage3_offline.sh

  run_step write_v3_online_control write_online_control
  run_step rebuttal2_acceptance_gates check_acceptance_gates
  run_step stage4_robustness_refresh "${PYTHON}" effectbench_omega/scripts/run_stage4_robustness.py
  run_step finalizer "${PYTHON}" effectbench_omega/scripts/finalize_rebuttal2.py --pipeline-job-id "${PIPELINE_JOB_ID}" --queue-job-id "${QUEUE_JOB_ID}" --status complete
  run_step pytest "${PYTHON}" -m pytest -q effectbench_omega/tests
  run_step claim_registry_check "${PYTHON}" effectbench_omega/effectbench/metrics/claim_registry_check.py --registry effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv
  run_step placeholder_scan "${PYTHON}" effectbench_omega/scripts/no_red_placeholders.py --root .
  run_step full_stress_replay_strict "${PYTHON}" effectbench_omega/effectbench/audit/replay_certificates.py --bundle-dir effectbench_omega/witness_bundles/stage3_stress_all_local_canonical_full --strict
  run_step archive create_archive

  event "pipeline" "done" "Rebuttal-2 stages 2/3/4/7 complete; archive recorded in ${PIPELINE_DIR}/archive_name"
}

main "$@"
