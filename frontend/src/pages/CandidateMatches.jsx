import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getCandidate, getMatches, selectInterviewer } from '../api'

export default function CandidateMatches() {
  const { id } = useParams()
  const [candidate, setCandidate] = useState(null)
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selecting, setSelecting] = useState(null)
  const [message, setMessage] = useState('')
  const [search, setSearch] = useState('')

  const filteredMatches = matches.filter((m) => {
    if (!search.trim()) return true
    const q = search.trim().toLowerCase()
    const name = (m.name || '').toLowerCase()
    const email = (m.email || '').toLowerCase()
    const skills = (m.skills || '').toLowerCase()
    const matched = (m.matched_skills || []).join(' ').toLowerCase()
    return name.includes(q) || email.includes(q) || skills.includes(q) || matched.includes(q)
  })

  useEffect(() => {
    (async () => {
      try {
        const [c, m] = await Promise.all([getCandidate(id), getMatches(id)])
        setCandidate(c)
        setMatches(m)
      } catch (err) {
        setError(err.message || 'Failed to load')
      } finally {
        setLoading(false)
      }
    })()
  }, [id])

  async function handleSelect(interviewerId, sendEmail = true) {
    setSelecting(interviewerId)
    setMessage('')
    try {
      const res = await selectInterviewer(Number(id), interviewerId, sendEmail)
      setMessage(
        res.email_sent
          ? `Selected ${res.interviewer_name}. Email sent to ${res.interviewer_email}.`
          : `Selected ${res.interviewer_name}. (Email not sent - check SMTP config.)`
      )
    } catch (err) {
      setMessage('Error: ' + (err.message || 'Failed'))
    } finally {
      setSelecting(null)
    }
  }

  if (loading) return <p style={{ color: 'var(--text-muted)' }}>Loading…</p>
  if (error) return <p style={{ color: 'var(--danger)' }}>{error}</p>
  if (!candidate) return null

  const cardStyle = {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 12,
    padding: '1.25rem',
  }
  const explanationStyle = {
    margin: '0.75rem 0',
    padding: '0.75rem',
    background: 'var(--bg)',
    borderRadius: 8,
    fontSize: '0.9rem',
    color: 'var(--text-muted)',
    fontStyle: 'italic',
  }

  return (
    <div>
      <h1 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Candidate Match Results</h1>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.1rem', marginBottom: '0.75rem', color: 'var(--text-muted)' }}>Extracted skills</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {candidate.skills?.length
            ? candidate.skills.map((s, i) => (
                <span
                  key={i}
                  style={{
                    background: 'var(--surface)',
                    border: '1px solid var(--border)',
                    padding: '0.35rem 0.75rem',
                    borderRadius: 6,
                    fontSize: '0.9rem',
                  }}
                >
                  {s.skill}
                </span>
              ))
            : 'No skills extracted'}
        </div>
      </div>
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '0.75rem' }}>
          <h2 style={{ fontSize: '1.1rem', margin: 0, color: 'var(--text-muted)' }}>Ranked interviewers (by match %)</h2>
          <input
            type="search"
            placeholder="Search by name, email, or skills…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: 280,
              padding: '0.6rem 1rem',
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              color: 'var(--text)',
              fontSize: '1rem',
            }}
            aria-label="Search matched interviewers"
          />
        </div>
        {message && <p style={{ color: 'var(--success)', marginBottom: '1rem' }}>{message}</p>}
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {filteredMatches.map((m, rank) => (
            <li key={m.interviewer_id} style={cardStyle}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ color: 'var(--accent)', fontWeight: 600 }}>#{rank + 1}</span>
                <span style={{ fontWeight: 600, color: 'var(--success)' }}>{m.score}% match</span>
              </div>
              <h3 style={{ margin: '0 0 0.25rem', fontSize: '1.1rem' }}>{m.name}</h3>
              <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-muted)' }}>{m.email}</p>
              <p style={{ margin: '0.5rem 0', fontSize: '0.9rem' }}><strong>Skills:</strong> {m.skills}</p>
              {m.matched_skills?.length > 0 && (
                <p style={{ margin: '0.25rem 0', fontSize: '0.85rem', color: 'var(--accent)' }}>Matched: {m.matched_skills.join(', ')}</p>
              )}
              {m.explanation && <p style={explanationStyle}>{m.explanation}</p>}
              <button
                style={{
                  marginTop: '0.75rem',
                  padding: '0.5rem 1rem',
                  background: 'var(--accent)',
                  color: 'white',
                  border: 'none',
                  borderRadius: 8,
                  fontWeight: 500,
                }}
                onClick={() => handleSelect(m.interviewer_id)}
                disabled={selecting !== null}
              >
                {selecting === m.interviewer_id ? 'Sending…' : 'Select & Send Email'}
              </button>
            </li>
          ))}
        </ul>
        {filteredMatches.length === 0 && (
          <p style={{ color: 'var(--text-muted)' }}>
            {matches.length === 0 ? 'No interviewers in the system. Add some first.' : 'No matched interviewers match your search.'}
          </p>
        )}
      </div>
    </div>
  )
}
