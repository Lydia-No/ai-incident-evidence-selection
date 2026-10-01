from analysis.recompute import (
    h1_premature_closure,
    paired_bootstrap_interval,
    paired_first_check,
    paired_summary,
    realized_value,
    trajectory_summary,
    true_explanation_retention,
)


def action(case_id, seed, strategy, before, after, cost):
    return {
        "case_id": case_id,
        "seed": seed,
        "strategy": strategy,
        "stratum": "confusable_resolvable",
        "step": 0,
        "selected_probe_id": "p0",
        "selected_probe_cost": cost,
        "candidate_count_before": before,
        "candidate_count_after": after,
    }


def terminal(
    case_id,
    strategy,
    stratum,
    state,
    *,
    truth="h0",
    selected="h0",
    before=1,
    observations=0,
    cost=0.0,
):
    return {
        "case_id": case_id,
        "seed": 1,
        "strategy": strategy,
        "stratum": stratum,
        "step": observations,
        "selected_probe_id": None,
        "selected_probe_cost": None,
        "candidate_ids_before": [truth] if before == 1 else [truth, "h1", "h2"][:before],
        "candidate_count_before": before,
        "candidate_ids_after": [truth] if state == "RESOLVED" else [],
        "candidate_count_after": 1 if state == "RESOLVED" else 0,
        "hidden_truth_id": truth,
        "selected_cause": selected,
        "state_after": state,
        "terminal_action": "terminal",
        "cumulative_observations": observations,
        "cumulative_cost": cost,
    }


def test_realized_value_is_recomputed_only_from_trace_counts_and_cost():
    record = action("c1", 1, "a", 4, 2, 2.0)
    assert realized_value(record) == 1.0


def test_paired_first_check_matches_by_case_not_row_order():
    records = [
        action("c2", 2, "a", 4, 2, 1.0),
        action("c1", 1, "b", 4, 3, 1.0),
        action("c1", 1, "a", 4, 1, 1.0),
        action("c2", 2, "b", 4, 3, 1.0),
    ]
    rows = paired_first_check(records, "a", "b")
    assert [row["case_id"] for row in rows] == ["c1", "c2"]
    assert [row["difference"] for row in rows] == [2.0, 1.0]


def test_bootstrap_interval_is_deterministic_for_frozen_seed():
    differences = [1.0, 0.5, 0.0, -0.25, 0.75]
    first = paired_bootstrap_interval(differences, seed=26091399, replicates=1000)
    second = paired_bootstrap_interval(differences, seed=26091399, replicates=1000)
    assert first == second
    assert first[0] <= first[1]


def test_paired_summary_reports_seed_direction_and_win_tie_loss():
    rows = [
        {"case_id": "a", "seed": 1, "difference": 1.0},
        {"case_id": "b", "seed": 1, "difference": 0.0},
        {"case_id": "c", "seed": 2, "difference": -0.5},
        {"case_id": "d", "seed": 2, "difference": 1.0},
    ]
    summary = paired_summary(rows)
    assert summary["wins"] == 2
    assert summary["ties"] == 1
    assert summary["losses"] == 1
    assert summary["positive_seed_count"] == 2
    assert set(summary["seed_mean_differences"]) == {"1", "2"}


def test_h1_recompute_distinguishes_supported_resolution_from_forced_closure():
    supported = {
        "case_id": "supported",
        "seed": 1,
        "strategy": "ap_minimax",
        "stratum": "confusable_resolvable",
        "step": 0,
        "selected_cause": "h0",
        "candidate_count_before": 3,
        "state_after": "RESOLVED",
    }
    forced = {
        "case_id": "forced",
        "seed": 1,
        "strategy": "forced_closure",
        "stratum": "confusable_resolvable",
        "step": 0,
        "selected_cause": "h0",
        "candidate_count_before": 3,
        "state_after": "FORCED_CLOSED",
    }
    result = h1_premature_closure([supported, forced])
    assert result["ap_minimax"]["premature_closure_rate"] == 0.0
    assert result["forced_closure"]["premature_closure_rate"] == 1.0
    assert result["forced_closure"]["unsupported_attributions"] == 1


def test_trajectory_recompute_scores_frozen_control_states_from_terminal_trace():
    records = [
        terminal("gap", "ap_minimax", "model_gap", "MODEL_GAP", truth="external_truth", selected=None, before=0),
        terminal("persistent", "ap_minimax", "persistent_ambiguity", "UNRESOLVED", selected=None, before=2),
        terminal("clean", "ap_minimax", "clean_resolvable", "RESOLVED", observations=0, cost=0.0),
        terminal("no-failure", "ap_minimax", "no_failure", "RESOLVED", truth="h3", selected="h3", observations=2, cost=2.0),
    ]
    summary = trajectory_summary(records)["ap_minimax"]
    assert summary["model_gap_rate_on_model_gap_controls"] == 1.0
    assert summary["unresolved_rate_on_persistent_controls"] == 1.0
    assert summary["valid_resolution_rate_on_clean_controls"] == 1.0
    assert summary["valid_resolution_rate_on_no_failure_controls"] == 1.0


def test_true_explanation_retention_uses_pre_resolution_candidate_sets():
    records = [
        {
            "case_id": "kept",
            "strategy": "ap_minimax",
            "hidden_truth_id": "h0",
            "candidate_count_before": 3,
            "candidate_ids_before": ["h0", "h1", "h2"],
        },
        {
            "case_id": "lost",
            "strategy": "ap_minimax",
            "hidden_truth_id": "h0",
            "candidate_count_before": 2,
            "candidate_ids_before": ["h1", "h2"],
        },
        {
            "case_id": "gap",
            "strategy": "ap_minimax",
            "hidden_truth_id": "external_truth",
            "candidate_count_before": 2,
            "candidate_ids_before": ["h1", "h2"],
        },
    ]
    result = true_explanation_retention(records)["ap_minimax"]
    assert result["eligible_steps"] == 2
    assert result["retained_steps"] == 1
    assert result["retention_rate"] == 0.5
