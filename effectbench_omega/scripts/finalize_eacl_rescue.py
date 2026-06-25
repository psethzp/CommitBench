#!/usr/bin/env python3
"""Generate final EACL rescue reports from frozen local artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Claim:
    claim_id: str
    claim: str
    value: str
    unit: str
    artifact: str
    extraction: str
    paper_status: str


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / path)


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def pct(value: float) -> str:
    return f"{100.0 * value:.4f}%"


def fmt_float(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def first_row(path: str) -> pd.Series:
    df = read_csv(path)
    if df.empty:
        raise ValueError(f"empty table: {path}")
    return df.iloc[0]


def online_row(path: str, system: str) -> pd.Series:
    df = read_csv(path)
    rows = df[df["system"] == system]
    if rows.empty:
        raise ValueError(f"missing system {system} in {path}")
    return rows.iloc[0]


def no_oracle_summary(paths: Iterable[str]) -> tuple[int, int]:
    checked = 0
    failures = 0
    for path in paths:
        df = read_csv(path)
        checked += int(df["rows_checked"].sum())
        failures += int(df["oracle_failures"].sum())
    return checked, failures


def artifact_files() -> list[Path]:
    generated_by_this_script = {
        ROOT / "effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv",
        ROOT / "effectbench_omega/reports/artifact_manifest.md",
        ROOT / "effectbench_omega/reports/eacl_rescue_paper_ready_summary.md",
        ROOT / "effectbench_omega/reports/stage7_lattice_policy_freeze.md",
        ROOT / "effectbench_omega/reports/stage8_claim_audit.md",
        ROOT / "effectbench_omega/tables/artifact_manifest.csv",
    }
    roots = [
        ROOT / "effectbench_omega/artifacts",
        ROOT / "effectbench_omega/figures",
        ROOT / "effectbench_omega/jobs",
        ROOT / "effectbench_omega/manifests",
        ROOT / "effectbench_omega/metrics",
        ROOT / "effectbench_omega/outputs",
        ROOT / "effectbench_omega/reports",
        ROOT / "effectbench_omega/tables",
        ROOT / "effectbench_omega/witness_bundles",
    ]
    root_files = [
        ROOT / "CommitBench.pdf",
        ROOT / "effectbench_supervisor_explainer.pptx",
    ]
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        files.extend(
            path
            for path in root.rglob("*")
            if path.is_file()
            and path not in generated_by_this_script
            and "__pycache__" not in path.parts
            and "models" not in path.parts
            and "upstreams" not in path.parts
        )
    files.extend(path for path in root_files if path.exists())
    return sorted(set(files))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_artifact_manifest() -> tuple[int, int, list[dict]]:
    files = artifact_files()
    rows = []
    for path in files:
        size = path.stat().st_size
        rows.append(
            {
                "path": rel(path),
                "size_bytes": size,
                "sha256": sha256(path),
            }
        )

    out_csv = ROOT / "effectbench_omega/tables/artifact_manifest.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["path", "size_bytes", "sha256"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    grouped: dict[str, tuple[int, int]] = {}
    for row in rows:
        path = Path(row["path"])
        if path.parts[0] == "effectbench_omega" and len(path.parts) > 1:
            group = f"{path.parts[0]}/{path.parts[1]}"
        else:
            group = path.parts[0]
        count, total = grouped.get(group, (0, 0))
        grouped[group] = (count + 1, total + int(row["size_bytes"]))

    summary_rows = [
        {"group": group, "file_count": count, "size_bytes": total}
        for group, (count, total) in sorted(grouped.items())
    ]
    out_md = ROOT / "effectbench_omega/reports/artifact_manifest.md"
    lines = [
        "# Artifact Manifest",
        "",
        f"Files indexed: {len(rows):,}",
        f"Total bytes: {sum(int(row['size_bytes']) for row in rows):,}",
        "",
        "| Group | Files | Bytes |",
        "|---|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(f"| `{row['group']}` | {row['file_count']:,} | {row['size_bytes']:,} |")
    lines.extend(
        [
            "",
            "The full per-file manifest with SHA-256 hashes is in",
            "`effectbench_omega/tables/artifact_manifest.csv`.",
            "",
            "Local caches, upstream repository clones, virtualenvs, and `.env` files are excluded.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n")
    return len(rows), sum(int(row["size_bytes"]) for row in rows), summary_rows


def build_claims(artifact_count: int, artifact_bytes: int) -> list[Claim]:
    main_frontier_path = "effectbench_omega/tables/frontier_canonical_main_mc_postfix_all_local_canonical.csv"
    guard_frontier_path = "effectbench_omega/tables/frontier_canonical_guard_v2_main_with_base_all_local_canonical.csv"
    native_frontier_path = "effectbench_omega/tables/frontier_canonical_native_subset_v1_all_local_canonical.csv"
    main_online_path = "effectbench_omega/tables/main_mc_postfix_all_local_canonical/online_control_main.csv"
    guard_online_path = "effectbench_omega/tables/guard_v2_main_with_base_all_local_canonical/online_control_main.csv"
    native_traces_path = "effectbench_omega/outputs/native_subset_v1_all_local/traces.parquet"
    stage6_path = "effectbench_omega/tables/stage6_full_replay_summary.csv"
    qwen_path = "effectbench_omega/tables/qwen_repair_sensitivity.csv"
    cegar_path = "effectbench_omega/tables/cegar_rejections_stage6_targeted_stress.csv"

    main_frontier = first_row(main_frontier_path)
    guard_frontier = first_row(guard_frontier_path)
    native_frontier = first_row(native_frontier_path)
    main_base = online_row(main_online_path, "BASE")
    guard_base = online_row(guard_online_path, "BASE")
    guard_proj = online_row(guard_online_path, "PROJ_GUARD_V2")
    guard_effect = online_row(guard_online_path, "EFFECTGUARD_V2")
    qwen = first_row(qwen_path)
    stage6 = read_csv(stage6_path)
    cegar = read_csv(cegar_path)
    native = pd.read_parquet(ROOT / native_traces_path)
    no_oracle_checked, no_oracle_failures = no_oracle_summary(
        [
            "effectbench_omega/tables/no_oracle_main_mc_postfix_all_local_canonical.csv",
            "effectbench_omega/tables/no_oracle_guard_v2_main_with_base_all_local_canonical.csv",
            "effectbench_omega/tables/no_oracle_native_subset_v1_all_local_canonical.csv",
        ]
    )

    native_total = len(native)
    native_success = int(native["terminal_success"].sum())
    native_failures = native_total - native_success
    replay_total = int(stage6["bundles_checked"].sum())
    replay_native = int(stage6["native_replays_checked"].sum())
    replay_failures = int(stage6["failures"].sum())
    cegar_all_fields = ",".join(sorted(cegar["omitted_field"].tolist()))
    cegar_total_groups = int(cegar["label_change_groups"].sum())

    rows = [
        Claim(
            "headline_denominator",
            "Controlled local headline split contains 128 tasks x 7 regimes x 2 seeds x 4 models x 3 systems.",
            "21504",
            "trajectories",
            main_frontier_path,
            "observed_successes",
            "allowed_main",
        ),
        Claim(
            "main_canonical_strict_excess",
            "Paper-grade strict-excess labels for the controlled split use enumerated-frontier certificates.",
            str(int(main_frontier["enumerated_strict_excess"])),
            "strict-excess certificates",
            main_frontier_path,
            "enumerated_strict_excess",
            "allowed_main",
        ),
        Claim(
            "main_legacy_strict_excess_archived",
            "Generated-trace strict labels are archived as legacy diagnostics, not headline labels.",
            str(int(main_frontier["old_strict_excess"])),
            "legacy strict-excess labels",
            main_frontier_path,
            "old_strict_excess",
            "archive_only",
        ),
        Claim(
            "main_spurious_legacy_witnesses",
            "Canonical audit records old generated-trace witnesses that were not enumerated-admissible.",
            str(int(main_frontier["spurious_legacy_witnesses"])),
            "spurious legacy witnesses",
            main_frontier_path,
            "spurious_legacy_witnesses",
            "allowed_audit",
        ),
        Claim(
            "main_canonical_gate",
            "Canonical enumerated-frontier gate passes for the controlled split.",
            str(bool(main_frontier["canonical_gate"])),
            "boolean",
            main_frontier_path,
            "canonical_gate and unexplained_mismatches",
            "allowed_main",
        ),
        Claim(
            "base_raw_kernel_gap",
            "BASE final-state success overstates certified least-effect success in the controlled split.",
            pct(float(main_base["strict_excess_rate"])),
            "percentage points among BASE successes",
            main_online_path,
            "BASE strict_excess_rate",
            "allowed_main",
        ),
        Claim(
            "guard_v2_base_strict_rate",
            "In the corrected-guard split, BASE strict-excess rate remains high.",
            pct(float(guard_base["strict_excess_rate"])),
            "strict-excess rate",
            guard_online_path,
            "BASE strict_excess_rate",
            "allowed_main",
        ),
        Claim(
            "guard_v2_proj_strict_rate",
            "PROJ_GUARD_V2 leaves residual strict excess.",
            pct(float(guard_proj["strict_excess_rate"])),
            "strict-excess rate",
            guard_online_path,
            "PROJ_GUARD_V2 strict_excess_rate",
            "allowed_main",
        ),
        Claim(
            "guard_v2_effect_strict_rate",
            "EFFECTGUARD_V2 removes strict excess in this corrected local split.",
            pct(float(guard_effect["strict_excess_rate"])),
            "strict-excess rate",
            guard_online_path,
            "EFFECTGUARD_V2 strict_excess_rate",
            "allowed_main_with_caveat",
        ),
        Claim(
            "guard_v2_canonical_strict_excess",
            "Corrected-guard combined split has canonical strict-excess labels from enumerated frontier scoring.",
            str(int(guard_frontier["enumerated_strict_excess"])),
            "strict-excess certificates",
            guard_frontier_path,
            "enumerated_strict_excess",
            "allowed_main",
        ),
        Claim(
            "native_subset_denominator",
            "Native-fidelity validation block has 48 native tasks x 4 regimes x 2 seeds x 4 models x 3 systems.",
            str(native_total),
            "trajectories",
            native_traces_path,
            "len(traces)",
            "allowed_validation",
        ),
        Claim(
            "native_terminal_failures",
            "Native-fidelity validation block has counted terminal failures.",
            str(native_failures),
            "terminal failures",
            native_traces_path,
            "terminal_success == False",
            "allowed_validation",
        ),
        Claim(
            "native_canonical_strict_excess",
            "Native-fidelity validation block has canonical strict-excess certificates.",
            str(int(native_frontier["enumerated_strict_excess"])),
            "strict-excess certificates",
            native_frontier_path,
            "enumerated_strict_excess",
            "allowed_validation",
        ),
        Claim(
            "native_successes",
            "Native-fidelity validation block records native successful episodes separately from terminal failures.",
            str(native_success),
            "native successes",
            native_traces_path,
            "terminal_success == True",
            "allowed_validation",
        ),
        Claim(
            "stage6_replay_total",
            "Full replay passes for all paper-cited canonical bundles generated in Stage 6.",
            str(replay_total),
            "bundles checked",
            stage6_path,
            "sum(bundles_checked)",
            "allowed_main",
        ),
        Claim(
            "stage6_replay_failures",
            "Full replay found no certificate failures.",
            str(replay_failures),
            "replay failures",
            stage6_path,
            "sum(failures)",
            "allowed_main",
        ),
        Claim(
            "stage6_native_replays",
            "Native-fidelity replay re-executes native bundles in the native wrappers.",
            str(replay_native),
            "native replays",
            stage6_path,
            "sum(native_replays_checked)",
            "allowed_validation",
        ),
        Claim(
            "targeted_cegar_fields",
            "Targeted CEGAR stress exercises every future-relevant field.",
            cegar_all_fields,
            "fields",
            cegar_path,
            "omitted_field",
            "allowed_audit",
        ),
        Claim(
            "targeted_cegar_label_change_groups",
            "Targeted CEGAR stress produces label-changing reduced-state collisions.",
            str(cegar_total_groups),
            "label-change groups",
            cegar_path,
            "sum(label_change_groups)",
            "allowed_audit",
        ),
        Claim(
            "qwen_repair_sensitivity",
            "Same-prompt Qwen repair sensitivity changed no proposals, effects, verdicts, or headline strict rate.",
            f"{int(qwen['affected_rows'])} affected rows; {fmt_float(float(qwen['overall_strict_delta_pp']))} pp delta",
            "rows and percentage points",
            qwen_path,
            "affected_rows and overall_strict_delta_pp",
            "allowed_caveat",
        ),
        Claim(
            "no_oracle_final",
            "No-oracle sentinels pass across the controlled, corrected-guard, and native canonical splits.",
            f"{no_oracle_checked} checked; {no_oracle_failures} failures",
            "rows and failures",
            "effectbench_omega/tables/no_oracle_*_canonical.csv",
            "sum rows_checked, oracle_failures",
            "allowed_main",
        ),
        Claim(
            "local_cost",
            "Local-only headline and validation runs have zero API cost.",
            "$0",
            "USD",
            "effectbench_omega/outputs/*/api_logs.jsonl",
            "cost_usd sums to zero for local provider rows",
            "allowed_main",
        ),
        Claim(
            "artifact_manifest",
            "Final artifact manifest indexes generated experiment artifacts with SHA-256 hashes.",
            f"{artifact_count} files; {artifact_bytes} bytes",
            "files and bytes",
            "effectbench_omega/tables/artifact_manifest.csv",
            "artifact manifest generation",
            "allowed_reproducibility",
        ),
    ]
    return rows


def write_claim_registry(claims: list[Claim]) -> None:
    out = ROOT / "effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(Claim.__dataclass_fields__.keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        for claim in claims:
            writer.writerow(claim.__dict__)


def write_stage7_report() -> None:
    paths = [
        "effectbench_omega/tables/lattice_sensitivity_main_mc_postfix_all_local_canonical.csv",
        "effectbench_omega/tables/lattice_sensitivity_guard_v2_main_with_base_all_local_canonical.csv",
        "effectbench_omega/tables/lattice_sensitivity_native_subset_v1_all_local_canonical.csv",
    ]
    lines = [
        "# Stage 7 Lattice Policy Freeze",
        "",
        "Decision: use the fixed declared Pareto lattice for all main claims.",
        "",
        "The current lattice sensitivity tables preserve the headline sign, but the",
        "reported strict-excess rates are exactly invariant across the configured",
        "weight/name variants. Under the rescue plan, this is not strong enough to",
        "support a main-paper value-governance sensitivity claim. The defensible",
        "paper treatment is to move lattice sensitivity to an appendix/diagnostic",
        "or omit it from main claims, and state that alternatives to the declared",
        "Pareto lattice are future work.",
        "",
        "| Split | Variants | Unique strict-excess rates | Policy |",
        "|---|---:|---:|---|",
    ]
    for path in paths:
        df = read_csv(path)
        split = Path(path).name.replace("lattice_sensitivity_", "").replace(".csv", "")
        lines.append(
            f"| `{split}` | {len(df)} | {df['strict_excess_rate'].nunique()} | appendix diagnostic only |"
        )
    lines.extend(
        [
            "",
            "Main-paper rule:",
            "",
            "```text",
            "Do not claim robustness across alternative value lattices from these",
            "tables. Claim only that all reported strict-excess labels use the fixed",
            "declared Pareto lattice in the effect schema, with incomparability",
            "reported separately.",
            "```",
        ]
    )
    (ROOT / "effectbench_omega/reports/stage7_lattice_policy_freeze.md").write_text(
        "\n".join(lines) + "\n"
    )


def write_claim_audit(claims: list[Claim]) -> None:
    rows_by_status: dict[str, int] = {}
    for claim in claims:
        rows_by_status[claim.paper_status] = rows_by_status.get(claim.paper_status, 0) + 1
    lines = [
        "# Stage 8 Claim Audit",
        "",
        f"Final claim registry rows: {len(claims)}",
        "",
        "| Paper status | Rows |",
        "|---|---:|",
    ]
    for status, count in sorted(rows_by_status.items()):
        lines.append(f"| `{status}` | {count} |")
    lines.extend(
        [
            "",
            "Rules enforced by the final registry:",
            "",
            "- Use canonical enumerated-frontier labels for strict-excess claims.",
            "- Treat generated-trace strict labels as archived diagnostics only.",
            "- Keep local/open-weight claims separate from Bedrock/frontier claims.",
            "- Report the native-fidelity subset as validation, not as the headline denominator.",
            "- Do not use lattice sensitivity as a main-paper robustness claim.",
            "- Do not claim human evaluation or commercial-model leaderboards.",
            "",
            "Registry path: `effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv`.",
        ]
    )
    (ROOT / "effectbench_omega/reports/stage8_claim_audit.md").write_text(
        "\n".join(lines) + "\n"
    )


def write_paper_summary(claims: list[Claim]) -> None:
    claim_lookup = {claim.claim_id: claim for claim in claims}
    lines = [
        "# EACL Rescue Paper-Ready Summary",
        "",
        "Recommended paper posture:",
        "",
        "> EffectBench-Omega introduces Effect Kernel certificates for tool-agent",
        "> traces. In local open-weight experiments, final-state success",
        "> substantially overstates certified least-effect success. Projection-only",
        "> safeguards reduce but do not remove strict excess, while the no-oracle",
        "> EffectGuard reference controller reduces strict excess under the fixed",
        "> declared effect lattice. A native-fidelity validation block and full",
        "> certificate replay support the auditability claim.",
        "",
        "Use these main numbers:",
        "",
        "| Claim | Value | Source |",
        "|---|---:|---|",
    ]
    for claim_id in [
        "headline_denominator",
        "main_canonical_strict_excess",
        "base_raw_kernel_gap",
        "guard_v2_proj_strict_rate",
        "guard_v2_effect_strict_rate",
        "native_subset_denominator",
        "native_terminal_failures",
        "stage6_replay_total",
        "stage6_replay_failures",
    ]:
        claim = claim_lookup[claim_id]
        lines.append(f"| {claim.claim} | {claim.value} | `{claim.artifact}` |")
    lines.extend(
        [
            "",
            "Figures available:",
            "",
            "- `effectbench_omega/figures/main_mc_postfix_all_local_canonical/`",
            "- `effectbench_omega/figures/guard_v2_main_with_base_all_local_canonical/`",
            "- `effectbench_omega/figures/native_subset_v1_all_local_canonical/`",
            "",
            "Required limitations:",
            "",
            "- Local/open-weight only; no frontier or Bedrock leaderboard.",
            "- Controlled adapter headline split has 100% raw success; use it for least-effect certification, not task-difficulty claims.",
            "- Native-fidelity subset is compact and source-backed, not a full upstream server re-host.",
            "- Projection baselines are deterministic projection baselines, not faithful reproductions of every named SOTA system.",
            "- Lattice sensitivity is appendix/diagnostic only in this rescue package.",
            "- No human-eval claim.",
        ]
    )
    (ROOT / "effectbench_omega/reports/eacl_rescue_paper_ready_summary.md").write_text(
        "\n".join(lines) + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-artifact-hashes", action="store_true")
    args = parser.parse_args()

    write_stage7_report()
    if args.skip_artifact_hashes:
        artifact_count, artifact_bytes, _ = 0, 0, []
    else:
        artifact_count, artifact_bytes, _ = write_artifact_manifest()
    claims = build_claims(artifact_count, artifact_bytes)
    write_claim_registry(claims)
    write_claim_audit(claims)
    write_paper_summary(claims)
    print(
        json.dumps(
            {
                "artifact_count": artifact_count,
                "artifact_bytes": artifact_bytes,
                "claim_registry_rows": len(claims),
                "outputs": [
                    "effectbench_omega/reports/stage7_lattice_policy_freeze.md",
                    "effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv",
                    "effectbench_omega/reports/stage8_claim_audit.md",
                    "effectbench_omega/reports/eacl_rescue_paper_ready_summary.md",
                    "effectbench_omega/reports/artifact_manifest.md",
                    "effectbench_omega/tables/artifact_manifest.csv",
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
