#!/usr/bin/env python3
"""Paired and clustered bootstrap uncertainty estimates."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd


DEFAULT_SYSTEMS = ["BASE", "PROJ_GUARD", "EFFECTGUARD"]
V2_SYSTEMS = ["BASE", "PROJ_GUARD_V2", "EFFECTGUARD_V2"]


def _base_task_id(task_id: str) -> str:
    return str(task_id).split(":", 1)[0]


def _resolve_systems(certs: pd.DataFrame, requested: list[str] | None) -> list[str]:
    if requested:
        if len(requested) != 3:
            raise ValueError("--systems must contain exactly three systems: BASE PROJ EFFECT")
        return requested
    observed = set(certs["system"].astype(str).unique())
    if set(V2_SYSTEMS).issubset(observed):
        return V2_SYSTEMS
    return DEFAULT_SYSTEMS


def _unit_table(certs: pd.DataFrame, systems: list[str]) -> pd.DataFrame:
    df = certs.copy()
    df["strict"] = df["verdict"].eq("strict_excess").astype(float)
    df["raw_success"] = df["terminal_success"].astype(float)
    df["kernel_success"] = (df["terminal_success"] & ~df["verdict"].eq("strict_excess")).astype(float)
    df["base_task_id"] = df["task_id"].map(_base_task_id)
    index = ["family", "base_task_id", "task_id", "regime", "seed", "model"]
    pivot = df.pivot_table(
        index=index,
        columns="system",
        values=["strict", "raw_success", "kernel_success"],
        aggfunc="first",
    )
    pivot.columns = [f"{metric}_{system}" for metric, system in pivot.columns]
    pivot = pivot.reset_index()
    required = [f"strict_{system}" for system in systems]
    missing = [col for col in required if col not in pivot]
    if missing:
        raise ValueError(f"missing required system columns: {missing}")
    return pivot.dropna(subset=required)


def _comparisons(systems: list[str]) -> dict[str, tuple[str, Callable[[pd.DataFrame], np.ndarray]]]:
    base, proj, effect = systems
    return {
        f"{base}_raw_minus_kernel_success": (
            "raw_success_gap",
            lambda df: (df[f"raw_success_{base}"] - df[f"kernel_success_{base}"]).to_numpy(float),
        ),
        f"{base}_strict_minus_{proj}_strict": (
            "strict_excess_reduction",
            lambda df: (df[f"strict_{base}"] - df[f"strict_{proj}"]).to_numpy(float),
        ),
        f"{proj}_strict_minus_{effect}_strict": (
            "strict_excess_reduction",
            lambda df: (df[f"strict_{proj}"] - df[f"strict_{effect}"]).to_numpy(float),
        ),
        f"{effect}_kernel_minus_{base}_kernel": (
            "kernel_success_gain",
            lambda df: (df[f"kernel_success_{effect}"] - df[f"kernel_success_{base}"]).to_numpy(float),
        ),
        f"{effect}_raw_minus_{base}_raw": (
            "raw_success_retention_delta",
            lambda df: (df[f"raw_success_{effect}"] - df[f"raw_success_{base}"]).to_numpy(float),
        ),
    }


def _ci(values: np.ndarray) -> tuple[float, float, float]:
    if len(values) == 0:
        return 0.0, 0.0, 0.0
    return (
        float(np.percentile(values, 2.5)),
        float(np.percentile(values, 97.5)),
        float(values.std(ddof=1)) if len(values) > 1 else 0.0,
    )


def _paired_bootstrap(values: np.ndarray, rng: np.random.Generator, n_bootstrap: int) -> np.ndarray:
    n = len(values)
    if n == 0:
        return np.array([0.0])
    samples = rng.integers(0, n, size=(n_bootstrap, n))
    return values[samples].mean(axis=1)


def _cluster_sums(values: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    unique = pd.unique(labels)
    sums = np.zeros(len(unique), dtype=float)
    counts = np.zeros(len(unique), dtype=float)
    positions = {label: index for index, label in enumerate(unique)}
    for value, label in zip(values, labels):
        index = positions[label]
        sums[index] += float(value)
        counts[index] += 1.0
    return unique, sums, counts


def _cluster_bootstrap_values(
    values: np.ndarray,
    labels: np.ndarray,
    rng: np.random.Generator,
    n_bootstrap: int,
) -> np.ndarray:
    clusters, sums, counts = _cluster_sums(values, labels)
    n = len(clusters)
    if n == 0:
        return np.array([0.0])
    samples = rng.integers(0, n, size=(n_bootstrap, n))
    sampled_sums = sums[samples].sum(axis=1)
    sampled_counts = counts[samples].sum(axis=1)
    return sampled_sums / np.maximum(sampled_counts, 1.0)


def _hierarchical_bootstrap(
    units: pd.DataFrame,
    values: np.ndarray,
    rng: np.random.Generator,
    n_bootstrap: int,
) -> np.ndarray:
    work = units[["family", "base_task_id"]].copy()
    work["value"] = values
    families = work["family"].drop_duplicates().to_numpy()
    grouped: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for family, family_df in work.groupby("family", sort=False):
        _, sums, counts = _cluster_sums(family_df["value"].to_numpy(float), family_df["base_task_id"].to_numpy())
        grouped[str(family)] = (sums, counts)
    estimates = []
    for _ in range(n_bootstrap):
        total_sum = 0.0
        total_count = 0.0
        sampled_families = rng.choice(families, size=len(families), replace=True)
        for family in sampled_families:
            sums, counts = grouped[str(family)]
            if len(sums) == 0:
                continue
            sampled_tasks = rng.integers(0, len(sums), size=len(sums))
            total_sum += float(sums[sampled_tasks].sum())
            total_count += float(counts[sampled_tasks].sum())
        estimates.append(total_sum / max(total_count, 1.0))
    return np.array(estimates)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificates", required=True)
    parser.add_argument("--group-by", nargs="*")
    parser.add_argument("--methods", nargs="*")
    parser.add_argument("--out", required=True)
    parser.add_argument("--n-bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--systems", nargs="+")
    args = parser.parse_args()

    certs = pd.read_parquet(args.certificates)
    systems = _resolve_systems(certs, args.systems)
    units = _unit_table(certs, systems)
    methods = args.methods or ["paired_bootstrap", "task_cluster", "hierarchical"]
    rng = np.random.default_rng(args.seed)
    rows = []
    for comparison, (metric, value_fn) in _comparisons(systems).items():
        values = value_fn(units)
        estimate = float(values.mean()) if len(values) else 0.0
        for method in methods:
            method_rng = np.random.default_rng(int(rng.integers(0, 2**31 - 1)))
            if method == "paired_bootstrap":
                boot = _paired_bootstrap(values, method_rng, args.n_bootstrap)
                cluster_col = "unit"
                n_clusters = len(units)
            elif method == "task_cluster":
                boot = _cluster_bootstrap_values(values, units["base_task_id"].to_numpy(), method_rng, args.n_bootstrap)
                cluster_col = "base_task_id"
                n_clusters = int(units["base_task_id"].nunique())
            elif method == "hierarchical":
                boot = _hierarchical_bootstrap(units, values, method_rng, args.n_bootstrap)
                cluster_col = "family/base_task_id"
                n_clusters = int(units["base_task_id"].nunique())
            else:
                raise ValueError(f"unknown bootstrap method: {method}")
            ci_low, ci_high, se = _ci(boot)
            rows.append(
                {
                    "comparison": comparison,
                    "metric": metric,
                    "method": method,
                    "estimate": estimate,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "standard_error": se,
                    "p_value_le_zero": float((boot <= 0).mean()),
                    "n_units": int(len(units)),
                    "n_clusters": n_clusters,
                    "cluster_col": cluster_col,
                    "n_bootstrap": int(args.n_bootstrap),
                    "seed": int(args.seed),
                }
            )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
