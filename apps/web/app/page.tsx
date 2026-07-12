const workflowSteps = [
  "Company profile",
  "Tender intake",
  "Requirement and K.O. check",
  "Transparent match score",
  "Pricing preparation",
  "Reference selection",
  "Offer dossier",
  "Human approval",
  "Submission simulation",
  "Award, billing, and learning simulation",
];

export default function Home() {
  return (
    <main
      style={{
        minHeight: "100vh",
        margin: 0,
        padding: "48px 32px",
        fontFamily:
          'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        color: "#172033",
        background: "#f7f8fb",
      }}
    >
      <section style={{ maxWidth: 960, margin: "0 auto" }}>
        <p style={{ margin: "0 0 12px", fontSize: 14, fontWeight: 700, color: "#496179" }}>
          Vermitlo MVP shell
        </p>
        <h1 style={{ margin: "0 0 16px", fontSize: 44, lineHeight: 1.08 }}>
          Tender workflow control for German mid-market IT service providers
        </h1>
        <p style={{ maxWidth: 720, margin: "0 0 32px", fontSize: 18, lineHeight: 1.6 }}>
          This first interface layer wraps the executable Python MVP core. It makes the
          current product path visible without claiming live portal submission, real
          payment execution, or production tender-source integrations.
        </p>

        <ol
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 12,
            margin: 0,
            padding: 0,
            listStyle: "none",
          }}
        >
          {workflowSteps.map((step, index) => (
            <li
              key={step}
              style={{
                minHeight: 96,
                border: "1px solid #d9e0e8",
                borderRadius: 8,
                padding: 16,
                background: "#ffffff",
              }}
            >
              <span style={{ display: "block", marginBottom: 8, color: "#6b7f93" }}>
                {String(index + 1).padStart(2, "0")}
              </span>
              <strong>{step}</strong>
            </li>
          ))}
        </ol>

        <p style={{ margin: "32px 0 0", fontSize: 14, lineHeight: 1.6, color: "#526276" }}>
          Current boundary: approval, submission, outcome, billing, and payment remain
          synthetic demo flows until explicit production access and legal/operational
          clearance exist.
        </p>
      </section>
    </main>
  );
}
