"""Independent review of the preserved v0.1 audit artifacts.

This script never imports or calls experiments.run, experiments.strategies, or
investigator.engine.  It reads the preserved trace and reconstructs only the
frozen case definitions needed to check compatibility and costs.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

from experiments.cases import HOLDOUT_SEEDS, generate_suite


STRATEGIES = (
    "ap_minimax",
    "forced_closure",
    "neutral_all",
    "neutral_discriminating",
    "information_gain",
)


def compatible(case, evidence: dict[str, str]) -> list[str]:
    return [
        explanation.explanation_id
        for explanation in case.explanations
        if all(
            observed in explanation.predictions.get(probe_id, frozenset())
            for probe_id, observed in evidence.items()
        )
    ]


def has_discriminating_probe(case, survivor_ids: list[str], remaining_ids: set[str]) -> bool:
    explanations = {item.explanation_id: item for item in case.explanations}
    for probe in case.probes:
        if probe.probe_id not in remaining_ids:
            continue
        groups = [
            sum(
                outcome in explanations[item_id].predictions[probe.probe_id]
                for item_id in survivor_ids
            )
            for outcome in probe.outcomes
        ]
        if any(0 < size < len(survivor_ids) for size in groups):
            return True
    return False


def aggregate(rows: list[dict]) -> dict:
    count = len(rows)
    return {
        "case_strategy_runs": count,
        "terminal_state_counts": dict(sorted(Counter(row["terminal_state"] for row in rows).items())),
        "warranted_resolution_count": sum(row["warranted_resolution"] for row in rows),
        "warranted_resolution_rate": sum(row["warranted_resolution"] for row in rows) / count,
        "warranted_correct_resolution_count": sum(row["warranted_correct_resolution"] for row in rows),
        "warranted_correct_resolution_rate": sum(row["warranted_correct_resolution"] for row in rows) / count,
        "premature_closure_count": sum(row["premature_closure"] for row in rows),
        "premature_closure_rate": sum(row["premature_closure"] for row in rows) / count,
        "unsupported_incompatible_selection_count": sum(row["unsupported_incompatible_selection"] for row in rows),
        "unresolved_count": sum(row["terminal_state"] == "UNRESOLVED" for row in rows),
        "unresolved_rate": sum(row["terminal_state"] == "UNRESOLVED" for row in rows) / count,
        "model_gap_count": sum(row["terminal_state"] == "MODEL_GAP" for row in rows),
        "model_gap_rate": sum(row["terminal_state"] == "MODEL_GAP" for row in rows) / count,
        "total_observations": sum(row["observations"] for row in rows),
        "mean_observations": sum(row["observations"] for row in rows) / count,
        "total_cost": sum(row["cost"] for row in rows),
        "mean_cost": sum(row["cost"] for row in rows) / count,
    }


def compare_values(path: str, left, right, differences: list[str]) -> None:
    if isinstance(left, float) or isinstance(right, float):
        if not math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-12):
            differences.append(f"{path}: recomputed={left!r}, preserved={right!r}")
    elif left != right:
        differences.append(f"{path}: recomputed={left!r}, preserved={right!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--preserved-metrics", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")

    cases = tuple(
        case for seed in HOLDOUT_SEEDS for case in generate_suite(seed, holdout=True)
    )
    case_by_id = {case.case_id: case for case in cases}
    records = [json.loads(line) for line in args.raw.read_text(encoding="utf-8").splitlines()]
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for record in records:
        grouped[(record["case_id"], record["strategy"])].append(record)

    errors: list[str] = []
    expected_groups = {(case.case_id, strategy) for case in cases for strategy in STRATEGIES}
    if set(grouped) != expected_groups:
        errors.append("case/strategy coverage differs from 800 cases x 5 strategies")
    result_rows = []
    check_counts = Counter()

    for case_id, strategy in sorted(expected_groups):
        case = case_by_id[case_id]
        rows = sorted(grouped[(case_id, strategy)], key=lambda row: row["step"])
        evidence = dict(case.initial_evidence)
        probe_by_id = {probe.probe_id: probe for probe in case.probes}
        remaining = set(probe_by_id)
        observations = 0
        cost = 0.0

        for index, row in enumerate(rows):
            label = f"{case_id}/{strategy}/{index}"
            if row["step"] != index:
                errors.append(f"{label}: non-contiguous step")
            expected_before = compatible(case, evidence)
            if row["candidate_ids_before"] != expected_before:
                errors.append(f"{label}: candidates before mismatch")
            if row["candidate_count_before"] != len(expected_before):
                errors.append(f"{label}: count before mismatch")
            if row["observed_evidence_before"] != [list(item) for item in sorted(evidence.items())]:
                errors.append(f"{label}: evidence snapshot mismatch")
            if row["experiment_version"] != "v0.1" or row["generator_version"] != "v0.1":
                errors.append(f"{label}: version metadata mismatch")
            for field, expected in (
                ("seed", case.seed),
                ("stratum", case.stratum),
                ("hidden_truth_id", case.hidden_truth_id),
                ("hidden_truth_family", case.hidden_truth_family),
            ):
                if row[field] != expected:
                    errors.append(f"{label}: {field} mismatch")

            selected = row["selected_probe_id"]
            if selected is not None:
                if selected not in remaining:
                    errors.append(f"{label}: unavailable or reused probe")
                probe = probe_by_id[selected]
                if row["selected_probe_cost"] != probe.cost:
                    errors.append(f"{label}: selected cost mismatch")
                if row["selected_probe_neutral_rank"] != probe.tie_rank:
                    errors.append(f"{label}: selected neutral rank mismatch")
                expected_outcome = dict(case.actual_outcomes).get(selected)
                if row["actual_outcome"] != expected_outcome:
                    errors.append(f"{label}: revealed outcome mismatch")
                evidence[selected] = row["actual_outcome"]
                remaining.remove(selected)
                observations += 1
                cost += probe.cost
            else:
                for field in ("selected_probe_cost", "selected_probe_neutral_rank", "selected_partition_sizes", "actual_outcome"):
                    if row[field] is not None:
                        errors.append(f"{label}: terminal {field} is non-null")

            expected_after = compatible(case, evidence)
            if row["candidate_ids_after"] != expected_after:
                errors.append(f"{label}: candidates after mismatch")
            if row["candidate_count_after"] != len(expected_after):
                errors.append(f"{label}: count after mismatch")
            if row["cumulative_observations"] != observations:
                errors.append(f"{label}: observation total mismatch")
            if not math.isclose(row["cumulative_cost"], cost):
                errors.append(f"{label}: cost total mismatch")

            expected_state = "MODEL_GAP" if not expected_after else "RESOLVED" if len(expected_after) == 1 else "UNRESOLVED"
            if strategy == "forced_closure" and len(expected_after) > 1:
                expected_state = "FORCED_CLOSED"
            if row["state_after"] != expected_state:
                errors.append(f"{label}: per-row state mismatch")

            if strategy == "forced_closure":
                ranks = case.explanation_rank_dict()
                expected_cause = None if not expected_after else expected_after[0] if len(expected_after) == 1 else min(expected_after, key=ranks.__getitem__)
            else:
                expected_cause = expected_after[0] if len(expected_after) == 1 else None
            if row["selected_cause"] != expected_cause:
                errors.append(f"{label}: selected cause mismatch")

            is_last = index == len(rows) - 1
            if selected is not None and row["terminal_action"] is not None:
                errors.append(f"{label}: reveal row terminal_action should be null in v0.1 schema")
            if not is_last and (selected is None or len(expected_after) <= 1):
                errors.append(f"{label}: trace continued after terminal condition")
            if is_last:
                if strategy == "forced_closure":
                    expected_action = "forced_close" if len(expected_after) > 1 else "terminal"
                    if row["terminal_action"] != expected_action:
                        errors.append(f"{label}: forced terminal action mismatch")
                elif selected is None:
                    expected_action = "model_gap" if not expected_after else "resolved" if len(expected_after) == 1 else "unresolved_no_discriminating_probe"
                    if row["terminal_action"] != expected_action:
                        errors.append(f"{label}: terminal action mismatch")
                    if len(expected_after) > 1 and has_discriminating_probe(case, expected_after, remaining):
                        errors.append(f"{label}: stopped unresolved with a discriminating probe available")
                elif len(expected_after) > 1:
                    errors.append(f"{label}: trace stopped after reveal while still unresolved")
            check_counts["rows_checked"] += 1

        final = rows[-1]
        final_ids = compatible(case, evidence)
        cause = final["selected_cause"]
        forced = final["state_after"] == "FORCED_CLOSED"
        state = "MODEL_GAP" if not final_ids else "RESOLVED" if len(final_ids) == 1 else "FORCED_CLOSED" if forced else "UNRESOLVED"
        warranted = len(final_ids) == 1 and cause == final_ids[0]
        result_rows.append({
            "case_id": case_id,
            "stratum": case.stratum,
            "strategy": strategy,
            "terminal_state": state,
            "observations": observations,
            "cost": cost,
            "warranted_resolution": warranted,
            "warranted_correct_resolution": warranted and cause == case.hidden_truth_id,
            "premature_closure": cause is not None and len(final_ids) != 1,
            "unsupported_incompatible_selection": cause is not None and cause not in final_ids,
        })

    recomputed = {}
    for strategy in STRATEGIES:
        strategy_rows = [row for row in result_rows if row["strategy"] == strategy]
        recomputed[strategy] = {
            "overall": aggregate(strategy_rows),
            "by_stratum": {
                stratum: aggregate([row for row in strategy_rows if row["stratum"] == stratum])
                for stratum in sorted({case.stratum for case in cases})
            },
        }

    preserved = json.loads(args.preserved_metrics.read_text(encoding="utf-8"))["by_strategy"]
    metric_differences: list[str] = []
    for strategy in STRATEGIES:
        for scope in ("overall",):
            for metric, value in recomputed[strategy][scope].items():
                compare_values(f"{strategy}/{scope}/{metric}", value, preserved[strategy][scope][metric], metric_differences)
        for stratum, values in recomputed[strategy]["by_stratum"].items():
            for metric, value in values.items():
                compare_values(f"{strategy}/{stratum}/{metric}", value, preserved[strategy]["by_stratum"][stratum][metric], metric_differences)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    hash_mismatches = []
    base = args.manifest.parent
    for filename, expected in manifest["sha256"].items():
        actual = hashlib.sha256((base / filename).read_bytes()).hexdigest()
        if actual != expected:
            hash_mismatches.append({"file": filename, "expected": expected, "actual": actual})

    output = {
        "scope": "audit of preserved v0.1 audit; raw trace read-only; no holdout execution",
        "raw_sha256": hashlib.sha256(args.raw.read_bytes()).hexdigest(),
        "case_count": len(cases),
        "case_strategy_group_count": len(grouped),
        "trace_record_count": len(records),
        "check_counts": dict(sorted(check_counts.items())),
        "trace_validation_errors": errors,
        "trace_validation_error_count": len(errors),
        "metric_differences_from_preserved_holdout_metrics": metric_differences,
        "metric_difference_count": len(metric_differences),
        "original_manifest_hash_mismatches": hash_mismatches,
        "original_manifest_hash_mismatch_count": len(hash_mismatches),
        "method_boundary": {
            "imports_frozen_runner": False,
            "imports_frozen_strategy_module": False,
            "imports_frozen_investigator_engine": False,
            "reconstructs_frozen_case_definitions": True,
            "uses_hidden_truth_for_action_selection": False,
            "uses_hidden_truth_only_for_correctness_and_preservation_checks": True
        },
        "recomputed_by_strategy": recomputed,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "trace_errors": len(errors),
        "metric_differences": len(metric_differences),
        "hash_mismatches": len(hash_mismatches),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
