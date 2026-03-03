import { Link } from 'react-router-dom'

export default function Layout({ children }) {
  return (
    <div style={styles.wrapper}>
      <header style={styles.header}>
        <Link to="/" style={styles.logo}>AI Talent Acquisition Engine</Link>
        <nav style={styles.nav}>
          <Link to="/" style={styles.navLink}>Home</Link>
          <Link to="/upload" style={styles.navLink}>Upload Resume</Link>
          <Link to="/interviewers" style={styles.navLink}>Interviewers</Link>
        </nav>
      </header>
      <main style={styles.main}>
        {children}
      </main>
    </div>
  )
}

const styles = {
  wrapper: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '1rem 2rem',
    background: 'var(--surface)',
    borderBottom: '1px solid var(--border)',
  },
  logo: {
    fontSize: '1.25rem',
    fontWeight: 600,
    color: 'var(--text)',
  },
  nav: {
    display: 'flex',
    gap: '1.5rem',
  },
  navLink: {
    color: 'var(--text-muted)',
    fontSize: '0.95rem',
  },
  main: {
    flex: 1,
    padding: '2rem',
    maxWidth: 900,
    margin: '0 auto',
    width: '100%',
  },
}
