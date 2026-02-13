import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadResume } from '../api'

export default function Upload() {
  const [file, setFile] = useState(null)
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
      navigate(`/candidate/${candidate.id}`)
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
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            style={styles.input}
          />
          <span style={styles.fileLabel}>{file ? file.name : 'Choose file'}</span>
        </label>
        {error && <p style={styles.error}>{error}</p>}
        <button type="submit" disabled={loading} style={styles.button}>
          {loading ? 'Uploading & extracting…' : 'Upload & Match'}
        </button>
      </form>
    </div>
  )
}

const styles = {
  container: { maxWidth: 420, margin: '0 auto' },
  title: { fontSize: '1.5rem', marginBottom: '0.5rem' },
  subtitle: { color: 'var(--text-muted)', marginBottom: '1.5rem' },
  form: { display: 'flex', flexDirection: 'column', gap: '1rem' },
  label: { display: 'block' },
  input: { display: 'none' },
  fileLabel: {
    display: 'inline-block',
    padding: '0.75rem 1rem',
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 8,
    cursor: 'pointer',
    color: 'var(--text-muted)',
  },
  error: { color: 'var(--danger)', fontSize: '0.9rem' },
  button: {
    padding: '0.75rem 1.5rem',
    background: 'var(--accent)',
    color: 'white',
    border: 'none',
    borderRadius: 8,
    fontWeight: 600,
  },
}
