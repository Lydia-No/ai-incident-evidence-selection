"""Structural AP-versus-information-gain analysis from preserved v0.1 evidence.

No experiment runner or frozen strategy function is imported or executed.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path

from experiments.cases import HOLDOUT_SEEDS, generate_suite


def compatible(case, evidence):
    return [
        item for item in case.explanations
        if all(outcome in item.predictions.get(probe_id, ()) for probe_id, outcome in evidence.items())
    ]


def probe_score(survivors, probe):
    groups = []
    for outcome in probe.outcomes:
        ids = [item.explanation_id for item in survivors if outcome in item.predictions[probe.probe_id]]
        if ids:
            groups.append(ids)
    sizes = tuple(sorted(len(ids) for ids in groups))
    n = len(survivors)
    gain = math.log2(n) - sum((len(ids) / n) * math.log2(len(ids)) for ids in groups)
    return {
        "sizes": sizes,
        "worst": max(sizes),
        "gain": gain,
        "discriminating": any(len(ids) < n for ids in groups),
    }


def objective_choices(case, evidence, available):
    survivors = compatible(case, evidence)
    scored = [(probe, probe_score(survivors, probe)) for probe in available]
    discriminating = [item for item in scored if item[1]["discriminating"]]
    ap = min(
        discriminating,
        key=lambda item: (item[1]["worst"], item[0].cost, item[0].tie_rank),
    )[0] if discriminating else None
    best_gain = max((item[1]["gain"] for item in scored), default=0.0)
    best_ig = [
        item for item in scored
        if best_gain > 1e-12 and math.isclose(item[1]["gain"], best_gain, rel_tol=0.0, abs_tol=1e-12)
    ]
    ig = min(best_ig, key=lambda item: (item[0].cost, item[0].tie_rank))[0] if best_ig else None
    return ap, ig, scored


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")

    cases = tuple(case for seed in HOLDOUT_SEEDS for case in generate_suite(seed, holdout=True))
    groups = defaultdict(list)
    for line in args.raw.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        groups[(row["case_id"], row["strategy"])].append(row)
    for rows in groups.values():
        rows.sort(key=lambda row: row["step"])

    def selected(case_id, strategy):
        return [row for row in groups[(case_id, strategy)] if row["selected_probe_id"] is not None]

    def final(case_id, strategy):
        return groups[(case_id, strategy)][-1]

    comparison_by_stratum = {}
    all_case_comparisons = []
    for stratum in sorted({case.stratum for case in cases}):
        subset = [case for case in cases if case.stratum == stratum]
        rows = []
        for case in subset:
            ap_rows = selected(case.case_id, "ap_minimax")
            ig_rows = selected(case.case_id, "information_gain")
            ap_final = final(case.case_id, "ap_minimax")
            ig_final = final(case.case_id, "information_gain")
            item = {
                "stratum": stratum,
                "first_action_same": [row["selected_probe_id"] for row in ap_rows[:1]] == [row["selected_probe_id"] for row in ig_rows[:1]],
                "full_probe_sequence_same": [row["selected_probe_id"] for row in ap_rows] == [row["selected_probe_id"] for row in ig_rows],
                "terminal_state_same": ap_final["state_after"] == ig_final["state_after"],
                "ap_observations": ap_final["cumulative_observations"],
                "ig_observations": ig_final["cumulative_observations"],
                "ap_cost": ap_final["cumulative_cost"],
                "ig_cost": ig_final["cumulative_cost"],
            }
            rows.append(item)
            all_case_comparisons.append(item)
        comparison_by_stratum[stratum] = {
            "cases": len(rows),
            "same_first_action": sum(row["first_action_same"] for row in rows),
            "same_full_probe_sequence": sum(row["full_probe_sequence_same"] for row in rows),
            "same_terminal_state": sum(row["terminal_state_same"] for row in rows),
            "ap_total_observations": sum(row["ap_observations"] for row in rows),
            "ig_total_observations": sum(row["ig_observations"] for row in rows),
            "ap_total_cost": sum(row["ap_cost"] for row in rows),
            "ig_total_cost": sum(row["ig_cost"] for row in rows),
        }

    public_states = {}
    for case in cases:
        for strategy in ("ap_minimax", "information_gain"):
            evidence = dict(case.initial_evidence)
            used = set()
            for row in selected(case.case_id, strategy):
                available_ids = tuple(sorted(probe.probe_id for probe in case.probes if probe.probe_id not in used))
                key = (case.case_id, tuple(sorted(evidence.items())), available_ids)
                public_states[key] = (
                    case,
                    dict(evidence),
                    tuple(probe for probe in case.probes if probe.probe_id not in used),
                )
                used.add(row["selected_probe_id"])
                evidence[row["selected_probe_id"]] = row["actual_outcome"]

    state_comparison = Counter()
    state_comparison_by_survivors = Counter()
    partition_patterns = Counter()
    for case, evidence, available in public_states.values():
        ap, ig, scored = objective_choices(case, evidence, available)
        same = ap.probe_id == ig.probe_id
        state_comparison["same_choice" if same else "different_choice"] += 1
        survivor_count = len(compatible(case, evidence))
        state_comparison_by_survivors[f"{survivor_count}_survivors/{'same' if same else 'different'}"] += 1
        for _, score in scored:
            partition_patterns[f"{survivor_count}_survivors/{','.join(map(str, score['sizes']))}"] += 1

    divergent_initial = Counter()
    divergent_residuals = Counter()
    divergent_immediate_cost = Counter()
    for case in cases:
        ap_rows = selected(case.case_id, "ap_minimax")
        ig_rows = selected(case.case_id, "information_gain")
        if not ap_rows or not ig_rows or ap_rows[0]["selected_probe_id"] == ig_rows[0]["selected_probe_id"]:
            continue
        evidence = dict(case.initial_evidence)
        survivors = compatible(case, evidence)
        probe_by_id = {probe.probe_id: probe for probe in case.probes}
        ap_probe = probe_by_id[ap_rows[0]["selected_probe_id"]]
        ig_probe = probe_by_id[ig_rows[0]["selected_probe_id"]]
        ap_score = probe_score(survivors, ap_probe)
        ig_score = probe_score(survivors, ig_probe)
        divergent_initial[f"{case.stratum}/{ap_score['sizes']}->{ig_score['sizes']}"] += 1
        actual = case.outcome_dict()
        ap_residual = sum(actual[ap_probe.probe_id] in item.predictions[ap_probe.probe_id] for item in survivors)
        ig_residual = sum(actual[ig_probe.probe_id] in item.predictions[ig_probe.probe_id] for item in survivors)
        divergent_residuals[f"AP={ap_residual}/IG={ig_residual}"] += 1
        divergent_immediate_cost[
            "AP_lower" if ap_probe.cost < ig_probe.cost else "AP_higher" if ap_probe.cost > ig_probe.cost else "equal"
        ] += 1

    generator_properties = Counter()
    cost_distribution = Counter()
    for case in cases:
        initial_count = len(compatible(case, dict(case.initial_evidence)))
        generator_properties[f"initial_compatible_count={initial_count}"] += 1
        for probe in case.probes:
            cost_distribution[str(probe.cost)] += 1
        for explanation in case.explanations:
            for probe in case.probes:
                if len(explanation.predictions[probe.probe_id]) == 1:
                    generator_properties["singleton_probe_predictions"] += 1
        if case.hidden_truth_id in {item.explanation_id for item in case.explanations}:
            truth = next(item for item in case.explanations if item.explanation_id == case.hidden_truth_id)
            for probe_id, actual in case.actual_outcomes:
                generator_properties["represented_truth_outcomes_checked"] += 1
                if actual in truth.predictions[probe_id]:
                    generator_properties["represented_truth_outcomes_matching_prediction"] += 1

        survivors = compatible(case, dict(case.initial_evidence))
        signatures = {
            item.explanation_id: tuple(
                next(iter(item.predictions[probe.probe_id])) for probe in case.probes
            )
            for item in survivors
        }
        if len(set(signatures.values())) == len(signatures):
            generator_properties[f"{case.stratum}/unique_survivor_signatures"] += 1
        else:
            generator_properties[f"{case.stratum}/nonunique_survivor_signatures"] += 1

    observations_relation = Counter()
    cost_relation = Counter()
    for row in all_case_comparisons:
        observations_relation[
            "AP_lower" if row["ap_observations"] < row["ig_observations"] else "AP_higher" if row["ap_observations"] > row["ig_observations"] else "equal"
        ] += 1
        cost_relation[
            "AP_lower" if row["ap_cost"] < row["ig_cost"] else "AP_higher" if row["ap_cost"] > row["ig_cost"] else "equal"
        ] += 1

    output = {
        "scope": "existing frozen case definitions plus preserved raw trace; no holdout execution",
        "case_comparison": {
            "cases": len(cases),
            "same_terminal_state": sum(row["terminal_state_same"] for row in all_case_comparisons),
            "same_first_action": sum(row["first_action_same"] for row in all_case_comparisons),
            "same_full_probe_sequence": sum(row["full_probe_sequence_same"] for row in all_case_comparisons),
            "observation_relation": dict(sorted(observations_relation.items())),
            "cost_relation": dict(sorted(cost_relation.items())),
            "by_stratum": comparison_by_stratum,
        },
        "objective_comparison_on_realized_public_states": {
            "unique_states": len(public_states),
            "choice_relation": dict(sorted(state_comparison.items())),
            "by_survivor_count": dict(sorted(state_comparison_by_survivors.items())),
            "available_probe_partition_patterns": dict(sorted(partition_patterns.items())),
        },
        "divergent_initial_choices": {
            "count": sum(divergent_initial.values()),
            "partition_transition_counts": dict(sorted(divergent_initial.items())),
            "realized_residual_counts": dict(sorted(divergent_residuals.items())),
            "immediate_probe_cost_relation": dict(sorted(divergent_immediate_cost.items())),
        },
        "generator_properties": dict(sorted(generator_properties.items())),
        "probe_cost_distribution": dict(sorted(cost_distribution.items())),
        "method_boundary": {
            "imports_or_calls_experiment_runner": False,
            "imports_or_calls_frozen_strategies": False,
            "uses_hidden_truth_to_choose_actions": False,
            "uses_hidden_truth_to_check_noiseless_realized_outcomes": True,
        },
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "divergent_initial_choices": sum(divergent_initial.values())}, sort_keys=True))


if __name__ == "__main__":
    main()
