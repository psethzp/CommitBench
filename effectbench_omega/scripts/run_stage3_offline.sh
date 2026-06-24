#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

SPLIT="${SPLIT:-main_mc_postfix_all_local}"
OUT_DIR="${OUT_DIR:-effectbench_omega/outputs/${SPLIT}}"
JOB_ID="${JOB_ID:-stage3_${SPLIT}_$(date -u +%Y%m%dT%H%M%SZ)}"
JOB_DIR="effectbench_omega/jobs/${JOB_ID}"
LOG_DIR="${JOB_DIR}/logs"
EVENTS="${JOB_DIR}/events.tsv"
PYTHON="${PYTHON:-.venv/bin/python}"

mkdir -p "${LOG_DIR}" effectbench_omega/tables effectbench_omega/reports effectbench_omega/witness_bundles
ln -sfn "${JOB_ID}" effectbench_omega/jobs/stage3_latest

timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

event() {
  local step="$1"
  local status="$2"
  local detail="$3"
  printf "%s\t%s\t%s\t%s\n" "$(timestamp)" "${step}" "${status}" "${detail}" >>"${EVENTS}"
}

run_step() {
  local step="$1"
  shift
  local log_file="${LOG_DIR}/${step}.log"
  event "${step}" "running" "$*"
  "$@" >"${log_file}" 2>&1
  event "${step}" "done" "log ${log_file}"
}

printf "timestamp\tstep\tstatus\tdetail\n" >"${EVENTS}"
{
  echo "job_id=${JOB_ID}"
  echo "split=${SPLIT}"
  echo "out_dir=${OUT_DIR}"
  echo "python=${PYTHON}"
} >"${JOB_DIR}/job.env"

if [[ ! -f "${OUT_DIR}/traces.parquet" ]]; then
  event "stage3" "failed" "missing ${OUT_DIR}/traces.parquet"
  exit 1
fi

run_step kernel_verifier \
  "${PYTHON}" effectbench_omega/effectbench/kernel/verifier.py \
    --traces "${OUT_DIR}/traces.parquet" \
    --schemas effectbench_omega/schemas \
    --out "${OUT_DIR}/kernel"

run_step no_oracle_report \
  "${PYTHON}" effectbench_omega/effectbench/audit/no_oracle_report.py \
    --runtime-logs "${OUT_DIR}/runtime_logs.parquet" \
    --out "effectbench_omega/tables/no_oracle_${SPLIT}.csv"

run_step projection_loss \
  "${PYTHON}" effectbench_omega/effectbench/baselines/project.py \
    --traces "${OUT_DIR}/traces.parquet" \
    --certificates "${OUT_DIR}/kernel/certificates.parquet" \
    --baselines FINAL_STATE CORE_DFA MINISCOPE_PERMISSION CONTRACT_MENU_CMTF REVISABILITY MODERNSTACK_PROJECTION KERNEL_FULL \
    --out "effectbench_omega/tables/projection_loss_${SPLIT}.csv" \
    --reason-out "effectbench_omega/tables/projection_loss_${SPLIT}_reasons.csv"

run_step cegar \
  "${PYTHON}" effectbench_omega/effectbench/audit/cegar.py \
    --traces "${OUT_DIR}/traces.parquet" \
    --schemas effectbench_omega/schemas \
    --omit-fields outbox policy_obligation contract_artifact_hash virtual_clock memory_cache user_visible_exposure compensation_or_payment_hold \
    --out "effectbench_omega/tables/cegar_rejections_${SPLIT}.csv" \
    --label-changes "effectbench_omega/tables/cegar_label_changes_${SPLIT}.csv"

run_step lattice_sensitivity \
  "${PYTHON}" effectbench_omega/effectbench/metrics/lattice_sensitivity.py \
    --certificates "${OUT_DIR}/kernel/certificates.parquet" \
    --lattices effectbench_omega/configs/lattices \
    --out "effectbench_omega/tables/lattice_sensitivity_${SPLIT}.csv"

run_step bootstrap \
  "${PYTHON}" effectbench_omega/effectbench/metrics/bootstrap.py \
    --certificates "${OUT_DIR}/kernel/certificates.parquet" \
    --group-by task_id model seed family \
    --methods paired_bootstrap task_cluster hierarchical \
    --out "effectbench_omega/tables/uncertainty_${SPLIT}.csv" \
    --n-bootstrap 2000 \
    --seed 13

run_step guard_tie \
  "${PYTHON}" effectbench_omega/effectbench/audit/guard_tie.py \
    --traces "${OUT_DIR}/traces.parquet" \
    --certificates "${OUT_DIR}/kernel/certificates.parquet" \
    --out "effectbench_omega/tables/guard_tie_${SPLIT}.csv" \
    --details-out "effectbench_omega/tables/guard_tie_${SPLIT}_details.csv"

run_step replay_bundles \
  "${PYTHON}" effectbench_omega/effectbench/audit/replay_bundles.py \
    --certificates "${OUT_DIR}/kernel/certificates.parquet" \
    --traces "${OUT_DIR}/traces.parquet" \
    --sample strict_excess=100 minimal=60 incomparable=60 necessary_high=30 \
    --out "effectbench_omega/witness_bundles/${SPLIT}"

run_step replay_certificates \
  "${PYTHON}" effectbench_omega/effectbench/audit/replay_certificates.py \
    --bundle-dir "effectbench_omega/witness_bundles/${SPLIT}" \
    --out "effectbench_omega/reports/certificate_replay_${SPLIT}.md" \
    --strict

run_step cost_audit \
  "${PYTHON}" effectbench_omega/effectbench/metrics/cost_audit.py \
    --logs "${OUT_DIR}/api_logs.jsonl" \
    --out "effectbench_omega/reports/${SPLIT}_cost.md" \
    --final

run_step aggregate \
  "${PYTHON}" effectbench_omega/effectbench/metrics/aggregate.py \
    --main-certificates "${OUT_DIR}/kernel/certificates.parquet" \
    --projection-loss "effectbench_omega/tables/projection_loss_${SPLIT}.csv" \
    --cost-logs "${OUT_DIR}/api_logs.jsonl" \
    --out-tables "effectbench_omega/tables/${SPLIT}" \
    --out-figures "effectbench_omega/figures/${SPLIT}" \
    --claim-registry "effectbench_omega/metrics/claim_registry_${SPLIT}.csv"

run_step no_oracle_pytest \
  "${PYTHON}" -m pytest -q effectbench_omega/tests/no_oracle

event "stage3" "done" "offline suite complete for ${SPLIT}"
