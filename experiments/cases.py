from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random
from typing import Iterable

from investigator import Explanation, Probe

GENERATOR_VERSION = "v0.1"
FAILURE_FAMILIES = ("retrieval", "tool", "state", "control")
HOLDOUT_SEEDS = (26091301, 26091302, 26091303, 26091304, 26091305)
DEV_SEED = 26091200


@dataclass(frozen=True)
class SyntheticCase:
    case_id: str
    seed: int
    stratum: str
    explanations: tuple[Explanation, ...]
    probes: tuple[Probe, ...]
    initial_evidence: tuple[tuple[str, str], ...]
    actual_outcomes: tuple[tuple[str, str], ...]
    hidden_truth_id: str
    hidden_truth_family: str
    family_by_id: tuple[tuple[str, str], ...]
    explanation_neutral_rank: tuple[tuple[str, int], ...]
    generator_version: str = GENERATOR_VERSION

    def evidence_dict(self) -> dict[str, str]:
        return dict(self.initial_evidence)

    def outcome_dict(self) -> dict[str, str]:
        return dict(self.actual_outcomes)

    def family_dict(self) -> dict[str, str]:
        return dict(self.family_by_id)

    def explanation_rank_dict(self) -> dict[str, int]:
        return dict(self.explanation_neutral_rank)


def _rng(seed: int, case_index: int, stream: int) -> random.Random:
    return random.Random(seed * 1_000_003 + case_index * 10_007 + stream * 997)


def _neutral_ranks(seed: int, case_index: int, n: int, stream: int) -> tuple[int, ...]:
    slots = list(range(n))
    _rng(seed, case_index, stream).shuffle(slots)
    rank = [0] * n
    for ordinal, slot in enumerate(slots):
        rank[slot] = ordinal
    return tuple(rank)


def _random_partition(seed: int, case_index: int, slot: int, attempt: int) -> tuple[int, ...]:
    rng = _rng(seed, case_index, 1000 + attempt * 17 + slot)
    k = rng.choice((2, 2, 3))
    values = [rng.randrange(k) for _ in range(4)]
    if len(set(values)) == 1:
        values[-1] = (values[-1] + 1) % k
    return tuple(values)


def _partition_quality(assignment: tuple[int, ...], survivors: tuple[int, ...]) -> int:
    counts = Counter(assignment[index] for index in survivors)
    return max(counts.values())


def _is_discriminating_assignment(assignment: tuple[int, ...], survivors: tuple[int, ...]) -> bool:
    return len({assignment[index] for index in survivors}) > 1


def _generate_confusable_assignments(
    seed: int,
    case_index: int,
    survivors: tuple[int, ...],
    include_nondiscriminating: bool,
) -> tuple[tuple[int, ...], ...]:
    for attempt in range(10_000):
        assignments = [_random_partition(seed, case_index, slot, attempt) for slot in range(5)]
        if include_nondiscriminating:
            assignments[4] = (0, 0, 0, 0)
        elif not _is_discriminating_assignment(assignments[4], survivors):
            continue

        first_four = assignments[:4]
        if not all(_is_discriminating_assignment(item, survivors) for item in first_four):
            continue

        signatures = {
            index: tuple(assignment[index] for assignment in assignments)
            for index in survivors
        }
        if len(set(signatures.values())) != len(survivors):
            continue

        qualities = {
            _partition_quality(assignment, survivors)
            for assignment in assignments
            if _is_discriminating_assignment(assignment, survivors)
        }
        if len(qualities) < 2:
            continue
        return tuple(assignments)
    raise RuntimeError("unable to generate confusable case satisfying frozen constraints")


def _generic_assignments(seed: int, case_index: int, unique_signatures: bool = True) -> tuple[tuple[int, ...], ...]:
    for attempt in range(10_000):
        assignments = tuple(_random_partition(seed, case_index, slot, attempt) for slot in range(5))
        if not unique_signatures:
            return assignments
        signatures = [tuple(assignment[index] for assignment in assignments) for index in range(4)]
        if len(set(signatures)) == 4:
            return assignments
    raise RuntimeError("unable to generate unique signatures")


