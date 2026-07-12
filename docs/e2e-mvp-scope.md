# End-to-End MVP Scope

Status: 2026-07-12
Goal: make the full Vermitlo core workflow visible with safe mock boundaries.

## Current Executable Baseline

The repository already contains a runnable local flow:

- `PYTHONPATH=src python -m vermitlo_mvp.demo`
- `PYTHONPATH=src python -m vermitlo_mvp.server`
- `PYTHONPATH=src python -m unittest discover -s tests`

The current code covers company profile loading, tender loading, rule-based match analysis, dossier creation, approval gate, submission simulation, outcome simulation, commission calculation, test invoice/payment status, and a learning event.

## MVP Flow V1

1. Company profile
   - capabilities
   - certifications
   - maximum contract value
   - real reference projects with evidence

2. Tender import
   - demo seed now
   - public source adapter next
   - raw source attribution retained

3. Requirement analysis
   - mandatory vs optional requirements
   - certification requirements
   - value/capacity requirements
   - keyword capability checks

4. K.O. and match
   - hard K.O. reasons first
   - aggregate score second
   - decision: bid, review, no_bid

5. Pricing preparation
   - non-binding synthetic pricing now
   - source-backed commercial calculator later

6. Reference selection
   - only from available company references
   - no synthetic references

7. Offer dossier
   - decision support
   - selected references
   - pricing assumptions
   - missing information
   - source attribution

8. Human approval
   - explicit approval required
   - no submission if approval is missing
   - no submission if decision is no_bid

9. Submission simulation
   - mock portal status now
   - manual checklist before any real portal integration

10. Outcome tracking
   - simulated award/loss now
   - manual outcome recording later

11. Commission and billing
   - success-fee calculation now
   - test invoice/payment status only
   - no live charging

12. Learning
   - tenant-scoped learning event
   - no cross-customer use of confidential bid data

## Next Acceptance Criteria

The next implementation PR should satisfy:

- Demo contains at least two tenders: one `bid`, one `no_bid` due to K.O. reasons.
- Match output keeps K.O. reasons visible even when numeric score is high.
- Dossier output lists missing information and source attribution.
- Approval gate blocks unapproved submissions.
- Commission is zero unless a simulated awarded outcome exists.
- Tests cover both approved and blocked flows.
- No external portal or payment side effects occur.

## Out of Scope for V1

- Live tender portal submission.
- Captcha, login, signature, or portal-rule automation.
- Production payment collection.
- Legal/tax advice.
- Generated unverifiable claims.
- Cross-tenant learning from confidential data.
