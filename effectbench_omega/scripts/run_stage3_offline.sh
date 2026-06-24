#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

SPLIT="${SPLIT:-main_mc_postfix_all_local}"
OUT_DIR="${OUT_DIR:-effectbench_omega/outputs/${SPLIT}}"
TABLE_SUFFIX="${TABLE_SUFFIX:-${SPLIT}}"
CANONICAL_CERT_MODE="${CANONICAL_CERT_MODE:-enumerated}"
JOB_ID="${JOB_ID:-stage3_${SPLIT}_$(date -u +%Y%m%dT%H%M%SZ)}"
JOB_DIR="effectbench_omega/jobs/${JOB_ID}"
LOG_DIR="${JOB_DIR}/logs"
EVENTS="${JOB_DIR}/events.tsv"
PYTHON="${PYTHON:-.venv/bin/python}"
LEGACY_KERNEL_DIR="${OUT_DIR}/kernel_legacy_generated_trace"
CANONICAL_KERNEL_DIR="${OUT_DIR}/kernel_canonical"
LEGACY_CERTIFICATES="${LEGACY_KERNEL_DIR}/certificates.parquet"
CANONICAL_CERTIFICATES="${CANONICAL_KERNEL_DIR}/certificates_enumerated.parquet"
CERTIFICATES="${CANONICAL_CERTIFICATES}"
GUARD_TIE_SYSTEMS="${GUARD_TIE_SYSTEMS:-PROJ_GUARD EFFECTGUARD}"
BOOTSTRAP_SYSTEMS="${BOOTSTRAP_SYSTEMS:-}"

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
  echo "table_suffix=${TABLE_SUFFIX}"
  echo "canonical_cert_mode=${CANONICAL_CERT_MODE}"
  echo "python=${PYTHON}"
} >"${JOB_DIR}/job.env"

if [[ ! -f "${OUT_DIR}/traces.parquet" ]]; then
  event "stage3" "failed" "missing ${OUT_DIR}/traces.parquet"
  exit 1
fi

if [[ "${CANONICAL_CERT_MODE}" == "enumerated" ]]; then
  run_step legacy_generated_trace_verifier \
    "${PYTHON}" effectbench_omega/effectbench/kernel/verifier.py \
      --traces "${OUT_DIR}/traces.parquet" \
      --schemas effectbench_omega/schemas \
      --out "${LEGACY_KERNEL_DIR}"

  run_step canonical_enumerated_frontier \
    "${PYTHON}" effectbench_omega/effectbench/kernel/enumerate_frontier.py \
      --traces "${OUT_DIR}/traces.parquet" \
      --certificates "${LEGACY_CERTIFICATES}" \
      --out "${CANONICAL_KERNEL_DIR}" \
      --tables-out "effectbench_omega/tables/frontier_canonical_${TABLE_SUFFIX}.csv" \
      --report-out "effectbench_omega/reports/frontier_canonical_${TABLE_SUFFIX}.md" \
      --gate canonical
else
  run_step kernel_verifier \
    "${PYTHON}" effectbench_omega/effectbench/kernel/verifier.py \
      --traces "${OUT_DIR}/traces.parquet" \
      --schemas effectbench_omega/schemas \
      --out "${OUT_DIR}/kernel"
  CERTIFICATES="${OUT_DIR}/kernel/certificates.parquet"
fi

run_step no_oracle_report \
  "${PYTHON}" effectbench_omega/effectbench/audit/no_oracle_report.py \
    --runtime-logs "${OUT_DIR}/runtime_logs.parquet" \
    --out "effectbench_omega/tables/no_oracle_${TABLE_SUFFIX}.csv"

run_step projection_loss \
  "${PYTHON}" effectbench_omega/effectbench/baselines/project.py \
    --traces "${OUT_DIR}/traces.parquet" \
    --certificates "${CERTIFICATES}" \
    --baselines FINAL_STATE CORE_DFA MINISCOPE_PERMISSION CONTRACT_MENU_CMTF REVISABILITY MODERNSTACK_PROJECTION KERNEL_FULL \
    --out "effectbench_omega/tables/projection_loss_${TABLE_SUFFIX}.csv" \
    --reason-out "effectbench_omega/tables/projection_loss_${TABLE_SUFFIX}_reasons.csv"

