import { Link } from 'react-router-dom'
import logo from '../assets/images/Ix-logo.svg'

export default function Layout({ children }) {
  return (
    <div style={styles.wrapper}>
      <header style={styles.header}>
        <Link to="/" style={styles.logo} aria-label="AI Talent Acquisition Engine - Home">
          <img src={logo} alt="AI Talent Acquisition Engine" style={styles.logoImg} />
        </Link>
        <nav style={styles.nav}>
          <Link to="/" className="nav-link-app">Home</Link>
          <Link to="/upload" className="nav-link-app">Upload Resume</Link>
          <Link to="/interviewers" className="nav-link-app">Interviewers</Link>
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
    boxShadow: '0 1px 0 rgba(255,255,255,0.03)',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
  },
  logoImg: {
    height: 32,
    width: 'auto',
    display: 'block',
  },
  nav: {
    display: 'flex',
    gap: '0.25rem',
  },
  main: {
    flex: 1,
    width: '100%',
    maxWidth: 1400,
    margin: '0 auto',
    padding: '1.25rem 1.5rem',
    boxSizing: 'border-box',
  },
}
