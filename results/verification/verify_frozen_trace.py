from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

from experiments.cases import DEV_SEED, HOLDOUT_SEEDS, generate_suite
from experiments.strategies import ALL_STRATEGIES


def compatible(case, evidence: dict[str, str]) -> list[str]:
    return [
        explanation.explanation_id
        for explanation in case.explanations
        if all(
            outcome in explanation.predictions.get(probe_id, frozenset())
            for probe_id, outcome in evidence.items()
        )
    ]


def partition(case, survivor_ids: list[str], probe) -> dict[str, list[str]]:
    explanations = {item.explanation_id: item for item in case.explanations}
    return {
        outcome: [
            item_id
            for item_id in survivor_ids
            if outcome in explanations[item_id].predictions[probe.probe_id]
        ]
        for outcome in probe.outcomes
        if any(
            outcome in explanations[item_id].predictions[probe.probe_id]
            for item_id in survivor_ids
        )
    }


def independently_choose(strategy: str, case, survivor_ids: list[str], available):
    scored = []
    for probe in available:
        groups = partition(case, survivor_ids, probe)
        sizes = [len(ids) for ids in groups.values()]
        discriminating = any(size < len(survivor_ids) for size in sizes)
        worst = max(sizes)
        n = len(survivor_ids)
        gain = math.log2(n) - sum((size / n) * math.log2(size) for size in sizes)
        scored.append((probe, discriminating, worst, gain))
    if strategy == "ap_minimax":
        eligible = [item for item in scored if item[1]]
        return min(eligible, key=lambda item: (item[2], item[0].cost, item[0].tie_rank))[0] if eligible else None
    if strategy == "neutral_all":
        return min(available, key=lambda probe: probe.tie_rank) if available else None
    if strategy == "neutral_discriminating":
        eligible = [item for item in scored if item[1]]
        return min(eligible, key=lambda item: item[0].tie_rank)[0] if eligible else None
    if strategy == "information_gain":
        if not scored:
            return None
        best = max(item[3] for item in scored)
        if best <= 1e-12:
            return None
        eligible = [item for item in scored if math.isclose(item[3], best, rel_tol=0.0, abs_tol=1e-12)]
        return min(eligible, key=lambda item: (item[0].cost, item[0].tie_rank))[0]
    raise ValueError(strategy)