run_step cegar \
  "${PYTHON}" effectbench_omega/effectbench/audit/cegar.py \
    --traces "${OUT_DIR}/traces.parquet" \
    --certificates "${CERTIFICATES}" \
    --schemas effectbench_omega/schemas \
    --omit-fields outbox policy_obligation contract_artifact_hash virtual_clock memory_cache user_visible_exposure compensation_or_payment_hold \
    --out "effectbench_omega/tables/cegar_rejections_${TABLE_SUFFIX}.csv" \
    --label-changes "effectbench_omega/tables/cegar_label_changes_${TABLE_SUFFIX}.csv"

run_step lattice_sensitivity \
  "${PYTHON}" effectbench_omega/effectbench/metrics/lattice_sensitivity.py \
    --certificates "${CERTIFICATES}" \
    --lattices effectbench_omega/configs/lattices \
    --out "effectbench_omega/tables/lattice_sensitivity_${TABLE_SUFFIX}.csv"

bootstrap_args=(
  "${PYTHON}" effectbench_omega/effectbench/metrics/bootstrap.py
    --certificates "${CERTIFICATES}"
    --group-by task_id model seed family
    --methods paired_bootstrap task_cluster hierarchical
    --out "effectbench_omega/tables/uncertainty_${TABLE_SUFFIX}.csv"
    --n-bootstrap 2000
    --seed 13
)
if [[ -n "${BOOTSTRAP_SYSTEMS}" ]]; then
  read -r -a bootstrap_systems <<<"${BOOTSTRAP_SYSTEMS}"
  bootstrap_args+=(--systems "${bootstrap_systems[@]}")
fi

run_step bootstrap \
  "${bootstrap_args[@]}"

read -r -a guard_tie_systems <<<"${GUARD_TIE_SYSTEMS}"

run_step guard_tie \
  "${PYTHON}" effectbench_omega/effectbench/audit/guard_tie.py \
    --traces "${OUT_DIR}/traces.parquet" \
    --certificates "${CERTIFICATES}" \
    --systems "${guard_tie_systems[@]}" \
    --out "effectbench_omega/tables/guard_tie_${TABLE_SUFFIX}.csv" \
    --details-out "effectbench_omega/tables/guard_tie_${TABLE_SUFFIX}_details.csv"

run_step replay_bundles \
  "${PYTHON}" effectbench_omega/effectbench/audit/replay_bundles.py \
    --certificates "${CERTIFICATES}" \
    --traces "${OUT_DIR}/traces.parquet" \
    --sample strict_excess=100 minimal=60 incomparable=60 necessary_high=30 \
    --out "effectbench_omega/witness_bundles/${TABLE_SUFFIX}"

run_step replay_certificates \
  "${PYTHON}" effectbench_omega/effectbench/audit/replay_certificates.py \
    --bundle-dir "effectbench_omega/witness_bundles/${TABLE_SUFFIX}" \
    --out "effectbench_omega/reports/certificate_replay_${TABLE_SUFFIX}.md" \
    --strict

run_step cost_audit \
  "${PYTHON}" effectbench_omega/effectbench/metrics/cost_audit.py \
    --logs "${OUT_DIR}/api_logs.jsonl" \
    --out "effectbench_omega/reports/${TABLE_SUFFIX}_cost.md" \
    --final

run_step aggregate \
  "${PYTHON}" effectbench_omega/effectbench/metrics/aggregate.py \
    --main-certificates "${CERTIFICATES}" \
    --projection-loss "effectbench_omega/tables/projection_loss_${TABLE_SUFFIX}.csv" \
    --cost-logs "${OUT_DIR}/api_logs.jsonl" \
    --out-tables "effectbench_omega/tables/${TABLE_SUFFIX}" \
    --out-figures "effectbench_omega/figures/${TABLE_SUFFIX}" \
    --claim-registry "effectbench_omega/metrics/claim_registry_${TABLE_SUFFIX}.csv"

run_step no_oracle_pytest \
  "${PYTHON}" -m pytest -q effectbench_omega/tests/no_oracle

event "stage3" "done" "offline suite complete for ${SPLIT}; certificates=${CERTIFICATES}"
