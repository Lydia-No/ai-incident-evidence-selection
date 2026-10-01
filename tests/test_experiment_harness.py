from collections import Counter
import inspect

import pytest

from investigator import Explanation, Probe, compatible_explanations, score_probe
from experiments.cases import DEV_SEED, FAILURE_FAMILIES, HOLDOUT_SEEDS, generate_suite
from experiments.run import run_case
from experiments.strategies import (
    AP_MINIMAX,
    FORCED_CLOSURE,
    INFORMATION_GAIN,
    NEUTRAL_ALL,
    NEUTRAL_DISCRIMINATING,
    choose_probe,
    forced_close,
)


@pytest.fixture(scope="module")
def holdout_seed_suite():
    return generate_suite(HOLDOUT_SEEDS[0], holdout=True)


@pytest.fixture(scope="module")
def dev_suite():
    return generate_suite(DEV_SEED, holdout=False)


def test_frozen_suite_counts(holdout_seed_suite, dev_suite):
    assert len(holdout_seed_suite) == 160
    assert Counter(case.stratum for case in holdout_seed_suite) == {
        "confusable_resolvable": 80,
        "clean_resolvable": 20,
        "persistent_ambiguity": 20,
        "model_gap": 20,
        "no_failure": 20,
    }
    assert len(dev_suite) == 40
    assert Counter(case.stratum for case in dev_suite) == {
        "confusable_resolvable": 8,
        "clean_resolvable": 8,
        "persistent_ambiguity": 8,
        "model_gap": 8,
        "no_failure": 8,
    }


def test_generation_is_deterministic_for_same_seed():
    assert generate_suite(DEV_SEED, holdout=False) == generate_suite(DEV_SEED, holdout=False)


def test_confusable_holdout_is_family_balanced_and_initially_ambiguous(holdout_seed_suite):
    cases = [case for case in holdout_seed_suite if case.stratum == "confusable_resolvable"]
    assert Counter(case.hidden_truth_family for case in cases) == {family: 20 for family in FAILURE_FAMILIES}
    candidate_counts = Counter()
    for case in cases:
        survivors = compatible_explanations(case.explanations, case.evidence_dict())
        candidate_counts[len(survivors)] += 1
        assert case.hidden_truth_id in {item.explanation_id for item in survivors}
    assert candidate_counts == {4: 40, 3: 40}


def test_confusable_cases_satisfy_frozen_probe_constraints(holdout_seed_suite):
    for case in (item for item in holdout_seed_suite if item.stratum == "confusable_resolvable"):
        survivors = compatible_explanations(case.explanations, case.evidence_dict())
        scores = [score_probe(survivors, probe) for probe in case.probes]
        discriminating = [
            score
            for score in scores
            if any(len(ids) < len(survivors) for ids in score.outcome_survivors.values())
        ]
        assert len(discriminating) >= 2
        assert len({score.worst_case_residual for score in discriminating}) >= 2

        signatures = []
        for explanation in survivors:
            signatures.append(
                tuple(next(iter(explanation.predictions[probe.probe_id])) for probe in case.probes)
            )
        assert len(set(signatures)) == len(signatures)
        assert sorted(probe.tie_rank for probe in case.probes) == [0, 1, 2, 3, 4]
        assert all(probe.cost in (1.0, 2.0, 3.0) for probe in case.probes)

        local_index = int(case.case_id.rsplit("-", 1)[1])
        nondiscriminating = [score for score in scores if score not in discriminating]
        if local_index % 2 == 0:
            assert nondiscriminating
        else:
            assert not nondiscriminating


def test_clean_resolvable_controls_start_with_one_warranted_truth(holdout_seed_suite):
    for case in (item for item in holdout_seed_suite if item.stratum == "clean_resolvable"):
        survivors = compatible_explanations(case.explanations, case.evidence_dict())
        assert [item.explanation_id for item in survivors] == [case.hidden_truth_id]


def test_persistent_ambiguity_is_not_identifiable_even_with_all_truth_outcomes(holdout_seed_suite):
    for case in (item for item in holdout_seed_suite if item.stratum == "persistent_ambiguity"):
        evidence = case.evidence_dict()
        evidence.update(case.outcome_dict())
        survivors = compatible_explanations(case.explanations, evidence)
        assert len(survivors) >= 2
        assert case.hidden_truth_id in {item.explanation_id for item in survivors}


def test_model_gap_controls_have_no_compatible_modeled_explanation(holdout_seed_suite):
    for case in (item for item in holdout_seed_suite if item.stratum == "model_gap"):
        assert compatible_explanations(case.explanations, case.evidence_dict()) == ()


def test_no_failure_truth_is_preserved_and_identifiable_by_full_frozen_evidence(holdout_seed_suite):
    for case in (item for item in holdout_seed_suite if item.stratum == "no_failure"):
        initial = compatible_explanations(case.explanations, case.evidence_dict())
        assert case.hidden_truth_id in {item.explanation_id for item in initial}
        evidence = case.evidence_dict()
        evidence.update(case.outcome_dict())
        final = compatible_explanations(case.explanations, evidence)
        assert [item.explanation_id for item in final] == [case.hidden_truth_id]
        assert case.hidden_truth_family == "no_failure"


def test_strategy_selector_has_no_hidden_truth_or_case_argument():
    params = tuple(inspect.signature(choose_probe).parameters)
    assert params == ("strategy", "explanations", "observed_evidence", "available_probes")
    assert all("truth" not in name and "case" not in name for name in params)


