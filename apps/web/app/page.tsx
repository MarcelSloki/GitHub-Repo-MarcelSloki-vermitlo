import type { CSSProperties } from 'react';

type DemoOverview = {
  current_goal: string;
  flow: string[];
  boundaries: string[];
};

async function getOverview(): Promise<DemoOverview | null> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

  try {
    const response = await fetch(`${baseUrl}/demo/overview`, { cache: 'no-store' });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as DemoOverview;
  } catch {
    return null;
  }
}

const fallbackOverview: DemoOverview = {
  current_goal:
    'Make the existing Vermitlo MVP core visible through one local UI and backend runtime.',
  flow: [
    'Company profile',
    'Tender import',
    'Requirement analysis',
    'Match and K.O. criteria',
    'Pricing preparation',
    'Reference selection',
    'Offer dossier',
    'Human approval',
    'Submission simulation',
    'Outcome and billing simulation',
  ],
  boundaries: [
    'Synthetic data is used for the current demo path.',
    'No real tender portal submission is executed.',
    'No real customer payment is charged.',
  ],
};

const styles: Record<string, CSSProperties> = {
  page: {
    margin: 0,
    minHeight: '100vh',
    background: '#f6f7f9',
    color: '#17202a',
    fontFamily: 'Arial, Helvetica, sans-serif',
  },
  shell: {
    maxWidth: '1120px',
    margin: '0 auto',
    padding: '32px 24px 56px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '16px',
    flexWrap: 'wrap',
    paddingBottom: '28px',
    borderBottom: '1px solid #d9dee7',
  },
  badge: {
    border: '1px solid #aeb8c8',
    borderRadius: '999px',
    padding: '8px 12px',
    fontSize: '13px',
    fontWeight: 700,
    background: '#ffffff',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 280px), 1fr))',
    gap: '24px',
    marginTop: '32px',
  },
  panel: {
    background: '#ffffff',
    border: '1px solid #d9dee7',
    borderRadius: '8px',
    padding: '28px',
  },
  muted: {
    color: '#4d5b6c',
    lineHeight: 1.65,
  },
};

export default async function Home() {
  const overview = (await getOverview()) ?? fallbackOverview;

  return (
    <main style={styles.page}>
      <div style={styles.shell}>
        <header style={styles.header}>
          <div>
            <strong style={{ fontSize: '18px' }}>Vermitlo</strong>
            <p style={{ ...styles.muted, margin: '6px 0 0' }}>
              Stage 2 product shell around the executable tender workflow core
            </p>
          </div>
          <div style={styles.badge}>Engineering foundation</div>
        </header>

        <section style={styles.grid}>
          <div style={styles.panel}>
            <p style={{ margin: '0 0 12px', fontWeight: 700, color: '#334155' }}>
              Current build goal
            </p>
            <h1 style={{ margin: 0, fontSize: '42px', lineHeight: 1.1 }}>
              One local runtime for the first believable Vermitlo product path
            </h1>
            <p style={{ ...styles.muted, fontSize: '18px', marginTop: '18px' }}>
              {overview.current_goal}
            </p>
            <p style={{ ...styles.muted, marginTop: '18px' }}>
              The architecture stays industry-neutral: company profiles, tender requirements,
              evidence, approvals, dossiers, outcomes, and billing simulations are modelled for
              organizations with recurring tender work, not only IT service providers.
            </p>
          </div>

          <aside style={styles.panel}>
            <p style={{ margin: '0 0 12px', fontWeight: 700, color: '#334155' }}>
              Runtime boundary
            </p>
            <ul style={{ margin: 0, paddingLeft: '20px', color: '#334155', lineHeight: 1.7 }}>
              {overview.boundaries.map((boundary) => (
                <li key={boundary}>{boundary}</li>
              ))}
            </ul>
          </aside>
        </section>

        <section style={{ ...styles.panel, marginTop: '24px' }}>
          <p style={{ margin: '0 0 18px', fontWeight: 700, color: '#334155' }}>
            Intended synthetic product path
          </p>
          <p style={{ ...styles.muted, margin: '0 0 18px' }}>
            The current backend exposes this sequence as an overview. Persisted workflow states,
            official-source ingestion and Golden Path proof are not active yet.
          </p>
          <ol
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '12px',
              margin: 0,
              paddingLeft: '20px',
              color: '#273445',
              lineHeight: 1.5,
            }}
          >
            {overview.flow.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </section>
      </div>
    </main>
  );
}
