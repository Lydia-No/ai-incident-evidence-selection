from __future__ import annotations

from collections.abc import Iterable, Mapping

from .model import (
    CompatibilityRecord,
    DecisionTrace,
    EvidenceMismatch,
    Explanation,
    InvestigationResult,
    InvestigationState,
    OperationalCheck,
    Probe,
    ProbeScore,
)


def _require_unique_ids(ids: Iterable[str], kind: str) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for identifier in ids:
        if identifier in seen:
            duplicates.add(identifier)
        seen.add(identifier)
    if duplicates:
        raise ValueError(f"{kind} identifiers must be unique: {sorted(duplicates)!r}")


def _compatibility_record(explanation: Explanation, observed_evidence: Mapping[str, str]) -> CompatibilityRecord:
    contradictions: list[EvidenceMismatch] = []
    for probe_id, observed_outcome in observed_evidence.items():
        allowed = explanation.predictions.get(probe_id)
        if allowed is None or observed_outcome not in allowed:
            contradictions.append(
                EvidenceMismatch(
                    probe_id=probe_id,
                    observed_outcome=observed_outcome,
                    compatible_outcomes=None if allowed is None else tuple(sorted(allowed)),
                )
            )
    return CompatibilityRecord(
        explanation_id=explanation.explanation_id,
        compatible=not contradictions,
        contradictions=tuple(contradictions),
    )


def compatible_explanations(explanations: Iterable[Explanation], observed_evidence: Mapping[str, str]) -> tuple[Explanation, ...]:
    explanation_tuple = tuple(explanations)
    _require_unique_ids((explanation.explanation_id for explanation in explanation_tuple), "explanation")
    return tuple(
        explanation
        for explanation in explanation_tuple
        if _compatibility_record(explanation, observed_evidence).compatible
    )


def _validate_probe_predictions(survivors: tuple[Explanation, ...], probe: Probe) -> None:
    declared = set(probe.outcomes)
    for explanation in survivors:
        allowed = explanation.predictions.get(probe.probe_id)
        if allowed is None:
            raise ValueError(
                f"surviving explanation {explanation.explanation_id!r} has no prediction for probe {probe.probe_id!r}"
            )
        undeclared = set(allowed) - declared
        if undeclared:
            raise ValueError(
                f"explanation {explanation.explanation_id!r} predicts undeclared outcomes "
                f"{sorted(undeclared)!r} for probe {probe.probe_id!r}"
            )


def score_probe(survivors: tuple[Explanation, ...], probe: Probe) -> ProbeScore:
    _validate_probe_predictions(survivors, probe)
    outcome_survivors: dict[str, tuple[str, ...]] = {}
    for outcome in probe.outcomes:
        ids = tuple(
            explanation.explanation_id
            for explanation in survivors
            if outcome in explanation.predictions[probe.probe_id]
        )
        if ids:
            outcome_survivors[outcome] = ids
    if not outcome_survivors:
        raise ValueError(f"probe {probe.probe_id!r} has no possible outcome")
    return ProbeScore(
        probe_id=probe.probe_id,
        worst_case_residual=max(len(ids) for ids in outcome_survivors.values()),
        cost=probe.cost,
        tie_rank=probe.tie_rank,
        outcome_survivors=outcome_survivors,
    )


def _is_discriminating(score: ProbeScore, survivor_count: int) -> bool:
    return any(len(ids) < survivor_count for ids in score.outcome_survivors.values())


def select_probe(survivors: tuple[Explanation, ...], probes: Iterable[Probe]) -> tuple[Probe | None, tuple[ProbeScore, ...]]:
    probe_tuple = tuple(probes)
    _require_unique_ids((probe.probe_id for probe in probe_tuple), "probe")
    scored_all: list[tuple[Probe, ProbeScore]] = [
        (probe, score_probe(survivors, probe))
        for probe in probe_tuple
    ]
    discriminating = [
        item
        for item in scored_all
        if _is_discriminating(item[1], len(survivors))
    ]

    if not discriminating:
        return None, tuple(score for _, score in scored_all)

    discriminating.sort(
        key=lambda item: (
            item[1].worst_case_residual,
            item[1].cost,
            item[1].tie_rank,
        )
    )
    best_key = (
        discriminating[0][1].worst_case_residual,
        discriminating[0][1].cost,
        discriminating[0][1].tie_rank,
    )
    if sum(
        (score.worst_case_residual, score.cost, score.tie_rank) == best_key
        for _, score in discriminating
    ) > 1:
        raise ValueError(
            "neutral tie_rank must uniquely resolve probes tied on worst-case residual ambiguity and cost"
        )
    return discriminating[0][0], tuple(score for _, score in scored_all)


def _operational_check(probe: Probe, score: ProbeScore, survivor_ids: tuple[str, ...]) -> OperationalCheck:
    survivor_set = set(survivor_ids)
    eliminations = {
        outcome: tuple(sorted(survivor_set - set(ids)))
        for outcome, ids in score.outcome_survivors.items()
    }
    possible_outcomes = tuple(score.outcome_survivors)
    resolving = tuple(outcome for outcome, ids in score.outcome_survivors.items() if len(ids) == 1)
    return OperationalCheck(
        probe_id=probe.probe_id,
        question=probe.question,
        source=probe.source,
        cost=probe.cost,
        outcomes=possible_outcomes,
        outcome_survivors=score.outcome_survivors,
        outcome_eliminations=eliminations,
        resolving_outcomes=resolving,
    )


def investigate(
    explanations: Iterable[Explanation],
    observed_evidence: Mapping[str, str],
    available_probes: Iterable[Probe],
) -> InvestigationResult:
    explanation_tuple = tuple(explanations)
    probe_tuple = tuple(available_probes)
    _require_unique_ids((explanation.explanation_id for explanation in explanation_tuple), "explanation")
    _require_unique_ids((probe.probe_id for probe in probe_tuple), "probe")

    records = tuple(_compatibility_record(explanation, observed_evidence) for explanation in explanation_tuple)
    survivors = tuple(
        explanation
        for explanation, record in zip(explanation_tuple, records, strict=True)
        if record.compatible
    )
    survivor_ids = tuple(explanation.explanation_id for explanation in survivors)
    observed_trace = tuple(sorted(observed_evidence.items()))

    if not survivors:
        return InvestigationResult(
            state=InvestigationState.MODEL_GAP,
            candidate_explanations=(),
            selected_cause=None,
            next_check=None,
            trace=DecisionTrace(observed_trace, records, (), None),
        )

    if len(survivors) == 1:
        return InvestigationResult(
            state=InvestigationState.RESOLVED,
            candidate_explanations=survivor_ids,
            selected_cause=survivor_ids[0],
            next_check=None,
            trace=DecisionTrace(observed_trace, records, (), None),
        )

    chosen_probe, scores = select_probe(survivors, probe_tuple)
    chosen_score = (
        next(score for score in scores if score.probe_id == chosen_probe.probe_id)
        if chosen_probe is not None
        else None
    )
    check = (
        _operational_check(chosen_probe, chosen_score, survivor_ids)
        if chosen_probe is not None and chosen_score is not None
        else None
    )
    return InvestigationResult(
        state=InvestigationState.UNRESOLVED,
        candidate_explanations=survivor_ids,
        selected_cause=None,
        next_check=check,
        trace=DecisionTrace(
            observed_evidence=observed_trace,
            compatibility=records,
            probe_scores=scores,
            chosen_probe_id=None if chosen_probe is None else chosen_probe.probe_id,
        ),
    )
