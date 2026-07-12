# MVP Assumptions and Safety Boundaries

## Confirmed setup

- Target repository: `MarcelSloki/GitHub-Repo-MarcelSloki-vermitlo`
- Default branch: `main`
- Initial repository state: empty at the start of this increment

## Product assumptions

- The first beachhead market is German mid-market IT and software service providers.
- Public tender imports are represented by source-attributed JSON until a real public-source adapter is selected.
- Matching is rule-based and explainable in the MVP.
- Offer dossiers are preparation artifacts, not legally binding offers.
- Submission, award, invoice, and payment are simulations until real permissions, contracts, and sandbox credentials exist.

## Safety boundaries

- No automatic legally binding submission.
- No invented references, certifications, prices, revenue, employees, or delivery experience.
- Missing evidence is explicitly surfaced.
- Customer data must stay tenant-separated in later persistence layers.
- Payment collection requires a verified billing event and test or production payment integration.

## Next integration candidates

1. Add a persistent store for company profiles, tenders, decisions, dossiers, approvals, and audit events.
2. Add a documented public tender source adapter behind the current seed import interface.
3. Add a minimal web UI for bid/no-bid review and human approval.
4. Replace payment simulation with a sandbox payment provider only after billing terms are validated.

## Implemented in current persistence increment

- SQLite-backed workflow run storage for synthetic MVP runs.
- Audit events for tender import, scoring, dossier preparation, approval, submission simulation, billing simulation, and learning.
- Server endpoint to list stored runs.
- CLI flag `--persist` to store a local demo run.
