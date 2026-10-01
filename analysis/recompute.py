from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Iterable, Mapping, Sequence

ANALYSIS_VERSION = "v0.1"
BOOTSTRAP_SEED = 26091399
BOOTSTRAP_REPLICATES = 10_000
AP_MINIMAX = "ap_minimax"
FORCED_CLOSURE = "forced_closure"
NEUTRAL_ALL = "neutral_all"
NEUTRAL_DISCRIMINATING = "neutral_discriminating"
INFORMATION_GAIN = "information_gain"
CONFUSABLE = "confusable_resolvable"


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def first_action_records(records: Iterable[Mapping], *, strategy: str, stratum: str = CONFUSABLE) -> dict[str, Mapping]:
    by_case: dict[str, Mapping] = {}
    for record in records:
        if record.get("strategy") != strategy or record.get("stratum") != stratum:
            continue
        if record.get("selected_probe_id") is None:
            continue
        case_id = str(record["case_id"])
        step = int(record["step"])
        current = by_case.get(case_id)
        if current is None or step < int(current["step"]):
            by_case[case_id] = record
    return by_case


def realized_value(record: Mapping) -> float:
    cost = record.get("selected_probe_cost")
    if cost is None or float(cost) <= 0:
        raise ValueError("first-check realized value requires a positive selected probe cost")
    before = int(record["candidate_count_before"])
    after = int(record["candidate_count_after"])
    if after > before:
        raise ValueError("candidate count cannot increase after revealing evidence")
    return (before - after) / float(cost)


def paired_first_check(records: Sequence[Mapping], strategy_a: str, strategy_b: str) -> list[dict]:
    a = first_action_records(records, strategy=strategy_a)
    b = first_action_records(records, strategy=strategy_b)
    if set(a) != set(b):
        missing_a = sorted(set(b) - set(a))
        missing_b = sorted(set(a) - set(b))
        raise ValueError(
            f"paired comparison requires identical case sets; missing from {strategy_a}: {missing_a[:5]!r}; "
            f"missing from {strategy_b}: {missing_b[:5]!r}"
        )
    rows: list[dict] = []
    for case_id in sorted(a):
        ra = a[case_id]
        rb = b[case_id]
        if int(ra["seed"]) != int(rb["seed"]):
            raise ValueError(f"seed mismatch for case {case_id}")
        value_a = realized_value(ra)
        value_b = realized_value(rb)
        rows.append(
            {
                "case_id": case_id,
                "seed": int(ra["seed"]),
                "value_a": value_a,
                "value_b": value_b,
                "difference": value_a - value_b,
            }
        )
    return rows


