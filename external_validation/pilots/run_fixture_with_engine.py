"""Bridge the controlled fixture to the repository's actual AP-MINIMAX engine.

Run from repository root with fixture alongside this file:
  PYTHONPATH=src python external_validation/pilots/run_fixture_with_engine.py

This is a self-audited engineering smoke test, NOT independent validation.
The fixture's public probe prediction model is deliberately available to ALL
model-based selectors; realized outcome and truth are never passed to choose_probe.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from investigator import Explanation, Probe
from experiments.strategies import AP_MINIMAX, choose_probe

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("controlled_fixture", HERE / "ap_minimax_instrumented_pilot_v01.py")
assert SPEC and SPEC.loader
fixture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixture)


def main():
    # NOTE: fixture.PROBES contains counterfactual *predictions*, which are
    # available to the engine. It is not a sealed oracle in this simple fixture.
    # The hidden realized truth remains inaccessible to choose_probe.
    explanations = tuple(
        Explanation(
            explanation_id=h,
            predictions={p: frozenset({v["outcomes"][h]}) for p, v in fixture.PROBES.items()},
        )
        for h in fixture.H
    )
    probes = tuple(
        Probe(
            probe_id=p,
            outcomes=tuple(sorted(set(v["outcomes"].values()))),
            cost=float(v["cost"]),
            tie_rank=rank,
            question=p.replace("_", " "),
            source="controlled_fixture",
        )
        for rank, (p, v) in enumerate(sorted(fixture.PROBES.items()))
    )
    # Select before revealing realized outcome or accessing the hidden truth.
    selected = choose_probe(AP_MINIMAX, explanations, {}, probes)
    assert selected is not None
    probe_id = selected.probe_id
    # Only after selection: score against the fixture's separately held key.
    scored = fixture.evaluate({"AP_MINIMAX_actual_engine": probe_id}, fixture.TRUTH)
    result = {
        "classification": "SELF_AUDITED_CONTROLLED_FIXTURE",
        "engine": "experiments.strategies.choose_probe(AP_MINIMAX)",
        "case": fixture.CASE["id"],
        "selected_probe": probe_id,
        "evaluation": scored,
        "limitations": [
            "One hand-built fixture, not external validation.",
            "The shared model predicts outcomes deterministically and perfectly.",
            "The same author provided predictions and truth; no independent adjudication.",
            "The original B4 is a cost-adjusted information-gain proxy, not full EVI.",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
