from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from investigator import Explanation, Probe, compatible_explanations, investigate, score_probe

AP_MINIMAX = "ap_minimax"
FORCED_CLOSURE = "forced_closure"
NEUTRAL_ALL = "neutral_all"
NEUTRAL_DISCRIMINATING = "neutral_discriminating"
INFORMATION_GAIN = "information_gain"

SEQUENTIAL_STRATEGIES = (AP_MINIMAX, NEUTRAL_ALL, NEUTRAL_DISCRIMINATING, INFORMATION_GAIN)
ALL_STRATEGIES = (AP_MINIMAX, FORCED_CLOSURE, NEUTRAL_ALL, NEUTRAL_DISCRIMINATING, INFORMATION_GAIN)


def current_survivors(
    explanations: Sequence[Explanation],
    observed_evidence: Mapping[str, str],
) -> tuple[Explanation, ...]:
    return compatible_explanations(explanations, observed_evidence)


def _probe_by_id(probes: Sequence[Probe], probe_id: str) -> Probe:
    return next(probe for probe in probes if probe.probe_id == probe_id)


def _is_discriminating(survivors: tuple[Explanation, ...], probe: Probe) -> bool:
    score = score_probe(survivors, probe)
    return any(len(ids) < len(survivors) for ids in score.outcome_survivors.values())


def _information_gain(survivors: tuple[Explanation, ...], probe: Probe) -> float:
    if not survivors:
        return 0.0
    score = score_probe(survivors, probe)
    n = len(survivors)
    before = math.log2(n)
    expected_after = 0.0
    for ids in score.outcome_survivors.values():
        probability = len(ids) / n
        expected_after += probability * math.log2(len(ids))
    return before - expected_after


def choose_probe(
    strategy: str,
    explanations: Sequence[Explanation],
    observed_evidence: Mapping[str, str],
    available_probes: Sequence[Probe],
) -> Probe | None:
    """Choose a next probe without access to hidden truth or unrevealed outcomes."""
    survivors = current_survivors(explanations, observed_evidence)
    if len(survivors) <= 1 or not available_probes:
        return None

    if strategy == AP_MINIMAX:
        result = investigate(explanations, observed_evidence, available_probes)
        if result.next_check is None:
            return None
        return _probe_by_id(available_probes, result.next_check.probe_id)

    if strategy == NEUTRAL_ALL:
        return min(available_probes, key=lambda probe: probe.tie_rank)

    if strategy == NEUTRAL_DISCRIMINATING:
        candidates = tuple(probe for probe in available_probes if _is_discriminating(survivors, probe))
        if not candidates:
            return None
        return min(candidates, key=lambda probe: probe.tie_rank)

    if strategy == INFORMATION_GAIN:
        scored = [(probe, _information_gain(survivors, probe)) for probe in available_probes]
        best_gain = max(gain for _, gain in scored)
        if best_gain <= 1e-12:
            return None
        best = [probe for probe, gain in scored if math.isclose(gain, best_gain, rel_tol=0.0, abs_tol=1e-12)]
        return min(best, key=lambda probe: (probe.cost, probe.tie_rank))

    raise ValueError(f"unknown sequential strategy: {strategy!r}")


def forced_close(
    explanations: Sequence[Explanation],
    observed_evidence: Mapping[str, str],
    explanation_neutral_rank: Mapping[str, int],
) -> str | None:
    """Return the ablation's selected cause; None when attribution is impossible or unnecessary."""
    survivors = current_survivors(explanations, observed_evidence)
    if not survivors:
        return None
    if len(survivors) == 1:
        return survivors[0].explanation_id
    return min(survivors, key=lambda explanation: explanation_neutral_rank[explanation.explanation_id]).explanation_id
