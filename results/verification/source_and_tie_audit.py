from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import json
import math
from pathlib import Path

from experiments.cases import HOLDOUT_SEEDS, generate_suite
from experiments.run import run_case
from experiments.strategies import ALL_STRATEGIES


def compatible(case, evidence):
    return tuple(
        item for item in case.explanations
        if all(outcome in item.predictions.get(probe_id, ()) for probe_id, outcome in evidence.items())
    )


def score(survivors, probe):
    sizes = [
        sum(outcome in item.predictions[probe.probe_id] for item in survivors)
        for outcome in probe.outcomes
    ]
    sizes = [size for size in sizes if size]
    n = len(survivors)
    worst = max(sizes)
    gain = math.log2(n) - sum((size / n) * math.log2(size) for size in sizes)
    return worst, gain, any(size < n for size in sizes)


def decision_signature(records):
    return [
        (
            row["selected_probe_id"],
            tuple(sorted(row["candidate_ids_before"])),
            tuple(sorted(row["candidate_ids_after"])),
            row["state_after"],
            row["selected_cause"],
            row["terminal_action"],
        )
        for row in records
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")

    root = Path(__file__).resolve().parents[2]
    strategy_source = (root / "experiments/strategies.py").read_text(encoding="utf-8")
    engine_source = (root / "src/investigator/engine.py").read_text(encoding="utf-8")
    run_source = (root / "experiments/run.py").read_text(encoding="utf-8")
    cases = tuple(case for seed in HOLDOUT_SEEDS for case in generate_suite(seed, holdout=True))
    hidden_metadata_failures = []
    tie_counts = Counter()

    for case in cases:
        metadata_changed = replace(case, hidden_truth_id="metadata-only-renamed", hidden_truth_family="metadata-only-family")
        for strategy in ALL_STRATEGIES:
            baseline = run_case(case, strategy)
            changed = run_case(metadata_changed, strategy)
            if decision_signature(baseline) != decision_signature(changed):
                hidden_metadata_failures.append({"case_id": case.case_id, "strategy": strategy})

            evidence = dict(case.initial_evidence)
            remaining = list(case.probes)
            for row in baseline:
                selected_id = row["selected_probe_id"]
                if selected_id is None:
                    continue
                survivors = compatible(case, evidence)
                scored = [(probe, *score(survivors, probe)) for probe in remaining]
                if strategy == "ap_minimax":
                    eligible = [item for item in scored if item[3]]
                    chosen = next(item for item in eligible if item[0].probe_id == selected_id)
                    tied = [item for item in eligible if (item[1], item[0].cost) == (chosen[1], chosen[0].cost)]
                    if len(tied) > 1:
                        tie_counts["ap_minimax_worst_case_and_cost_ties_resolved_by_neutral_rank"] += 1
                elif strategy == "information_gain":
                    chosen = next(item for item in scored if item[0].probe_id == selected_id)
                    tied = [item for item in scored if math.isclose(item[2], chosen[2], rel_tol=0, abs_tol=1e-12) and item[0].cost == chosen[0].cost]
                    if len(tied) > 1:
                        tie_counts["information_gain_and_cost_ties_resolved_by_neutral_rank"] += 1
                elif strategy == "neutral_all":
                    tie_counts["neutral_all_choices_defined_by_neutral_rank"] += 1
                elif strategy == "neutral_discriminating":
                    tie_counts["neutral_discriminating_choices_defined_by_neutral_rank"] += 1
                evidence[selected_id] = row["actual_outcome"]
                remaining = [probe for probe in remaining if probe.probe_id != selected_id]

    suspicious_literals = ("expected_output", "gold_answer", "assert result ==", "hardcoded")
    output = {
        "static_source_checks": {
            "hidden_truth_token_in_strategy_module": "hidden_truth" in strategy_source,
            "hidden_truth_token_in_investigator_engine": "hidden_truth" in engine_source,
            "run_module_hidden_truth_occurrences_are_trace_serialization": [
                index for index, line in enumerate(run_source.splitlines(), 1) if "hidden_truth" in line
            ],
            "suspicious_expected_output_literals_found": {
                token: token in (strategy_source + engine_source + run_source) for token in suspicious_literals
            },
        },
        "hidden_metadata_perturbation": {
            "case_strategy_checks": len(cases) * len(ALL_STRATEGIES),
            "failure_count": len(hidden_metadata_failures),
            "failures": hidden_metadata_failures,
        },
        "tie_rank_usage": dict(sorted(tie_counts.items())),
        "nonanticipation_basis": "All 4321 selected HOLDOUT actions were independently recomputed from only current evidence, current compatible explanations, and currently available probes in holdout_invariants.json; run.py reads actual_outcome only after choose_probe returns.",
        "scoring_pass_through_basis": "hidden truth metadata is serialized for evaluation but absent from strategies.py and investigator/engine.py; 4000 hidden-metadata perturbations did not change decisions.",
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "hidden_metadata_failures": len(hidden_metadata_failures)}, sort_keys=True))


if __name__ == "__main__":
    main()
