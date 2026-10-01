from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from investigator import InvestigationState, compatible_explanations, score_probe

from .cases import DEV_SEED, HOLDOUT_SEEDS, SyntheticCase, generate_suite
from .strategies import (
    ALL_STRATEGIES,
    FORCED_CLOSURE,
    choose_probe,
    forced_close,
)

EXPERIMENT_VERSION = "v0.1"


def _state_for_count(count: int) -> str:
    if count == 0:
        return InvestigationState.MODEL_GAP.value
    if count == 1:
        return InvestigationState.RESOLVED.value
    return InvestigationState.UNRESOLVED.value


def _evidence_snapshot(evidence: dict[str, str]) -> list[list[str]]:
    return [[probe_id, outcome] for probe_id, outcome in sorted(evidence.items())]


def _terminal_record(
    case: SyntheticCase,
    strategy: str,
    step: int,
    evidence: dict[str, str],
    survivors,
    cumulative_cost: float,
    *,
    selected_cause: str | None = None,
    terminal_action: str,
) -> dict:
    return {
        "experiment_version": EXPERIMENT_VERSION,
        "generator_version": case.generator_version,
        "seed": case.seed,
        "case_id": case.case_id,
        "stratum": case.stratum,
        "hidden_truth_id": case.hidden_truth_id,
        "hidden_truth_family": case.hidden_truth_family,
        "strategy": strategy,
        "step": step,
        "candidate_ids_before": [item.explanation_id for item in survivors],
        "candidate_count_before": len(survivors),
        "observed_evidence_before": _evidence_snapshot(evidence),
        "observed_evidence_ids_before": sorted(evidence),
        "selected_probe_id": None,
        "selected_probe_cost": None,
        "selected_probe_neutral_rank": None,
        "selected_partition_sizes": None,
        "actual_outcome": None,
        "candidate_ids_after": [item.explanation_id for item in survivors],
        "candidate_count_after": len(survivors),
        "state_after": _state_for_count(len(survivors)) if terminal_action != "forced_close" else "FORCED_CLOSED",
        "selected_cause": selected_cause,
        "terminal_action": terminal_action,
        "cumulative_observations": step,
        "cumulative_cost": cumulative_cost,
    }


def run_case(case: SyntheticCase, strategy: str) -> list[dict]:
    evidence = case.evidence_dict()
    outcomes = case.outcome_dict()
    remaining = list(case.probes)
    cumulative_cost = 0.0
    records: list[dict] = []

    survivors = compatible_explanations(case.explanations, evidence)

    if strategy == FORCED_CLOSURE:
        selected = forced_close(case.explanations, evidence, case.explanation_rank_dict())
        action = "forced_close" if len(survivors) > 1 else "terminal"
        records.append(
            _terminal_record(
                case,
                strategy,
                0,
                evidence,
                survivors,
                cumulative_cost,
                selected_cause=selected,
                terminal_action=action,
            )
        )
        return records

    for step in range(6):
        survivors = compatible_explanations(case.explanations, evidence)
        if len(survivors) == 0:
            records.append(
                _terminal_record(
                    case,
                    strategy,
                    step,
                    evidence,
                    survivors,
                    cumulative_cost,
                    terminal_action="model_gap",
                )
            )
            break
        if len(survivors) == 1:
            records.append(
                _terminal_record(
                    case,
                    strategy,
                    step,
                    evidence,
                    survivors,
                    cumulative_cost,
                    selected_cause=survivors[0].explanation_id,
                    terminal_action="resolved",
                )
            )
            break

        selected = choose_probe(strategy, case.explanations, evidence, tuple(remaining))
        if selected is None:
            records.append(
                _terminal_record(
                    case,
                    strategy,
                    step,
                    evidence,
                    survivors,
                    cumulative_cost,
                    terminal_action="unresolved_no_discriminating_probe",
                )
            )
            break

        score = score_probe(survivors, selected)
        partition_sizes = sorted(len(ids) for ids in score.outcome_survivors.values())
        actual_outcome = outcomes[selected.probe_id]
        before_ids = [item.explanation_id for item in survivors]
        evidence_before = _evidence_snapshot(evidence)
        evidence_ids_before = sorted(evidence)
        evidence = dict(evidence)
        evidence[selected.probe_id] = actual_outcome
        cumulative_cost += selected.cost
        remaining = [probe for probe in remaining if probe.probe_id != selected.probe_id]
        after = compatible_explanations(case.explanations, evidence)

        records.append(
            {
                "experiment_version": EXPERIMENT_VERSION,
                "generator_version": case.generator_version,
                "seed": case.seed,
                "case_id": case.case_id,
                "stratum": case.stratum,
                "hidden_truth_id": case.hidden_truth_id,
                "hidden_truth_family": case.hidden_truth_family,
                "strategy": strategy,
                "step": step,
                "candidate_ids_before": before_ids,
                "candidate_count_before": len(survivors),
                "observed_evidence_before": evidence_before,
                "observed_evidence_ids_before": evidence_ids_before,
                "selected_probe_id": selected.probe_id,
                "selected_probe_cost": selected.cost,
                "selected_probe_neutral_rank": selected.tie_rank,
                "selected_partition_sizes": partition_sizes,
                "actual_outcome": actual_outcome,
                "candidate_ids_after": [item.explanation_id for item in after],
                "candidate_count_after": len(after),
                "state_after": _state_for_count(len(after)),
                "selected_cause": after[0].explanation_id if len(after) == 1 else None,
                "terminal_action": None,
                "cumulative_observations": step + 1,
                "cumulative_cost": cumulative_cost,
            }
        )

        if len(after) <= 1:
            break
    return records


def run_cases(cases: Iterable[SyntheticCase]) -> list[dict]:
    records: list[dict] = []
    for case in cases:
        for strategy in ALL_STRATEGIES:
            records.extend(run_case(case, strategy))
    return records


def write_jsonl(records: Iterable[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")


def _cases_for_mode(mode: str) -> tuple[SyntheticCase, ...]:
    if mode == "dev":
        return generate_suite(DEV_SEED, holdout=False)
    if mode == "holdout":
        return tuple(
            case
            for seed in HOLDOUT_SEEDS
            for case in generate_suite(seed, holdout=True)
        )
    raise ValueError(mode)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("dev", "holdout"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = _cases_for_mode(args.mode)
    write_jsonl(run_cases(cases), args.output)


if __name__ == "__main__":
    main()
