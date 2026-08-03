# Stage 2 runtime shell merge gate

This document is the review contract for PR #12. It does not authorize draft removal or merge.

## Scope under review

- preserve `src/vermitlo_mvp` as the canonical executable core
- add the minimal `apps/web` shell and shared Docker Compose startup
- expose read-only Stage 2 overview and health endpoints
- keep all demo data synthetic
- keep submission, outcome, billing, commission, invoice, and payment behavior simulated

## Exact-head evidence required

The pull request may leave draft only when one exact head commit has all of the following evidence:

1. `PYTHONPATH=src python -m unittest discover -s tests` passes.
2. `npm --prefix apps/web install --no-audit --no-fund` succeeds.
3. `npm --prefix apps/web run build` succeeds.
4. `docker compose config --quiet` succeeds.
5. The integrated API and web services start from the documented shared command.
6. Ports 8000 and 3000 respond successfully.
7. The API and rendered shell preserve these boundaries:
   - explicit human approval
   - no live tender portal submission
   - no real customer payment
   - synthetic demo data
8. Desktop and mobile screenshots show no overflow, overlap, or hidden boundary copy.

## Role acceptance

- DRI: QA and Audit Lead
- Review by: Engineering Lead, Product Lead, Legal/Compliance Lead
- Approval gate: CEO / maintainer
- Done when: the exact-head CI check is green, rendered evidence is inspected, reviewers accept it, and the CEO / maintainer approves draft removal

A workflow definition, partial local evidence, or an empty status list is not passing evidence.
