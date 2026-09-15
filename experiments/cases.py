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

    def evidence_dict(self) -> dict[str, str]: return dict(self.initial_evidence)
    def outcome_dict(self) -> dict[str, str]: return dict(self.actual_outcomes)
    def family_dict(self) -> dict[str, str]: return dict(self.family_by_id)
    def explanation_rank_dict(self) -> dict[str, int]: return dict(self.explanation_neutral_rank)


def _rng(seed: int, case_index: int, stream: int) -> random.Random:
    return random.Random(seed * 1_000_003 + case_index * 10_007 + stream * 997)


def _neutral_ranks(seed: int, case_index: int, n: int, stream: int) -> tuple[int, ...]:
    slots = list(range(n)); _rng(seed, case_index, stream).shuffle(slots); rank = [0] * n
    for ordinal, slot in enumerate(slots): rank[slot] = ordinal
    return tuple(rank)


def _random_partition(seed: int, case_index: int, slot: int, attempt: int) -> tuple[int, ...]:
    rng = _rng(seed, case_index, 1000 + attempt * 17 + slot); k = rng.choice((2, 2, 3)); values = [rng.randrange(k) for _ in range(4)]
    if len(set(values)) == 1: values[-1] = (values[-1] + 1) % k
    return tuple(values)


def _partition_quality(assignment, survivors): return max(Counter(assignment[index] for index in survivors).values())
def _is_discriminating_assignment(assignment, survivors): return len({assignment[index] for index in survivors}) > 1


def _generate_confusable_assignments(seed, case_index, survivors, include_nondiscriminating):
    for attempt in range(10_000):
        assignments = [_random_partition(seed, case_index, slot, attempt) for slot in range(5)]
        if include_nondiscriminating: assignments[4] = (0, 0, 0, 0)
        elif not _is_discriminating_assignment(assignments[4], survivors): continue
        if not all(_is_discriminating_assignment(item, survivors) for item in assignments[:4]): continue
        signatures = {index: tuple(a[index] for a in assignments) for index in survivors}
        if len(set(signatures.values())) != len(survivors): continue
        qualities = {_partition_quality(a, survivors) for a in assignments if _is_discriminating_assignment(a, survivors)}
        if len(qualities) >= 2: return tuple(assignments)
    raise RuntimeError("unable to generate confusable case satisfying frozen constraints")


def _generic_assignments(seed, case_index, unique_signatures=True):
    for attempt in range(10_000):
        assignments = tuple(_random_partition(seed, case_index, slot, attempt) for slot in range(5))
        if not unique_signatures: return assignments
        signatures = [tuple(a[index] for a in assignments) for index in range(4)]
        if len(set(signatures)) == 4: return assignments
    raise RuntimeError("unable to generate unique signatures")


def _materialize(*, seed, case_index, case_id, stratum, truth_index, hidden_truth_id, hidden_truth_family, families, pre_assignment, initial_evidence, assignments):
    probe_ranks = _neutral_ranks(seed, case_index, 5, 6000); explanation_ranks = _neutral_ranks(seed, case_index, 4, 7000)
    costs = tuple(float(_rng(seed, case_index, 5000 + slot).choice((1, 2, 3))) for slot in range(5))
    explanation_order = list(range(4)); _rng(seed, case_index, 8000).shuffle(explanation_order)
    probe_order = list(range(5)); _rng(seed, case_index, 8001).shuffle(probe_order)
    hypothesis_ids = tuple(f"h{index}" for index in range(4)); probe_ids = tuple(f"p{index}" for index in range(5))
    explanations = []
    for i, hid in enumerate(hypothesis_ids):
        predictions = {"pre": frozenset({pre_assignment[i]})}
        for slot, assignment in enumerate(assignments): predictions[probe_ids[slot]] = frozenset({f"o{assignment[i]}"})
        explanations.append(Explanation(explanation_id=hid, predictions=predictions))
    probes = []
    for slot, assignment in enumerate(assignments):
        probes.append(Probe(probe_id=probe_ids[slot], outcomes=tuple(f"o{v}" for v in sorted(set(assignment))), cost=costs[slot], tie_rank=probe_ranks[slot], question=f"Synthetic check {slot}", source=f"synthetic_source_{slot}"))
    actual_outcomes = () if truth_index is None else tuple((probe_ids[slot], f"o{assignments[slot][truth_index]}") for slot in range(5))
    return SyntheticCase(case_id, seed, stratum, tuple(explanations[i] for i in explanation_order), tuple(probes[i] for i in probe_order), initial_evidence, actual_outcomes, hidden_truth_id, hidden_truth_family, tuple(zip(hypothesis_ids, families, strict=True)), tuple((hypothesis_ids[i], explanation_ranks[i]) for i in range(4)))


