const workflowSteps = [
  "Company profile intake",
  "Tender import",
  "Requirement and K.O. criteria analysis",
  "Explainable match scoring",
  "Proposal dossier preparation",
  "Human approval before submission",
  "Submission and outcome simulation",
  "Commission, invoice, and payment simulation"
];

const currentBoundaries = [
  "The Python core in src/vermitlo_mvp remains the executable workflow source of truth.",
  "Real portal submission, production billing, and payment execution are not included in this slice.",
  "The first buyer frame is tender-active companies in Germany, not only IT or software service providers."
];

export default function Home() {
  return (
    <main className="shell">
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Vermitlo MVP shell</p>
        <h1 id="page-title">Tender workflow control for tender-active companies</h1>
        <p className="intro">
          This first interface layer wraps the executable Python MVP core. It makes the
          current product path visible for small, medium-sized, and larger companies with
          recurring public-tender work, without claiming live portal submission, real payment
          execution, or production tender-source integrations.
        </p>
      </section>

      <section aria-labelledby="workflow-title">
        <h2 id="workflow-title">Current visible workflow</h2>
        <ol className="workflow-grid">
          {workflowSteps.map((step, index) => (
            <li key={step} className="workflow-step">
              <span>{String(index + 1).padStart(2, "0")}</span>
              <strong>{step}</strong>
            </li>
          ))}
        </ol>
      </section>

      <section className="boundaries" aria-labelledby="boundaries-title">
        <h2 id="boundaries-title">Current scope boundaries</h2>
        <ul>
          {currentBoundaries.map((boundary) => (
            <li key={boundary}>{boundary}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}
