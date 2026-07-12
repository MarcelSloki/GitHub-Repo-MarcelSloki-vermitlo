import { runDemoFlow } from "./demoFlow.js";

const state = runDemoFlow();
const steps = [
  {
    key: "profile",
    title: "Unternehmensprofil",
    status: "geladen",
    detail: state.company.name,
    meta: `${state.company.segment} | ${state.company.location}`
  },
  {
    key: "analysis",
    title: "Ausschreibungsanalyse",
    status: `${state.dossier.analysis.score}% Fit`,
    detail: state.tender.title,
    meta: `${state.dossier.analysis.covered.length}/${state.tender.requiredCapabilities.length} Pflichtfaehigkeiten abgedeckt`
  },
  {
    key: "bid",
    title: "Bid-or-No-Bid",
    status: state.dossier.analysis.decision.toUpperCase(),
    detail: state.dossier.blockers.length === 0 ? "Keine harten Blocker erkannt" : state.dossier.blockers.join(", "),
    meta: "Regelbasiert, erklaerbar, auditierbar"
  },
  {
    key: "offer",
    title: "Angebot & Dossier",
    status: state.summary.offerPrice,
    detail: `${state.dossier.references.length} belastbare Referenzen ausgewaehlt`,
    meta: `${state.dossier.requiredDocuments.length} Dokumente vorbereitet`
  },
  {
    key: "approval",
    title: "Menschliche Freigabe",
    status: state.approvedDossier.approval.status,
    detail: state.approvedDossier.approval.note,
    meta: state.approvedDossier.approval.approver
  },
  {
    key: "submission",
    title: "Submission-Simulation",
    status: state.submission.status,
    detail: state.submission.receiptId,
    meta: state.submission.note
  },
  {
    key: "award",
    title: "Zuschlags-Simulation",
    status: `${state.award.winProbability}%`,
    detail: state.award.reason,
    meta: state.award.status
  },
  {
    key: "billing",
    title: "Test-Abrechnung",
    status: state.invoice.status,
    detail: `${formatCurrency(state.invoice.totalEur)} brutto`,
    meta: state.invoice.safetyNote
  },
  {
    key: "learning",
    title: "Outcome-Learning",
    status: state.learning.status,
    detail: state.learning.nextActions[0],
    meta: "Kundendaten getrennt, keine Wettbewerber-Nutzung"
  }
];

let activeStep = 0;

function formatCurrency(value) {
  return new Intl.NumberFormat("de-DE", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0
  }).format(value);
}

function statusClass(status) {
  if (status.includes("failed") || status.includes("blocked") || status.includes("no-bid")) return "danger";
  if (status.includes("warning") || status.includes("review")) return "warning";
  return "good";
}

function render() {
  const app = document.querySelector("#app");
  const active = steps[activeStep];

  app.innerHTML = `
    <aside class="sidebar" aria-label="Demo-Flow">
      <div class="brand">
        <span>Vermitlo</span>
        <strong>MVP Demo</strong>
      </div>
      <nav class="step-nav">
        ${steps
          .map(
            (step, index) => `
              <button class="${index === activeStep ? "active" : ""}" data-step="${index}">
                <span>${String(index + 1).padStart(2, "0")}</span>
                ${step.title}
              </button>
            `
          )
          .join("")}
      </nav>
    </aside>

    <main class="workspace">
      <section class="topline">
        <div>
          <p class="eyebrow">End-to-End Demo-Flow</p>
          <h1>${active.title}</h1>
        </div>
        <div class="decision ${statusClass(active.status.toLowerCase())}">
          <span>Status</span>
          <strong>${active.status}</strong>
        </div>
      </section>

      <section class="stage">
        <div class="stage-copy">
          <p>${active.detail}</p>
          <small>${active.meta}</small>
        </div>
        <div class="flow-line" aria-hidden="true">
          ${steps
            .map(
              (_, index) => `
                <span class="${index < activeStep ? "done" : index === activeStep ? "current" : ""}"></span>
              `
            )
            .join("")}
        </div>
      </section>

      <section class="grid">
        ${renderActivePanel(active.key)}
      </section>

      <section class="actions">
        <button class="icon-button" data-prev title="Vorheriger Schritt" ${activeStep === 0 ? "disabled" : ""}>&lt;</button>
        <button class="primary" data-next ${activeStep === steps.length - 1 ? "disabled" : ""}>Naechster Schritt</button>
      </section>
    </main>
  `;

  document.querySelectorAll("[data-step]").forEach((button) => {
    button.addEventListener("click", () => {
      activeStep = Number(button.dataset.step);
      render();
    });
  });

  document.querySelector("[data-prev]")?.addEventListener("click", () => {
    activeStep = Math.max(0, activeStep - 1);
    render();
  });

  document.querySelector("[data-next]")?.addEventListener("click", () => {
    activeStep = Math.min(steps.length - 1, activeStep + 1);
    render();
  });
}