def _materialize(
    *,
    seed: int,
    case_index: int,
    case_id: str,
    stratum: str,
    truth_index: int | None,
    hidden_truth_id: str,
    hidden_truth_family: str,
    families: tuple[str, ...],
    pre_assignment: tuple[str, ...],
    initial_evidence: tuple[tuple[str, str], ...],
    assignments: tuple[tuple[int, ...], ...],
) -> SyntheticCase:
    # Freeze all neutral structural quantities before assigning human-readable IDs.
    probe_ranks = _neutral_ranks(seed, case_index, 5, 6000)
    explanation_ranks = _neutral_ranks(seed, case_index, 4, 7000)
    costs = tuple(float(_rng(seed, case_index, 5000 + slot).choice((1, 2, 3))) for slot in range(5))
    explanation_order = list(range(4))
    _rng(seed, case_index, 8000).shuffle(explanation_order)
    probe_order = list(range(5))
    _rng(seed, case_index, 8001).shuffle(probe_order)

    hypothesis_ids = tuple(f"h{index}" for index in range(4))
    probe_ids = tuple(f"p{index}" for index in range(5))

    explanations: list[Explanation] = []
    for hypothesis_index, hypothesis_id in enumerate(hypothesis_ids):
        predictions: dict[str, frozenset[str]] = {"pre": frozenset({pre_assignment[hypothesis_index]})}
        for slot, assignment in enumerate(assignments):
            predictions[probe_ids[slot]] = frozenset({f"o{assignment[hypothesis_index]}"})
        explanations.append(Explanation(explanation_id=hypothesis_id, predictions=predictions))

    probes = []
    for slot, assignment in enumerate(assignments):
        possible = tuple(f"o{value}" for value in sorted(set(assignment)))
        probes.append(
            Probe(
                probe_id=probe_ids[slot],
                outcomes=possible,
                cost=costs[slot],
                tie_rank=probe_ranks[slot],
                question=f"Synthetic check {slot}",
                source=f"synthetic_source_{slot}",
            )
        )

    ordered_explanations = tuple(explanations[index] for index in explanation_order)
    ordered_probes = tuple(probes[index] for index in probe_order)

    if truth_index is None:
        actual_outcomes: tuple[tuple[str, str], ...] = ()
    else:
        actual_outcomes = tuple(
            (probe_ids[slot], f"o{assignments[slot][truth_index]}")
            for slot in range(5)
        )

    return SyntheticCase(
        case_id=case_id,
        seed=seed,
        stratum=stratum,
        explanations=ordered_explanations,
        probes=ordered_probes,
        initial_evidence=initial_evidence,
        actual_outcomes=actual_outcomes,
        hidden_truth_id=hidden_truth_id,
        hidden_truth_family=hidden_truth_family,
        family_by_id=tuple(zip(hypothesis_ids, families, strict=True)),
        explanation_neutral_rank=tuple(
            (hypothesis_ids[index], explanation_ranks[index]) for index in range(4)
        ),
    )


def _confusable(seed: int, local_index: int) -> SyntheticCase:
    case_index = local_index
    truth_index = local_index % 4
    use_three_survivors = local_index % 2 == 1
    pre = ["KEEP"] * 4
    if use_three_survivors:
        choices = [index for index in range(4) if index != truth_index]
        excluded = _rng(seed, case_index, 9000).choice(choices)
        pre[excluded] = "DROP"
        survivors = tuple(index for index in range(4) if index != excluded)
        initial = (("pre", "KEEP"),)
    else:
        survivors = (0, 1, 2, 3)
        initial = ()

    assignments = _generate_confusable_assignments(
        seed,
        case_index,
        survivors,
        include_nondiscriminating=(local_index % 2 == 0),
    )
    return _materialize(
        seed=seed,
        case_index=case_index,
        case_id=f"{seed}-confusable-{local_index:03d}",
        stratum="confusable_resolvable",
        truth_index=truth_index,
        hidden_truth_id=f"h{truth_index}",
        hidden_truth_family=FAILURE_FAMILIES[truth_index],
        families=FAILURE_FAMILIES,
        pre_assignment=tuple(pre),
        initial_evidence=initial,
        assignments=assignments,
    )


