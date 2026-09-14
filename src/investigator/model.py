from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class InvestigationState(StrEnum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    MODEL_GAP = "MODEL_GAP"


@dataclass(frozen=True)
class Explanation:
    explanation_id: str
    predictions: Mapping[str, frozenset[str]]


@dataclass(frozen=True)
class Probe:
    probe_id: str
    outcomes: tuple[str, ...]
    cost: float
    tie_rank: int
    question: str
    source: str

    def __post_init__(self) -> None:
        if not self.outcomes:
            raise ValueError("probe outcomes cannot be empty")
        if len(set(self.outcomes)) != len(self.outcomes):
            raise ValueError("probe outcomes must be unique")
        if self.cost <= 0:
            raise ValueError("probe cost must be positive")


@dataclass(frozen=True)
class EvidenceMismatch:
    probe_id: str
    observed_outcome: str
    compatible_outcomes: tuple[str, ...] | None


@dataclass(frozen=True)
class CompatibilityRecord:
    explanation_id: str
    compatible: bool
    contradictions: tuple[EvidenceMismatch, ...]


@dataclass(frozen=True)
class ProbeScore:
    probe_id: str
    worst_case_residual: int
    cost: float
    tie_rank: int
    outcome_survivors: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class OperationalCheck:
    probe_id: str
    question: str
    source: str
    cost: float
    outcomes: tuple[str, ...]
    outcome_survivors: Mapping[str, tuple[str, ...]]
    outcome_eliminations: Mapping[str, tuple[str, ...]]
    resolving_outcomes: tuple[str, ...]


@dataclass(frozen=True)
class DecisionTrace:
    observed_evidence: tuple[tuple[str, str], ...]
    compatibility: tuple[CompatibilityRecord, ...]
    probe_scores: tuple[ProbeScore, ...]
    chosen_probe_id: str | None


@dataclass(frozen=True)
class InvestigationResult:
    state: InvestigationState
    candidate_explanations: tuple[str, ...]
    selected_cause: str | None
    next_check: OperationalCheck | None
    trace: DecisionTrace
