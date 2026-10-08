# AIID external validation v0.2 — draft sampling protocol

Status: DRAFT; not preregistered or frozen. No actual incidents selected.

## Source
AI Incident Database (AIID), snapshot dated 2026-10-05, `backup-20261005101424.tar.bz2`.
Source: https://incidentdatabase.ai/research/snapshots/
Snapshot SHA-256: PENDING DOWNLOAD.

## Sampling
1. Inventory incident IDs, report IDs, dates, duplicates, and source provenance from the exact snapshot.
2. Independently screen incidents for concrete AI involvement and a reconstructable early investigation timepoint. Do not require known causal truth or later resolution. Log all exclusions.
3. Define unresolved and complex strata **without model outputs**, using a prespecified coding rubric and blinded independent reviewers. Resolve disagreements before sampling.
4. Draw 40 from all eligible IDs, then 5 additional unresolved and 5 additional complex IDs, excluding previously drawn IDs. Keep groups disjoint. If strata are insufficient, revise protocol openly before sampling.
5. Rank IDs using SHA-256 of `AIID-v0.2-20261009|<stratum>|<incident_id>`; take the lowest hashes. Save complete eligible and excluded frames, selected IDs, and deterministic verification script.
6. Freeze selection before running AP-MINIMAX; never replace poor-performing cases.

## Evaluation
- Primary 40 estimate performance in eligible population. Report oversampled 10 separately; do not pool as an unbiased population estimate.
- Preserve time ordering: investigator sees only information published at the chosen early timepoint. Later sources remain sealed.
- Measure representation adequacy and evidence-selection quality separately.
- Compare with neutral and cost-aware information-gain strategies.
- Counterfactual probe outcomes that were never observed are UNKNOWN, not inferred as fact.
- Record missingness, evaluability and source uncertainty. No automatic attribution of truth.
- Keep the original frozen v0.1 study unchanged.

## Data governance
- Do not commit the 113 MB AIID archive, raw third-party reports, personal data, or unreviewed source text to Git.
- Store raw snapshot in restricted archival storage (e.g. Dropbox), with SHA-256 and exact retrieval URL in a Git-tracked manifest.
- Git tracks protocols, scripts, metadata, source links, permissible derived tables, and selected ID manifest after verification.
- Check AIID and original report licenses/terms before redistribution.

## Current status
Official snapshot URL verified. Runtime download attempted but unsuccessful. Screening and 50-ID draw NOT performed.