def _nearest_rank(sorted_values: Sequence[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("cannot compute percentile of empty sequence")
    rank = max(1, min(len(sorted_values), int(probability * len(sorted_values) + 0.999999999999)))
    return sorted_values[rank - 1]


def paired_bootstrap_interval(
    differences: Sequence[float],
    *,
    seed: int = BOOTSTRAP_SEED,
    replicates: int = BOOTSTRAP_REPLICATES,
) -> tuple[float, float]:
    if not differences:
        raise ValueError("bootstrap requires at least one paired difference")
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    rng = random.Random(seed)
    n = len(differences)
    bootstrap_means = [
        mean(differences[rng.randrange(n)] for _ in range(n))
        for _ in range(replicates)
    ]
    bootstrap_means.sort()
    return _nearest_rank(bootstrap_means, 0.025), _nearest_rank(bootstrap_means, 0.975)


def paired_summary(rows: Sequence[Mapping]) -> dict:
    differences = [float(row["difference"]) for row in rows]
    lower, upper = paired_bootstrap_interval(differences)
    wins = sum(value > 0 for value in differences)
    ties = sum(value == 0 for value in differences)
    losses = sum(value < 0 for value in differences)
    by_seed: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        by_seed[int(row["seed"])].append(float(row["difference"]))
    seed_means = {str(seed): mean(values) for seed, values in sorted(by_seed.items())}
    return {
        "n": len(rows),
        "mean_difference": mean(differences),
        "bootstrap_95": [lower, upper],
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "seed_mean_differences": seed_means,
        "positive_seed_count": sum(value > 0 for value in seed_means.values()),
    }


def h1_premature_closure(records: Sequence[Mapping]) -> dict:
    """Recompute unsupported attribution directly from trace state, not implementation summaries."""
    output: dict[str, dict] = {}
    for strategy in (AP_MINIMAX, FORCED_CLOSURE):
        decisions = [
            record
            for record in records
            if record.get("strategy") == strategy
            and record.get("stratum") == CONFUSABLE
            and record.get("selected_cause") is not None
        ]
        unsupported = [
            record
            for record in decisions
            if int(record.get("candidate_count_before", 0)) > 1
            and record.get("state_after") != "RESOLVED"
        ]
        output[strategy] = {
            "attribution_decisions": len(decisions),
            "unsupported_attributions": len(unsupported),
            "premature_closure_rate": (len(unsupported) / len(decisions)) if decisions else None,
        }
    return output


def h2_decision(records: Sequence[Mapping]) -> dict:
    versus_all_rows = paired_first_check(records, AP_MINIMAX, NEUTRAL_ALL)
    versus_disc_rows = paired_first_check(records, AP_MINIMAX, NEUTRAL_DISCRIMINATING)
    versus_all = paired_summary(versus_all_rows)
    versus_disc = paired_summary(versus_disc_rows)

    all_positive_ci = versus_all["mean_difference"] > 0 and versus_all["bootstrap_95"][0] > 0
    disc_positive_ci = versus_disc["mean_difference"] > 0 and versus_disc["bootstrap_95"][0] > 0
    seed_stable = versus_all["positive_seed_count"] >= 4

    if all_positive_ci and seed_stable and disc_positive_ci:
        decision = "PASS"
    elif versus_all["mean_difference"] > 0:
        decision = "PARTIAL"
    else:
        decision = "FAIL"

    return {
        "analysis_version": ANALYSIS_VERSION,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "decision": decision,
        "ap_minus_neutral_all": versus_all,
        "ap_minus_neutral_discriminating": versus_disc,
    }


def trajectory_summary(records: Sequence[Mapping]) -> dict:
    by_strategy_case: dict[tuple[str, str], list[Mapping]] = defaultdict(list)
    for record in records:
        by_strategy_case[(str(record["strategy"]), str(record["case_id"]))].append(record)

    out: dict[str, dict] = {}
    strategy_rows: dict[str, list[dict]] = defaultdict(list)
    for (strategy, case_id), rows in by_strategy_case.items():
        rows = sorted(rows, key=lambda item: int(item["step"]))
        last = rows[-1]
        selected_cause = last.get("selected_cause")
        hidden_truth = last.get("hidden_truth_id")
        terminal_state = last.get("state_after")
        valid_resolution = terminal_state == "RESOLVED" and selected_cause == hidden_truth
        strategy_rows[strategy].append(
            {
                "case_id": case_id,
                "stratum": last.get("stratum"),
                "valid_resolution": valid_resolution,
                "state": terminal_state,
                "observations": int(last.get("cumulative_observations", 0)),
                "cost": float(last.get("cumulative_cost", 0.0)),
            }
        )

    for strategy, rows in sorted(strategy_rows.items()):
        valid_rows = [row for row in rows if row["valid_resolution"]]
        out[strategy] = {
            "n_cases": len(rows),
            "valid_resolution_rate": sum(row["valid_resolution"] for row in rows) / len(rows),
            "mean_observations": mean(row["observations"] for row in rows),
            "mean_cost": mean(row["cost"] for row in rows),
            "mean_observations_to_valid_resolution": mean(row["observations"] for row in valid_rows) if valid_rows else None,
            "mean_cost_to_valid_resolution": mean(row["cost"] for row in valid_rows) if valid_rows else None,
            "model_gap_rate_on_model_gap_controls": _state_rate(rows, "model_gap", "MODEL_GAP"),
            "unresolved_rate_on_persistent_controls": _state_rate(rows, "persistent_ambiguity", "UNRESOLVED"),
            "valid_resolution_rate_on_clean_controls": _valid_resolution_rate(rows, "clean_resolvable"),
            "valid_resolution_rate_on_no_failure_controls": _valid_resolution_rate(rows, "no_failure"),
        }
    return out


def true_explanation_retention(records: Sequence[Mapping]) -> dict:
    by_strategy: dict[str, list[bool]] = defaultdict(list)
    for record in records:
        truth = record.get("hidden_truth_id")
        if truth in (None, "external_truth"):
            continue
        if int(record.get("candidate_count_before", 0)) <= 1:
            continue
        candidate_ids = set(record.get("candidate_ids_before") or [])
        by_strategy[str(record["strategy"])].append(truth in candidate_ids)
    return {
        strategy: {
            "eligible_steps": len(values),
            "retained_steps": sum(values),
            "retention_rate": (sum(values) / len(values)) if values else None,
        }
        for strategy, values in sorted(by_strategy.items())
    }


def _state_rate(rows: Sequence[Mapping], stratum: str, state: str) -> float | None:
    selected = [row for row in rows if row.get("stratum") == stratum]
    if not selected:
        return None
    return sum(row.get("state") == state for row in selected) / len(selected)


def _valid_resolution_rate(rows: Sequence[Mapping], stratum: str) -> float | None:
    selected = [row for row in rows if row.get("stratum") == stratum]
    if not selected:
        return None
    return sum(bool(row.get("valid_resolution")) for row in selected) / len(selected)


def analyze(records: Sequence[Mapping]) -> dict:
    return {
        "analysis_version": ANALYSIS_VERSION,
        "h1": h1_premature_closure(records),
        "h2": h2_decision(records),
        "true_explanation_retention": true_explanation_retention(records),
        "trajectory": trajectory_summary(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_jsonl", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = analyze(load_jsonl(args.raw_jsonl))
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
