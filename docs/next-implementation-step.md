# Next Implementation Step

Status: 2026-07-12

## Konsolidierte Empfehlung

The most effective next implementation step is to extend the current executable baseline into a two-tender vertical slice with explicit audit events.

## Why This Step

The repository already proves the happy path. The next useful increment should prove decision safety:

- one tender that can move to simulated submission after approval;
- one tender that is blocked by hard K.O. criteria;
- one audit trail that explains why each status changed.

This creates a credible MVP demo without touching legally risky live portals or payments.

## Proposed File-Level Work

1. Add `AuditEvent` and `audit_log` support in `src/vermitlo_mvp/models.py` and workflow output.
2. Change seed loading from one tender to multiple tenders.
3. Add a second seed tender with missing mandatory certification or over-capacity value.
4. Update `run_demo` to return a list of tender runs or a portfolio summary.
5. Add tests for:
   - approved bid flow;
   - K.O.-blocked no-bid flow;
   - no synthetic references;
   - zero commission when not awarded;
   - audit events exist for match, approval, submission, outcome, and billing.
6. Keep the HTTP API compatible by returning the same object for single-demo mode or a new `/demo/run-portfolio` route.

## Definition of Done

- `PYTHONPATH=src python -m unittest discover -s tests` passes.
- Demo output includes both a positive and blocked tender path.
- Every generated bid decision has assumptions, source attribution, and missing-information fields.
- Submission and billing remain mocks.
- README documents both CLI and HTTP usage.

## Risks to Defer Safely

- Real Bekanntmachungsservice adapter: design the interface first, implement after the domain flow is stable.
- PDF/DOCX generation: add after dossier structure is stable.
- Stripe sandbox: add after commission event state is stable.
- E-invoice output: add after invoice data model and tax review are clear.
