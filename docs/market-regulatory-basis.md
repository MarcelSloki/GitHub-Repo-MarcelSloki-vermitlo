# Market, Source, and Regulatory Basis

Status: 2026-07-12
Scope: Vermitlo MVP for German mid-market IT and software service providers.

## Belegte Fakten

- Public procurement is economically material in Germany. The Federal Ministry for Economic Affairs describes public-sector procurement as an annual market in the hundreds of billions of euros.
- German procurement rules distinguish contracts above and below EU thresholds. Since 2026-01-01, the BMWE lists EU thresholds including 140,000 EUR for supplies/services of supreme and higher federal authorities, 216,000 EUR for other supplies/services, 432,000 EUR for utilities/transport/defence-related supply and service contracts, and 5,404,000 EUR for works and concessions.
- The Bekanntmachungsservice of the Datenservice Oeffentlicher Einkauf is available without registration and exposes an open-data interface for notice data. The Beschaffungsamt states that bundled notice data can be retrieved as eForms, OCDS, and CSV.
- TED is the official EU tender portal for notices in the Supplement to the Official Journal of the EU.
- eForms became mandatory for EU public procurement notices in October 2023 and replaced the previous standard forms.
- German B2B e-invoicing rules apply from 2025-01-01 with transition rules. The BMF notes that its FAQ covers tax questions of fundamental importance, not technical implementation, B2G details, or individual legal/tax cases.
- Payment services can be permission-sensitive under the German ZAG/BaFin regime. Live payment collection, escrow, or money transmission must be avoided unless covered by a licensed provider and reviewed.
- The EU AI Act is risk-based. Even if the first Vermitlo MVP is rule-based, later AI assistance should keep explainability, human oversight, and evidence retention as design constraints.

## Quellenprioritaet fuer den MVP

1. Bekanntmachungsservice / Datenservice Oeffentlicher Einkauf open data.
2. TED / EU eForms for above-threshold EU notices.
3. Customer-provided tender documents only when the customer has the right to process them in Vermitlo.
4. Mock or seed data for submission, billing, and payment until production authority and provider terms are clear.

## Annahmen

- First beachhead market: German mid-market IT and software providers.
- Initial tender coverage should focus on software development, cloud migration, IT security, data engineering, and service desk services.
- Vermitlo should start as an assistant and control surface, not as an autonomous bidder.
- Success-fee billing can be simulated in the MVP, but production billing needs contract, tax, and payment-flow review.

## Offene Risiken

- Portal terms may prohibit or limit automated scraping, downloading, or submission.
- Tender documents can contain personal data or protected content. Data minimization and tenant isolation are required.
- Generated dossier text can create false claims unless every claim is source-backed.
- German and EU procurement rules can change; threshold and compliance data needs versioning.
- E-invoice production output needs EN 16931-compatible implementation and review.

## Product Guardrails

- No legally binding offer without explicit human approval.
- No invented references, certificates, revenues, staff profiles, prices, or project experience.
- Hard exclusion criteria must be shown before aggregate scoring.
- Submission is simulated until authority, signatures, authentication, portal rules, and terms are validated.
- Payment remains test-only until the billing basis and payment provider setup are verified.

## Source Links

- BMWE public procurement overview: https://www.bundeswirtschaftsministerium.de/Redaktion/DE/Dossier/oeffentliche-auftraege-und-vergabe.html
- Beschaffungsamt Datenservice Oeffentlicher Einkauf: https://www.bescha.bund.de/DE/ElektronischerEinkauf/Datenservice_Oeffentlicher_Einkauf/Datenservice-Oeffentlicher-Einkauf_node.html
- TED eForms: https://ted.europa.eu/en/simap/eforms
- BMF e-invoice FAQ: https://www.bundesfinanzministerium.de/Content/DE/FAQ/e-rechnung.html
- BaFin payment services orientation: https://www.bafin.de/DE/unternehmen-maerkte/erlaubnis-registrierung/zahlungsdienste-zahlungsinstitute/zahlungsdienste-zahlungsinstitute_node.html
- EU AI Act overview: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
