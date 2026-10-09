# Pilot source audit — 2026-10-09 (partial, evidence-bound)

## Audit scope
15 AIID-linked candidate records were imported from the third-party compilation `DavidFarago/ai_security_incidents_2026`, file `incidents/all_2026_ai_software_security_incidents.csv`. This compilation is **not** the AI Incident Database's primary export. Its incident descriptions, confidence labels, and dates are third-party assertions until checked against original sources. Selection was first 15 records sorted by the derivative's own ID; this is reproducible but **not** a representative or randomized AIID sample. The snapshot is not pinned to a source commit yet.

## Primary-source spot-check: PILOT-01 / DB-2026-003 / AIID 1412
- Original incident-research report: https://codewall.ai/blog/how-we-hacked-mckinseys-ai-platform (published 2026-03-09; accessed 2026-10-09).
- The report attributes to the research agent an initial target choice, API discovery, unauthenticated endpoints, reflected SQL errors, iterative probing, database access and responsible disclosure. It includes a dated disclosure timeline.
- **Source-bounded fact:** the article describes a sequence of observations and investigator actions, including fifteen blind iterations.
- **Limit:** the report is retrospective and authored by the research team. It does **not** provide a complete time-stamped decision log with the full contemporaneous hypothesis set, available probes, costs, or counterfactual outcomes. Do not infer those fields.
- **Classification:** promising for **qualitative sequential mapping**, **NOT** eligible for quantitative ground-truth selector performance without additional records.
- **Potential leakage:** a retrospective mapping that uses the final SQL injection diagnosis to choose earlier hypotheses or candidate checks would leak outcome information. Require decision-time evidence cutoff.

## Remaining 14 candidates
**PENDING ORIGINAL-SOURCE VERIFICATION.** Their presence in the derivative dataset does not establish independent corroboration or AP-MINIMAX eligibility. Check original incident reports and AIID primary records individually before mapping.

## Design corrections / open gates
1. Verify the precise source dataset discussed earlier; a third-party compilation with 17 AIID-linked records cannot yield 50 distinct AIID-linked cases by itself.
2. Pin an upstream source commit or export hash, record license and source timestamps.
3. Confirm sampling frame and stratification before extending beyond these preliminary 15. Do not call the first 15 a random pilot.
4. Differentiate source-bounded narrative review from controlled, ground-truth quantitative validation.
5. For each candidate, log decision-time observation cutoff, alternate hypotheses, feasible probes, unavailable evidence and mapping confidence.
6. Preserve all failed/unsuitable candidates with explicit reasons; never backfill silently.

## Decision
**GO:** source verification and feasibility screening.
**NO-GO:** claims of 15 verified usable cases, quantitative external performance, 50-case completeness, or a frozen representative sample.

No core code or synthetic holdout was changed. No external evaluation was run.