def load_records(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def summarize(records: list[dict], cases: tuple, raw_path: Path) -> tuple[dict, dict]:
    case_by_id = {case.case_id: case for case in cases}
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for record in records:
        grouped[(record["case_id"], record["strategy"])].append(record)

    errors: list[str] = []
    checks = Counter()
    hidden_truth_checks = Counter()
    result_rows = []
    expected_groups = {(case.case_id, strategy) for case in cases for strategy in ALL_STRATEGIES}
    if set(grouped) != expected_groups:
        errors.append("case/strategy group set differs from independently generated frozen suite")

    for key in sorted(expected_groups):
        case_id, strategy = key
        case = case_by_id[case_id]
        rows = sorted(grouped.get(key, []), key=lambda row: row["step"])
        if not rows:
            continue
        evidence = dict(case.initial_evidence)
        probes = {probe.probe_id: probe for probe in case.probes}
        remaining = list(case.probes)
        used: list[str] = []
        cumulative_cost = 0.0
        represented_truth = case.hidden_truth_id in {item.explanation_id for item in case.explanations}

        for expected_step, row in enumerate(rows):
            prefix = f"{case_id}/{strategy}/step={row['step']}"
            if row["step"] != expected_step:
                errors.append(f"{prefix}: non-contiguous step")
            expected_before = compatible(case, evidence)
            checks["compatibility_recomputations"] += 1
            if row["candidate_ids_before"] != expected_before:
                errors.append(f"{prefix}: candidate_ids_before mismatch")
            if row["candidate_count_before"] != len(row["candidate_ids_before"]):
                errors.append(f"{prefix}: candidate_count_before mismatch")
            expected_snapshot = [list(item) for item in sorted(evidence.items())]
            if row["observed_evidence_before"] != expected_snapshot:
                errors.append(f"{prefix}: observed_evidence_before mismatch")
            if row["observed_evidence_ids_before"] != sorted(evidence):
                errors.append(f"{prefix}: observed evidence IDs mismatch")
            if represented_truth:
                hidden_truth_checks["states_checked"] += 1
                if case.hidden_truth_id not in expected_before:
                    errors.append(f"{prefix}: represented hidden truth absent before reveal")

            selected_id = row["selected_probe_id"]
            if selected_id is None:
                expected_after = expected_before
                if row["candidate_ids_after"] != expected_after:
                    errors.append(f"{prefix}: terminal candidate set changed without evidence")
                checks["terminal_no_change_checks"] += 1
            else:
                checks["selected_probe_availability_checks"] += 1
                if selected_id not in {probe.probe_id for probe in remaining}:
                    errors.append(f"{prefix}: selected probe unavailable or reused")
                if selected_id in used:
                    errors.append(f"{prefix}: probe reused")
                probe = probes[selected_id]
                expected_choice = independently_choose(strategy, case, expected_before, remaining)
                checks["independent_probe_choice_checks"] += 1
                if expected_choice is None or expected_choice.probe_id != selected_id:
                    errors.append(f"{prefix}: selected probe differs from independent public-state choice")
                expected_outcome = dict(case.actual_outcomes).get(selected_id)
                if row["actual_outcome"] != expected_outcome:
                    errors.append(f"{prefix}: actual outcome mismatch")
                expected_sizes = sorted(len(ids) for ids in partition(case, expected_before, probe).values())
                if row["selected_partition_sizes"] != expected_sizes:
                    errors.append(f"{prefix}: selected partition sizes mismatch")
                evidence[selected_id] = row["actual_outcome"]
                cumulative_cost += probe.cost
                used.append(selected_id)
                remaining = [item for item in remaining if item.probe_id != selected_id]
                expected_after = compatible(case, evidence)
                checks["post_reveal_compatibility_recomputations"] += 1
                if row["candidate_ids_after"] != expected_after:
                    errors.append(f"{prefix}: candidate_ids_after mismatch")
                if represented_truth:
                    hidden_truth_checks["states_checked"] += 1
                    if case.hidden_truth_id not in expected_after:
                        errors.append(f"{prefix}: represented hidden truth absent after reveal")
            if row["candidate_count_after"] != len(row["candidate_ids_after"]):
                errors.append(f"{prefix}: candidate_count_after mismatch")
            if row["cumulative_observations"] != len(used):
                errors.append(f"{prefix}: cumulative observation count mismatch")
            if not math.isclose(row["cumulative_cost"], cumulative_cost):
                errors.append(f"{prefix}: cumulative cost mismatch")

        final = rows[-1]
        final_ids = compatible(case, evidence)
        selected_cause = final["selected_cause"]
        forced = final["state_after"] == "FORCED_CLOSED"
        warranted = len(final_ids) == 1 and selected_cause == final_ids[0]
        correct = selected_cause == case.hidden_truth_id
        unsupported_incompatible = selected_cause is not None and selected_cause not in final_ids
        premature = selected_cause is not None and len(final_ids) != 1
        independent_state = "MODEL_GAP" if not final_ids else "RESOLVED" if len(final_ids) == 1 else ("FORCED_CLOSED" if forced else "UNRESOLVED")
        if final["state_after"] != independent_state:
            errors.append(f"{case_id}/{strategy}: terminal state mismatch")
        result_rows.append({
            "case_id": case_id,
            "stratum": case.stratum,
            "strategy": strategy,
            "terminal_state": independent_state,
            "observations": len(used),
            "cost": cumulative_cost,
            "warranted_resolution": warranted,
            "warranted_correct_resolution": warranted and correct,
            "selected_cause_correct": correct if selected_cause is not None else None,
            "unsupported_incompatible_selection": unsupported_incompatible,
            "premature_closure": premature,
            "unresolved": independent_state == "UNRESOLVED",
            "model_gap": independent_state == "MODEL_GAP",
        })

    def aggregate(rows):
        count = len(rows)
        terminal = Counter(row["terminal_state"] for row in rows)
        return {
            "case_strategy_runs": count,
            "terminal_state_counts": dict(sorted(terminal.items())),
            "warranted_resolution_count": sum(row["warranted_resolution"] for row in rows),
            "warranted_resolution_rate": sum(row["warranted_resolution"] for row in rows) / count,
            "warranted_correct_resolution_count": sum(row["warranted_correct_resolution"] for row in rows),
            "warranted_correct_resolution_rate": sum(row["warranted_correct_resolution"] for row in rows) / count,
            "premature_closure_count": sum(row["premature_closure"] for row in rows),
            "premature_closure_rate": sum(row["premature_closure"] for row in rows) / count,
            "unsupported_incompatible_selection_count": sum(row["unsupported_incompatible_selection"] for row in rows),
            "unresolved_count": sum(row["unresolved"] for row in rows),
            "unresolved_rate": sum(row["unresolved"] for row in rows) / count,
            "model_gap_count": sum(row["model_gap"] for row in rows),
            "model_gap_rate": sum(row["model_gap"] for row in rows) / count,
            "total_observations": sum(row["observations"] for row in rows),
            "mean_observations": sum(row["observations"] for row in rows) / count,
            "total_cost": sum(row["cost"] for row in rows),
            "mean_cost": sum(row["cost"] for row in rows) / count,
        }

    by_strategy = {}
    for strategy in ALL_STRATEGIES:
        strategy_rows = [row for row in result_rows if row["strategy"] == strategy]
        by_strategy[strategy] = {
            "overall": aggregate(strategy_rows),
            "by_stratum": {
                stratum: aggregate([row for row in strategy_rows if row["stratum"] == stratum])
                for stratum in sorted({case.stratum for case in cases})
            },
        }

    ap = by_strategy["ap_minimax"]["overall"]
    comparisons = {}
    for strategy in ALL_STRATEGIES:
        if strategy == "ap_minimax":
            continue
        other = by_strategy[strategy]["overall"]
        comparisons[strategy] = {
            "warranted_resolution_rate_difference_ap_minus_baseline": ap["warranted_resolution_rate"] - other["warranted_resolution_rate"],
            "premature_closure_rate_difference_ap_minus_baseline": ap["premature_closure_rate"] - other["premature_closure_rate"],
            "mean_observations_difference_ap_minus_baseline": ap["mean_observations"] - other["mean_observations"],
            "mean_cost_difference_ap_minus_baseline": ap["mean_cost"] - other["mean_cost"],
        }

    metrics = {
        "raw_trace": str(raw_path),
        "raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "trace_records": len(records),
        "unique_cases": len(cases),
        "case_counts_by_stratum": dict(sorted(Counter(case.stratum for case in cases).items())),
        "strategies": list(ALL_STRATEGIES),
        "definitions": {
            "warranted_resolution": "final independently compatible set has exactly one ID and selected_cause is that ID",
            "warranted_correct_resolution": "warranted_resolution and selected_cause equals hidden_truth_id",
            "premature_closure": "a cause is selected while the final independently compatible set does not have exactly one ID",
            "unsupported_incompatible_selection": "selected_cause is not in the final independently compatible set",
            "unresolved": "more than one independently compatible explanation remains and no forced closure is applied",
            "model_gap": "zero independently compatible explanations remain",
            "observations": "count of non-null selected_probe_id records",
            "cost": "sum of frozen costs for selected probes",
        },
        "by_strategy": by_strategy,
        "ap_minimax_comparisons": comparisons,
    }
    invariants = {
        "errors": errors,
        "error_count": len(errors),
        "checks_performed": dict(sorted(checks.items())),
        "represented_hidden_truth_compatibility": {
            "states_checked": hidden_truth_checks["states_checked"],
            "failures": sum("represented hidden truth absent" in error for error in errors),
        },
        "all_trace_invariants_pass": not errors,
    }
    return metrics, invariants


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("dev", "holdout"), required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--invariants", type=Path, required=True)
    args = parser.parse_args()
    cases = generate_suite(DEV_SEED, holdout=False) if args.mode == "dev" else tuple(
        case for seed in HOLDOUT_SEEDS for case in generate_suite(seed, holdout=True)
    )
    for output in (args.metrics, args.invariants):
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")
    metrics, invariants = summarize(load_records(args.raw), cases, args.raw)
    args.metrics.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.invariants.write_text(json.dumps(invariants, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": str(args.metrics), "invariants": str(args.invariants), "errors": invariants["error_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
