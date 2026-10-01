import pytest

from investigator import Explanation, InvestigationState, Probe, investigate


def e(explanation_id, **predictions):
    return Explanation(
        explanation_id=explanation_id,
        predictions={key: frozenset(value) for key, value in predictions.items()},
    )


def p(probe_id, outcomes, *, cost=1.0, tie_rank=0):
    return Probe(
        probe_id=probe_id,
        outcomes=tuple(outcomes),
        cost=cost,
        tie_rank=tie_rank,
        question=f"Check {probe_id}",
        source=f"source:{probe_id}",
    )


def test_preserves_all_explanations_compatible_with_observed_evidence():
    explanations = (
        e("A", retrieval=("VALID",), tool=("CORRUPT",)),
        e("B", retrieval=("VALID",), tool=("VALID",)),
        e("C", retrieval=("INVALID",), tool=("VALID",)),
    )
    result = investigate(explanations, {"retrieval": "VALID"}, (p("tool", ("VALID", "CORRUPT")),))
    assert result.state == InvestigationState.UNRESOLVED
    assert set(result.candidate_explanations) == {"A", "B"}
    assert result.selected_cause is None


def test_unique_survivor_is_resolved():
    explanations = (e("A", retrieval=("VALID",)), e("B", retrieval=("INVALID",)))
    result = investigate(explanations, {"retrieval": "VALID"}, ())
    assert result.state == InvestigationState.RESOLVED
    assert result.candidate_explanations == ("A",)
    assert result.selected_cause == "A"
    assert result.next_check is None


def test_zero_survivors_surfaces_model_gap():
    explanations = (e("A", retrieval=("VALID",)), e("B", retrieval=("INVALID",)))
    result = investigate(explanations, {"retrieval": "UNKNOWN"}, ())
    assert result.state == InvestigationState.MODEL_GAP
    assert result.selected_cause is None


def test_minimax_selects_probe_with_smallest_worst_case_residual():
    explanations = (
        e("A", weak=("x",), strong=("x",)),
        e("B", weak=("x",), strong=("y",)),
        e("C", weak=("y",), strong=("z",)),
        e("D", weak=("y",), strong=("w",)),
    )
    result = investigate(
        explanations,
        {},
        (
            p("weak", ("x", "y"), tie_rank=1),
            p("strong", ("x", "y", "z", "w"), tie_rank=2),
        ),
    )
    assert result.next_check is not None
    assert result.next_check.probe_id == "strong"


def test_lower_cost_breaks_equal_minimax_score():
    explanations = (
        e("A", cheap=("x",), expensive=("x",)),
        e("B", cheap=("y",), expensive=("y",)),
    )
    result = investigate(
        explanations,
        {},
        (
            p("expensive", ("x", "y"), cost=2.0, tie_rank=1),
            p("cheap", ("x", "y"), cost=1.0, tie_rank=9),
        ),
    )
    assert result.next_check.probe_id == "cheap"


def test_neutral_tie_rank_breaks_remaining_tie_independent_of_input_order():
    explanations = (
        e("A", one=("x",), two=("x",)),
        e("B", one=("y",), two=("y",)),
    )
    one = p("one", ("x", "y"), tie_rank=20)
    two = p("two", ("x", "y"), tie_rank=10)
    forward = investigate(explanations, {}, (one, two))
    reversed_result = investigate(tuple(reversed(explanations)), {}, (two, one))
    assert forward.next_check.probe_id == "two"
    assert reversed_result.next_check.probe_id == "two"


def test_renaming_explanations_does_not_change_probe_choice():
    original = (
        e("A", first=("x",), second=("x",)),
        e("B", first=("x",), second=("y",)),
        e("C", first=("y",), second=("z",)),
    )
    renamed = (
        e("omega", first=("x",), second=("x",)),
        e("alpha", first=("x",), second=("y",)),
        e("kappa", first=("y",), second=("z",)),
    )
    probes = (
        p("first", ("x", "y"), tie_rank=5),
        p("second", ("x", "y", "z"), tie_rank=6),
    )
    assert investigate(original, {}, probes).next_check.probe_id == "second"
    assert investigate(renamed, {}, probes).next_check.probe_id == "second"


def test_future_unrevealed_evidence_does_not_affect_current_decision():
    explanations = (
        e("A", now=("x",), future=("left",)),
        e("B", now=("y",), future=("right",)),
    )
    now = p("now", ("x", "y"), tie_rank=1)
    baseline = investigate(explanations, {}, (now,))
    changed = investigate(
        (
            e("A", now=("x",), future=("right",)),
            e("B", now=("y",), future=("left",)),
        ),
        {},
        (now,),
    )
    assert baseline.state == changed.state == InvestigationState.UNRESOLVED
    assert baseline.next_check.probe_id == changed.next_check.probe_id == "now"


