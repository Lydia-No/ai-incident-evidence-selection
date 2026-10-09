# Official AIID Excel 50-case screening draw — 2026-10-09

Source uploaded by researcher: `AIID_Excel_Export-20261005.xlsx` (AIID 2026-10-05 export). SHA-256: `95c71e26ef379432a9a87934d26854c1a68998ef158a3fc4b247d96afb20c749`.

The workbook contains 1,711 unique incident IDs and 7,840 reports. The 2020–2026 screening frame comprises **822** incidents satisfying: 2020 <= `year` <= 2026; `report_count >= 2`; nonempty `title` and `description`. Counts by year: 2020=56, 2021=49, 2022=81, 2023=98, 2024=164, 2025=246, 2026=128.

A reproducible exploratory **year-stratified** draw uses Python `random.Random(20261009)`, sorted incident IDs within each year, with quotas 7/year for 2020–2025 and 8 for 2026 (50 total). The 50 selected IDs in order are:

`102,115,125,172,220,356,772,145,160,197,343,425,534,569,372,389,413,427,455,630,1689,466,573,591,608,609,619,799,746,755,794,872,883,972,1291,1106,1188,1244,1284,1356,1442,1500,1415,1508,1544,1629,1645,1665,1693,1707`.

**Important limitations:** This is a **screening sample**, not 50 validated AP-MINIMAX evaluations. The workbook does not establish available contemporaneous decision traces, hypothesis sets, probe costs or counterfactual outcomes. Equal-year quotas deliberately oversample earlier years relative to their incidence counts and cannot estimate incident prevalence without weighting. Two-report threshold selects better-documented incidents and creates coverage bias. The full local manifest and provenance files were generated for review; the repository does not yet contain the complete manifest. No external scoring was performed; frozen synthetic experiments were untouched.

Next: source verification, case-level inclusion/exclusion audit and decision-time leakage checks **before** any external performance comparison.