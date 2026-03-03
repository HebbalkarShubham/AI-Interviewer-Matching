import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>AI Talent Acquisition Engine</h1>
      <p style={styles.subtitle}>
        Upload a resume to extract skills and get matched with the best interviewers.
      </p>
      <div style={styles.cards}>
        <Link to="/upload" style={styles.card}>
          <span style={styles.cardIcon}>📄</span>
          <h3>Upload Resume</h3>
          <p>Upload a PDF resume. We'll extract skills using AI and create a candidate profile.</p>
        </Link>
        <Link to="/interviewers" style={styles.card}>
          <span style={styles.cardIcon}>👥</span>
          <h3>Manage Interviewers</h3>
          <p>Add or view interviewers and their skills. Matching uses this data.</p>
        </Link>
      </div>
    </div>
  )
}

const styles = {
  container: {
    textAlign: 'center',
    paddingTop: '2rem',
  },
  title: {
    fontSize: '1.75rem',
    fontWeight: 600,
    marginBottom: '0.5rem',
  },
  subtitle: {
    color: 'var(--text-muted)',
    marginBottom: '2.5rem',
  },
  cards: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
    gap: '1.5rem',
    textAlign: 'left',
  },
  card: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 12,
    padding: '1.5rem',
    color: 'inherit',
    transition: 'border-color 0.2s, transform 0.2s',
  },
  cardIcon: {
    fontSize: '2rem',
    display: 'block',
    marginBottom: '0.75rem',
  },
}
