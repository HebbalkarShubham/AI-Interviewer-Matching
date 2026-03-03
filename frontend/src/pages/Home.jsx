import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>
        <span style={styles.titleAccent}>AI</span> Talent Acquisition Engine
      </h1>
      <p style={styles.subtitle}>
        Upload a resume to extract skills and get matched with the best interviewers.
      </p>
      <div style={styles.cards}>
        <Link to="/upload" className="card-hover" style={styles.card}>
          <span style={styles.cardIconWrap}>
            <span style={styles.cardIcon}>📄</span>
          </span>
          <h3 style={styles.cardTitle}>Upload Resume</h3>
          <p style={styles.cardDesc}>Upload a PDF resume. We'll extract skills using AI and create a candidate profile.</p>
        </Link>
        <Link to="/interviewers" className="card-hover" style={styles.card}>
          <span style={styles.cardIconWrap}>
            <span style={styles.cardIcon}>👥</span>
          </span>
          <h3 style={styles.cardTitle}>Manage Interviewers</h3>
          <p style={styles.cardDesc}>Add or view interviewers and their skills. Matching uses this data.</p>
        </Link>
      </div>
    </div>
  )
}

const styles = {
  container: {
    textAlign: 'center',
    paddingTop: '2.5rem',
    paddingBottom: '3rem',
  },
  title: {
    fontSize: '2rem',
    fontWeight: 700,
    marginBottom: '0.75rem',
    letterSpacing: '-0.03em',
    color: 'var(--text)',
  },
  titleAccent: {
    color: 'var(--accent)',
    fontWeight: 800,
  },
  subtitle: {
    color: 'var(--text-muted)',
    marginBottom: '3rem',
    fontSize: '1.05rem',
    maxWidth: 420,
    marginLeft: 'auto',
    marginRight: 'auto',
  },
  cards: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '1.5rem',
    textAlign: 'left',
  },
  card: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    padding: '1.75rem',
    color: 'inherit',
    textDecoration: 'none',
    display: 'block',
  },
  cardIconWrap: {
    width: 48,
    height: 48,
    borderRadius: 'var(--radius-md)',
    background: 'var(--accent-glow)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '1rem',
  },
  cardIcon: {
    fontSize: '1.5rem',
  },
  cardTitle: {
    margin: '0 0 0.5rem',
    fontSize: '1.15rem',
    fontWeight: 600,
    color: 'var(--text)',
  },
  cardDesc: {
    margin: 0,
    fontSize: '0.95rem',
    color: 'var(--text-muted)',
    lineHeight: 1.55,
  },
}
