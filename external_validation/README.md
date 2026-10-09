# External validation — 50-case intake

Status: PREPARATION ONLY. No 50-case sample has been selected, collected, mapped, or evaluated. This branch does not change the frozen synthetic holdout or investigator implementation.

## Purpose
Build a traceable, independently sourced intake of up to 50 real-world AI incident records for source-bounded evaluation of evidence-selection recommendations. A real incident report is not automatically a ground-truth sequential decision case.

## Workflow
1. Freeze eligibility and selection protocol before selecting records.
2. Record each candidate in `cases/case_manifest.csv` using source IDs and stable source URLs; preserve selection exclusions.
3. Store only appropriately licensed/public source excerpts or references in `cases/source_records/`; do not upload personal data, credentials, or copyrighted full-text without rights.
4. Map competing explanations, observations, and candidate probes in `mappings/` with provenance; distinguish reported facts from analyst hypotheses.
5. Build a read-only adapter in `adapter/` that validates mappings against existing investigator interfaces. Do not edit `src/` or frozen `experiments/`.
6. Predefine eligible baselines, outcomes, uncertainty and qualitative vs quantitative analysis before execution. Place results in `results/` only after GO approval.

## Research boundaries
- Existing 400-case synthetic holdout remains unchanged.
- The 50 cases are a prospective *target*, not 50 verified usable cases.
- Incident narratives usually lack counterfactual outcomes and fully known ground truth; do not present source-bounded case mappings as confirmatory performance validation.
- Explicitly record insufficient evidence, overlapping explanations, missing probe outcomes, and undetectable omitted causes.
- No execution or outcome claims are authorized by this scaffold.
