from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path

from experiments.cases import HOLDOUT_SEEDS, generate_suite
from experiments.run import run_case
from experiments.strategies import ALL_STRATEGIES
from investigator import Explanation


def signature(records, explanation_map=None):
    reverse = {new: old for old, new in (explanation_map or {}).items()}

    def normalize(identifier):
        return reverse.get(identifier, identifier)

    return [
        {
            "step": row["step"],
            "candidate_ids_before": sorted(normalize(item) for item in row["candidate_ids_before"]),
            "selected_probe_id": row["selected_probe_id"],
            "actual_outcome": row["actual_outcome"],
            "candidate_ids_after": sorted(normalize(item) for item in row["candidate_ids_after"]),
            "state_after": row["state_after"],
            "selected_cause": None if row["selected_cause"] is None else normalize(row["selected_cause"]),
            "terminal_action": row["terminal_action"],
            "cumulative_observations": row["cumulative_observations"],
            "cumulative_cost": row["cumulative_cost"],
        }
        for row in records
    ]


def renamed_case(case):
    old_ids = [item.explanation_id for item in case.explanations]
    labels = ("renamed-zulu", "renamed-alpha", "renamed-mike", "renamed-bravo")
    mapping = dict(zip(sorted(old_ids), labels, strict=True))
    explanations = tuple(
        Explanation(mapping[item.explanation_id], item.predictions)
        for item in case.explanations
    )
    return replace(
        case,
        explanations=explanations,
        hidden_truth_id=mapping.get(case.hidden_truth_id, case.hidden_truth_id),
        family_by_id=tuple((mapping[item_id], family) for item_id, family in case.family_by_id),
        explanation_neutral_rank=tuple((mapping[item_id], rank) for item_id, rank in case.explanation_neutral_rank),
    ), mapping


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")

    cases = tuple(case for seed in HOLDOUT_SEEDS for case in generate_suite(seed, holdout=True))
    failures = []
    checks = Counter()
    presentation_order_changes = 0
    for case in cases:
        renamed, mapping = renamed_case(case)
        variants = (
            ("explanation_renaming", renamed, mapping),
            ("explanation_order_reversal", replace(case, explanations=tuple(reversed(case.explanations))), None),
            ("probe_order_reversal", replace(case, probes=tuple(reversed(case.probes))), None),
        )
        for strategy in ALL_STRATEGIES:
            baseline_records = run_case(case, strategy)
            baseline = signature(baseline_records)
            for check_name, variant, explanation_map in variants:
                variant_records = run_case(variant, strategy)
                candidate_lists_baseline = [row["candidate_ids_before"] for row in baseline_records]
                candidate_lists_variant = [row["candidate_ids_before"] for row in variant_records]
                if check_name == "explanation_order_reversal" and candidate_lists_baseline != candidate_lists_variant:
                    presentation_order_changes += 1
                checks[check_name] += 1
                if baseline != signature(variant_records, explanation_map):
                    failures.append({"case_id": case.case_id, "strategy": strategy, "check": check_name})

    output = {
        "scope": "post-freeze metamorphic verification; not new experimental evidence",
        "holdout_cases_checked": len(cases),
        "strategies_checked": len(ALL_STRATEGIES),
        "checks": dict(sorted(checks.items())),
        "substantive_failures": failures,
        "substantive_failure_count": len(failures),
        "presentation_only_candidate_order_changes": presentation_order_changes,
        "interpretation": "Candidate list presentation order may follow explanation input order; terminal states, selected causes, selected probes, evidence, observations, and costs are compared after ID normalization and set-like candidate normalization.",
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "failures": len(failures)}, sort_keys=True))


if __name__ == "__main__":
    main()
