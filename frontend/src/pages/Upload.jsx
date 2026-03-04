import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadResume } from '../api'

export default function Upload() {
  const [file, setFile] = useState(null)
  const [level, setLevel] = useState('') // Interviewer level: '', L1, L2 (not stored in DB)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    if (!file) {
      setError('Please select a file')
      return
    }
    setError('')
    setLoading(true)
    try {
      const candidate = await uploadResume(file)
      navigate(`/candidate/${candidate.id}`, { state: { levelFilter: level || null } })
    } catch (err) {
      setError(err.message || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Upload Resume</h1>
      <p style={styles.subtitle}>We'll extract name, email, and skills from your resume. PDF or text.</p>
      <form onSubmit={handleSubmit} style={styles.form}>
        <label style={styles.label}>
          <span style={styles.fieldLabel}>Interviewer level</span>
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            style={styles.select}
            aria-label="Interviewer level filter for matches"
          >
            <option value="L1">L1</option>
            <option value="L2">L2</option>
            <option value="L3">L3</option>
            <option value="L4">L4</option>
          </select>
        </label>
        <label style={styles.label}>
          <span style={styles.fieldLabel}>Resume file</span>
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            style={styles.input}
          />
          <span className="file-label-upload" style={styles.fileLabel}>
            {file ? file.name : 'Choose file (PDF or .txt)'}
          </span>
        </label>
        {error && <p style={styles.error}>{error}</p>}
        <button type="submit" disabled={loading} className="btn-primary" style={styles.button}>
          {loading ? 'Uploading & extracting…' : 'Upload & Match'}
        </button>
      </form>
    </div>
  )
}

const styles = {
  container: {
    maxWidth: 440,
    margin: '0 auto',
    paddingTop: '0.5rem',
  },
  title: {
    fontSize: '1.6rem',
    fontWeight: 700,
    marginBottom: '0.5rem',
    letterSpacing: '-0.02em',
  },
  subtitle: {
    color: 'var(--text-muted)',
    marginBottom: '1.75rem',
    fontSize: '0.98rem',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.25rem',
  },
  label: {
    display: 'block',
  },
  fieldLabel: {
    display: 'block',
    fontSize: '0.9rem',
    fontWeight: 600,
    color: 'var(--text-muted)',
    marginBottom: '0.4rem',
  },
  select: {
    width: '100%',
    padding: '0.65rem 0.9rem',
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
    color: 'var(--text)',
    fontSize: '1rem',
    cursor: 'pointer',
  },
  input: {
    display: 'none',
  },
  fileLabel: {
    display: 'block',
    padding: '1.25rem 1.25rem',
    background: 'var(--surface)',
    border: '2px dashed var(--border)',
    borderRadius: 'var(--radius-lg)',
    cursor: 'pointer',
    color: 'var(--text-muted)',
    fontSize: '0.95rem',
    textAlign: 'center',
    transition: 'border-color 0.2s ease, background 0.2s ease',
  },
  error: {
    color: 'var(--danger)',
    fontSize: '0.9rem',
    margin: 0,
  },
  button: {
    padding: '0.85rem 1.5rem',
    borderRadius: 'var(--radius-md)',
    fontSize: '1rem',
  },
}