def _confusable(seed, local_index):
    case_index = local_index; truth_index = local_index % 4; pre = ["KEEP"] * 4
    if local_index % 2 == 1:
        excluded = _rng(seed, case_index, 9000).choice([i for i in range(4) if i != truth_index]); pre[excluded] = "DROP"; survivors = tuple(i for i in range(4) if i != excluded); initial = (("pre", "KEEP"),)
    else: survivors = (0,1,2,3); initial = ()
    assignments = _generate_confusable_assignments(seed, case_index, survivors, local_index % 2 == 0)
    return _materialize(seed=seed, case_index=case_index, case_id=f"{seed}-confusable-{local_index:03d}", stratum="confusable_resolvable", truth_index=truth_index, hidden_truth_id=f"h{truth_index}", hidden_truth_family=FAILURE_FAMILIES[truth_index], families=FAILURE_FAMILIES, pre_assignment=tuple(pre), initial_evidence=initial, assignments=assignments)


def _clean_resolvable(seed, local_index):
    ci=1000+local_index; ti=local_index%4; pre=tuple("TRUTH" if i==ti else "OTHER" for i in range(4))
    return _materialize(seed=seed,case_index=ci,case_id=f"{seed}-clean-{local_index:03d}",stratum="clean_resolvable",truth_index=ti,hidden_truth_id=f"h{ti}",hidden_truth_family=FAILURE_FAMILIES[ti],families=FAILURE_FAMILIES,pre_assignment=pre,initial_evidence=(("pre","TRUTH"),),assignments=_generic_assignments(seed,ci))


def _persistent_ambiguity(seed, local_index):
    ci=2000+local_index; ti=local_index%4; twin=(ti+1)%4
    for attempt in range(10_000):
        raw=[list(x) for x in _generic_assignments(seed,ci+attempt,False)]
        for a in raw: a[twin]=a[ti]
        assignments=tuple(tuple(x) for x in raw); sig=[tuple(a[i] for a in assignments) for i in range(4)]; other=[i for i in range(4) if i not in (ti,twin)]
        if sig[ti]==sig[twin] and all(sig[i]!=sig[ti] for i in other): break
    else: raise RuntimeError("unable to generate persistent-ambiguity case")
    return _materialize(seed=seed,case_index=ci,case_id=f"{seed}-persistent-{local_index:03d}",stratum="persistent_ambiguity",truth_index=ti,hidden_truth_id=f"h{ti}",hidden_truth_family=FAILURE_FAMILIES[ti],families=FAILURE_FAMILIES,pre_assignment=("KEEP",)*4,initial_evidence=(),assignments=assignments)


def _model_gap(seed, local_index):
    ci=3000+local_index
    return _materialize(seed=seed,case_index=ci,case_id=f"{seed}-model-gap-{local_index:03d}",stratum="model_gap",truth_index=None,hidden_truth_id="external_truth",hidden_truth_family="unmodeled",families=FAILURE_FAMILIES,pre_assignment=("A","A","B","B"),initial_evidence=(("pre","GAP"),),assignments=_generic_assignments(seed,ci))


def _no_failure(seed, local_index):
    ci=4000+local_index
    return _materialize(seed=seed,case_index=ci,case_id=f"{seed}-no-failure-{local_index:03d}",stratum="no_failure",truth_index=3,hidden_truth_id="h3",hidden_truth_family="no_failure",families=("retrieval","tool","state","no_failure"),pre_assignment=("KEEP",)*4,initial_evidence=(),assignments=_generic_assignments(seed,ci))


def generate_suite(seed: int, *, holdout: bool) -> tuple[SyntheticCase, ...]:
    n=80 if holdout else 8; m=20 if holdout else 8
    return tuple([*(_confusable(seed,i) for i in range(n)), *(_clean_resolvable(seed,i) for i in range(m)), *(_persistent_ambiguity(seed,i) for i in range(m)), *(_model_gap(seed,i) for i in range(m)), *(_no_failure(seed,i) for i in range(m))])

def generate_holdout(): return tuple(case for seed in HOLDOUT_SEEDS for case in generate_suite(seed,holdout=True))
def case_counts(cases: Iterable[SyntheticCase]): return Counter(case.stratum for case in cases)