function renderActivePanel(key) {
  const panels = {
    profile: `
      ${metric("Zertifikate", state.company.certifications.join(", "))}
      ${metric("Max. Projektwert", formatCurrency(state.company.constraints.maxProjectValueEur))}
      ${list("Faehigkeiten", state.company.capabilities)}
    `,
    analysis: `
      ${list("Pflichtfaehigkeiten abgedeckt", state.dossier.analysis.covered)}
      ${list("Nice-to-have abgedeckt", state.dossier.analysis.niceToHaveCovered)}
      ${koPanel()}
    `,
    bid: `
      ${metric("Entscheidung", state.dossier.analysis.decision)}
      ${metric("Confidence", state.dossier.analysis.confidence)}
      ${list("Blocker", state.dossier.blockers.length ? state.dossier.blockers : ["Keine harten Blocker"])}
    `,
    offer: `
      ${metric("Angebotspreis", formatCurrency(state.dossier.pricing.offerPrice))}
      ${metric("Bruttomarge", `${state.dossier.pricing.grossMarginPercent}%`)}
      ${referencesPanel()}
    `,
    approval: `
      ${metric("Freigabe", state.approvedDossier.approval.status)}
      ${metric("Freigeber", state.approvedDossier.approval.approver)}
      ${list("Audit-Trail", state.approvedDossier.auditTrail)}
    `,
    submission: `
      ${metric("Portal", state.submission.portal)}
      ${metric("Quittung", state.submission.receiptId)}
      ${metric("Schutzlinie", "Nur Simulation, keine echte Abgabe")}
    `,
    award: `
      ${metric("Simulierter Ausgang", state.award.status)}
      ${metric("Zuschlagswert", formatCurrency(state.award.awardValueEur))}
      ${metric("Grund", state.award.reason)}
    `,
    billing: `
      ${metric("Rechnung", state.invoice.invoiceNo || "Keine Rechnung")}
      ${metric("Netto", formatCurrency(state.invoice.netAmountEur))}
      ${metric("Payment", state.invoice.payment.status)}
    `,
    learning: `
      ${learningPanel()}
      ${list("Naechste Schritte", state.learning.nextActions)}
    `
  };

  return panels[key];
}

function metric(label, value) {
  return `
    <article class="panel">
      <span>${label}</span>
      <strong>${value}</strong>
    </article>
  `;
}

function list(label, items) {
  return `
    <article class="panel wide">
      <span>${label}</span>
      <ul>
        ${items.map((item) => `<li>${item}</li>`).join("")}
      </ul>
    </article>
  `;
}

function koPanel() {
  return `
    <article class="panel wide">
      <span>K.O.-Kriterien</span>
      <ul>
        ${state.dossier.analysis.koResults
          .map((item) => `<li><b class="${statusClass(item.status)}">${item.status}</b> ${item.label}</li>`)
          .join("")}
      </ul>
    </article>
  `;
}

function referencesPanel() {
  return `
    <article class="panel wide">
      <span>Ausgewaehlte Referenzen</span>
      <ul>
        ${state.dossier.references
          .map((reference) => `<li>${reference.title} <small>${reference.evidence}</small></li>`)
          .join("")}
      </ul>
    </article>
  `;
}

function learningPanel() {
  return `
    <article class="panel wide">
      <span>Lernsignale</span>
      <ul>
        ${state.learning.signals
          .map((signal) => `<li>${signal.label}: ${signal.value} <small>${signal.learning}</small></li>`)
          .join("")}
      </ul>
    </article>
  `;
}

render();