@pytest.mark.parametrize(
    "strategy",
    [AP_MINIMAX, NEUTRAL_ALL, NEUTRAL_DISCRIMINATING, INFORMATION_GAIN],
)
def test_sequential_strategy_choice_is_input_order_invariant(dev_suite, strategy):
    case = next(item for item in dev_suite if item.stratum == "confusable_resolvable")
    original = choose_probe(strategy, case.explanations, case.evidence_dict(), case.probes)
    reversed_choice = choose_probe(
        strategy,
        tuple(reversed(case.explanations)),
        case.evidence_dict(),
        tuple(reversed(case.probes)),
    )
    assert original is not None
    assert reversed_choice is not None
    assert original.probe_id == reversed_choice.probe_id


@pytest.mark.parametrize(
    "strategy",
    [AP_MINIMAX, NEUTRAL_ALL, NEUTRAL_DISCRIMINATING, INFORMATION_GAIN],
)
def test_sequential_strategy_choice_is_explanation_rename_invariant(dev_suite, strategy):
    case = next(item for item in dev_suite if item.stratum == "confusable_resolvable")
    original = choose_probe(strategy, case.explanations, case.evidence_dict(), case.probes)
    renamed = tuple(
        Explanation(explanation_id=f"renamed_{index}", predictions=explanation.predictions)
        for index, explanation in enumerate(case.explanations)
    )
    changed = choose_probe(strategy, renamed, case.evidence_dict(), case.probes)
    assert original is not None
    assert changed is not None
    assert original.probe_id == changed.probe_id


@pytest.mark.parametrize(
    "strategy",
    [AP_MINIMAX, NEUTRAL_ALL, NEUTRAL_DISCRIMINATING, INFORMATION_GAIN],
)
def test_sequential_strategy_choice_is_probe_rename_invariant(dev_suite, strategy):
    case = next(item for item in dev_suite if item.stratum == "confusable_resolvable")
    probe_map = {probe.probe_id: f"renamed_probe_{index}" for index, probe in enumerate(case.probes)}
    original = choose_probe(strategy, case.explanations, case.evidence_dict(), case.probes)

    renamed_explanations = tuple(
        Explanation(
            explanation_id=explanation.explanation_id,
            predictions={probe_map.get(key, key): value for key, value in explanation.predictions.items()},
        )
        for explanation in case.explanations
    )
    renamed_probes = tuple(
        Probe(
            probe_id=probe_map[probe.probe_id],
            outcomes=probe.outcomes,
            cost=probe.cost,
            tie_rank=probe.tie_rank,
            question=probe.question,
            source=probe.source,
        )
        for probe in case.probes
    )
    renamed_evidence = {probe_map.get(key, key): value for key, value in case.evidence_dict().items()}
    changed = choose_probe(strategy, renamed_explanations, renamed_evidence, renamed_probes)

    assert original is not None
    assert changed is not None
    assert changed.probe_id == probe_map[original.probe_id]


def test_forced_closure_is_explanation_rename_invariant(dev_suite):
    case = next(item for item in dev_suite if item.stratum == "confusable_resolvable")
    original = forced_close(case.explanations, case.evidence_dict(), case.explanation_rank_dict())
    id_map = {explanation.explanation_id: f"renamed_{index}" for index, explanation in enumerate(case.explanations)}
    renamed_explanations = tuple(
        Explanation(explanation_id=id_map[explanation.explanation_id], predictions=explanation.predictions)
        for explanation in case.explanations
    )
    renamed_ranks = {id_map[key]: value for key, value in case.explanation_rank_dict().items()}
    changed = forced_close(renamed_explanations, case.evidence_dict(), renamed_ranks)
    assert changed == id_map[original]


def test_raw_action_trace_replays_candidate_transition(dev_suite):
    case = next(item for item in dev_suite if item.stratum == "confusable_resolvable")
    records = run_case(case, AP_MINIMAX)
    evidence = case.evidence_dict()
    by_probe = {probe.probe_id: probe for probe in case.probes}

    for record in records:
        assert dict(record["observed_evidence_before"]) == evidence
        assert record["observed_evidence_ids_before"] == sorted(evidence)
        survivors = compatible_explanations(case.explanations, evidence)
        assert set(record["candidate_ids_before"]) == {item.explanation_id for item in survivors}
        if record["selected_probe_id"] is None:
            continue
        probe_id = record["selected_probe_id"]
        assert probe_id in by_probe
        assert record["actual_outcome"] == case.outcome_dict()[probe_id]
        evidence[probe_id] = record["actual_outcome"]
        after = compatible_explanations(case.explanations, evidence)
        assert set(record["candidate_ids_after"]) == {item.explanation_id for item in after}


def test_forced_closure_ablation_closes_while_ambiguity_remains(dev_suite):
    case = next(item for item in dev_suite if item.stratum == "confusable_resolvable")
    record = run_case(case, FORCED_CLOSURE)[0]
    assert record["candidate_count_before"] > 1
    assert record["terminal_action"] == "forced_close"
    assert record["state_after"] == "FORCED_CLOSED"
    assert record["selected_cause"] in record["candidate_ids_before"]


def test_information_gain_stops_when_persistent_pair_has_zero_gain(dev_suite):
    case = next(item for item in dev_suite if item.stratum == "persistent_ambiguity")
    records = run_case(case, INFORMATION_GAIN)
    terminal = records[-1]
    assert terminal["selected_probe_id"] is None
    assert terminal["terminal_action"] == "unresolved_no_discriminating_probe"
    assert terminal["candidate_count_before"] >= 2


def test_case_ids_are_unique_and_actual_outcomes_are_pre_generated(dev_suite):
    assert len({case.case_id for case in dev_suite}) == len(dev_suite)
    for case in dev_suite:
        if case.stratum == "model_gap":
            assert case.actual_outcomes == ()
        else:
            assert set(case.outcome_dict()) == {probe.probe_id for probe in case.probes}