def _clean_resolvable(seed: int, local_index: int) -> SyntheticCase:
    case_index = 1000 + local_index
    truth_index = local_index % 4
    pre = tuple("TRUTH" if index == truth_index else "OTHER" for index in range(4))
    return _materialize(
        seed=seed,
        case_index=case_index,
        case_id=f"{seed}-clean-{local_index:03d}",
        stratum="clean_resolvable",
        truth_index=truth_index,
        hidden_truth_id=f"h{truth_index}",
        hidden_truth_family=FAILURE_FAMILIES[truth_index],
        families=FAILURE_FAMILIES,
        pre_assignment=pre,
        initial_evidence=(("pre", "TRUTH"),),
        assignments=_generic_assignments(seed, case_index),
    )


def _persistent_ambiguity(seed: int, local_index: int) -> SyntheticCase:
    case_index = 2000 + local_index
    truth_index = local_index % 4
    twin = (truth_index + 1) % 4
    for attempt in range(10_000):
        raw = [list(item) for item in _generic_assignments(seed, case_index + attempt, unique_signatures=False)]
        for assignment in raw:
            assignment[twin] = assignment[truth_index]
        assignments = tuple(tuple(item) for item in raw)
        signatures = [tuple(item[index] for item in assignments) for index in range(4)]
        if signatures[truth_index] != signatures[twin]:
            continue
        other = [index for index in range(4) if index not in (truth_index, twin)]
        if all(signatures[index] != signatures[truth_index] for index in other):
            break
    else:
        raise RuntimeError("unable to generate persistent-ambiguity case")

    return _materialize(
        seed=seed,
        case_index=case_index,
        case_id=f"{seed}-persistent-{local_index:03d}",
        stratum="persistent_ambiguity",
        truth_index=truth_index,
        hidden_truth_id=f"h{truth_index}",
        hidden_truth_family=FAILURE_FAMILIES[truth_index],
        families=FAILURE_FAMILIES,
        pre_assignment=("KEEP", "KEEP", "KEEP", "KEEP"),
        initial_evidence=(),
        assignments=assignments,
    )


def _model_gap(seed: int, local_index: int) -> SyntheticCase:
    case_index = 3000 + local_index
    return _materialize(
        seed=seed,
        case_index=case_index,
        case_id=f"{seed}-model-gap-{local_index:03d}",
        stratum="model_gap",
        truth_index=None,
        hidden_truth_id="external_truth",
        hidden_truth_family="unmodeled",
        families=FAILURE_FAMILIES,
        pre_assignment=("A", "A", "B", "B"),
        initial_evidence=(("pre", "GAP"),),
        assignments=_generic_assignments(seed, case_index),
    )


def _no_failure(seed: int, local_index: int) -> SyntheticCase:
    case_index = 4000 + local_index
    truth_index = 3
    families = ("retrieval", "tool", "state", "no_failure")
    assignments = _generic_assignments(seed, case_index)
    return _materialize(
        seed=seed,
        case_index=case_index,
        case_id=f"{seed}-no-failure-{local_index:03d}",
        stratum="no_failure",
        truth_index=truth_index,
        hidden_truth_id="h3",
        hidden_truth_family="no_failure",
        families=families,
        pre_assignment=("KEEP", "KEEP", "KEEP", "KEEP"),
        initial_evidence=(),
        assignments=assignments,
    )


def generate_suite(seed: int, *, holdout: bool) -> tuple[SyntheticCase, ...]:
    per_stratum = {
        "confusable": 80 if holdout else 8,
        "clean": 20 if holdout else 8,
        "persistent": 20 if holdout else 8,
        "gap": 20 if holdout else 8,
        "no_failure": 20 if holdout else 8,
    }
    cases: list[SyntheticCase] = []
    cases.extend(_confusable(seed, index) for index in range(per_stratum["confusable"]))
    cases.extend(_clean_resolvable(seed, index) for index in range(per_stratum["clean"]))
    cases.extend(_persistent_ambiguity(seed, index) for index in range(per_stratum["persistent"]))
    cases.extend(_model_gap(seed, index) for index in range(per_stratum["gap"]))
    cases.extend(_no_failure(seed, index) for index in range(per_stratum["no_failure"]))
    return tuple(cases)


def generate_holdout() -> tuple[SyntheticCase, ...]:
    return tuple(case for seed in HOLDOUT_SEEDS for case in generate_suite(seed, holdout=True))


def case_counts(cases: Iterable[SyntheticCase]) -> Counter[str]:
    return Counter(case.stratum for case in cases)