def test_dynamic_reveal_recomputes_compatibility():
    explanations = (e("A", tool=("CORRUPT",)), e("B", tool=("VALID",)))
    before = investigate(explanations, {}, (p("tool", ("VALID", "CORRUPT"), tie_rank=1),))
    after = investigate(explanations, {"tool": "VALID"}, ())
    assert before.state == InvestigationState.UNRESOLVED
    assert after.state == InvestigationState.RESOLVED
    assert after.selected_cause == "B"


def test_no_discriminating_probe_leaves_explicit_evidence_gap():
    explanations = (
        e("A", shared=("x", "y")),
        e("B", shared=("x", "y")),
    )
    result = investigate(explanations, {}, (p("shared", ("x", "y"), tie_rank=1),))
    assert result.state == InvestigationState.UNRESOLVED
    assert result.next_check is None


def test_operational_check_exposes_outcome_conditioned_causal_consequences():
    explanations = (
        e("retrieval", verify=("INVALID",)),
        e("tool", verify=("VALID",)),
    )
    result = investigate(
        explanations,
        {},
        (
            Probe(
                probe_id="verify",
                outcomes=("VALID", "INVALID"),
                cost=1.0,
                tie_rank=1,
                question="Verify retrieval integrity",
                source="retrieval logs",
            ),
        ),
    )
    check = result.next_check
    assert check.question == "Verify retrieval integrity"
    assert check.source == "retrieval logs"
    assert set(check.outcome_survivors["VALID"]) == {"tool"}
    assert set(check.outcome_eliminations["VALID"]) == {"retrieval"}
    assert set(check.resolving_outcomes) == {"VALID", "INVALID"}


def test_trace_records_why_an_explanation_was_eliminated():
    explanations = (e("A", retrieval=("VALID",)), e("B", retrieval=("INVALID",)))
    result = investigate(explanations, {"retrieval": "VALID"}, ())
    by_id = {record.explanation_id: record for record in result.trace.compatibility}
    assert by_id["A"].compatible is True
    assert by_id["B"].compatible is False
    assert by_id["B"].contradictions[0].probe_id == "retrieval"
    assert by_id["B"].contradictions[0].observed_outcome == "VALID"


def test_unresolved_probe_tie_without_unique_neutral_rank_fails_closed():
    explanations = (
        e("A", one=("x",), two=("x",)),
        e("B", one=("y",), two=("y",)),
    )
    with pytest.raises(ValueError, match="tie_rank"):
        investigate(
            explanations,
            {},
            (
                p("one", ("x", "y"), tie_rank=1),
                p("two", ("x", "y"), tie_rank=1),
            ),
        )


def test_trace_includes_nondiscriminating_probes_for_auditability():
    explanations = (
        e("A", useful=("x",), useless=("same",)),
        e("B", useful=("y",), useless=("same",)),
    )
    result = investigate(
        explanations,
        {},
        (
            p("useless", ("same",), tie_rank=1),
            p("useful", ("x", "y"), tie_rank=2),
        ),
    )
    assert result.next_check.probe_id == "useful"
    assert {score.probe_id for score in result.trace.probe_scores} == {"useful", "useless"}


def test_duplicate_explanation_identifiers_fail_closed():
    explanations = (
        e("same", verify=("VALID",)),
        e("same", verify=("INVALID",)),
    )
    with pytest.raises(ValueError, match="explanation identifiers must be unique"):
        investigate(explanations, {}, (p("verify", ("VALID", "INVALID"), tie_rank=1),))


def test_duplicate_probe_identifiers_fail_closed():
    explanations = (
        e("A", verify=("VALID",)),
        e("B", verify=("INVALID",)),
    )
    probes = (
        p("verify", ("VALID", "INVALID"), tie_rank=1),
        p("verify", ("VALID", "INVALID"), tie_rank=2),
    )
    with pytest.raises(ValueError, match="probe identifiers must be unique"):
        investigate(explanations, {}, probes)


def test_operational_check_lists_only_outcomes_possible_under_surviving_explanations():
    explanations = (
        e("A", verify=("VALID",)),
        e("B", verify=("INVALID",)),
    )
    result = investigate(
        explanations,
        {},
        (p("verify", ("VALID", "INVALID", "UNOBSERVED"), tie_rank=1),),
    )
    assert result.next_check.outcomes == ("VALID", "INVALID")
    assert "UNOBSERVED" not in result.next_check.outcome_survivors
