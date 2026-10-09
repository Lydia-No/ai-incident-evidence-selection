# Primary AIID sampling frame — source decision (2026-10-09)

## Discovery
The AI Incident Database itself publishes weekly point-in-time backups of the full database in JSON, MongoDB archive and CSV formats: https://incidentdatabase.ai/research/snapshots/ . Its publicly visible snapshot listing currently identifies the 2026-08-03 11:05 backup (`backup-20260803110541.tar.bz2`, 106.50 MB) as the latest listed snapshot. Source owners request that researchers contact them about database use. AIID's official repository is `responsible-ai-collaborative/aiid`, and its site documents a read-only GraphQL API at `https://incidentdatabase.ai/api/graphql`.

## Decision
**Choose AIID official point-in-time snapshot as the intended sampling frame, not the DavidFarago derivative.** This resolves the 17-linked-record ceiling of the preliminary convenience pilot. The 15 existing candidates remain in a separately labeled feasibility intake, not a random sample and not a frozen 50-case dataset.

## Retrieval and verification gates
1. Obtain the official dated snapshot, inspect archive member names and safe extraction paths before unpacking. Never upload the raw 106 MB archive to multiple repos or cloud folders; do not commit the archive or personal data.
2. Record exact snapshot date, download URL, SHA-256, number of incident records, schema, licensing/terms and the extraction/query script used. If the download cannot be verified, **do not invent a hash or record count**.
3. Define eligible AIID incident records (not individual reports), document duplicates/linked reports and disjoint exclusion criteria. Log full sampling frame and a reproducible fixed-seed selection before reading later outcomes.
4. Screen pilot records with blinded decision-time cutoffs; keep negative/near-miss and uncertain cases where supported, but do not infer outcome ground truth from a retrospective summary.
5. Create a new source-derived 50-case manifest only after a reproducible source frame exists; do not relabel the 15 derivative candidates as official random selections.

## Status
Official snapshot listing and primary API documentation **identified**, but no archive downloaded, hashed, unpacked, or audited. The 50-case primary selection is **NOT STARTED**. This record does not authorize evaluation runs or claims.
