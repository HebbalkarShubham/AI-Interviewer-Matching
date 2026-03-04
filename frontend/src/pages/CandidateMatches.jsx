import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import { getCandidate, getMatches, scheduleInterview } from '../api'
import Modal from '../components/Modal'
import { formatSkillsString, formatSkillLabel } from '../utils/skillsFormat'

export default function CandidateMatches() {
  const { id } = useParams()
  const [candidate, setCandidate] = useState(null)
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)
  const [scheduleModalFor, setScheduleModalFor] = useState(null) // interviewer id when modal open
  const [scheduleSending, setScheduleSending] = useState(false)
  const [scheduleError, setScheduleError] = useState('')
  const [successModalMessage, setSuccessModalMessage] = useState(null)
  const [errorModalMessage, setErrorModalMessage] = useState(null)
  const [search, setSearch] = useState('')
  // Form state for schedule modal (select only, no typing)
  const [scheduleDate, setScheduleDate] = useState('')
  const [scheduleTime, setScheduleTime] = useState('')
  const [scheduleCustomMessage, setScheduleCustomMessage] = useState('')
  const [scheduleDateObj, setScheduleDateObj] = useState(null)
  const [scheduleTimeObj, setScheduleTimeObj] = useState(null)

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
        setErrorModalMessage(err.message || 'Failed to load')
      } finally {
        setLoading(false)
      }
    })()
  }, [id])

  function openScheduleModal(interviewerId) {
    setScheduleModalFor(interviewerId)
    setScheduleDate('')
    setScheduleTime('')
    setScheduleDateObj(null)
    setScheduleTimeObj(null)
    setScheduleCustomMessage('')
    setScheduleError('')
  }

  function closeScheduleModal() {
    setScheduleModalFor(null)
    setScheduleError('')
  }

  function clearSuccessModal() {
    setSuccessModalMessage(null)
  }
  function clearErrorModal() {
    setErrorModalMessage(null)
  }

  function getTodayISO() {
    const d = new Date()
    return d.toISOString().slice(0, 10)
  }

  async function handleScheduleAndSend() {
    if (!scheduleDate.trim()) {
      setScheduleError('Date is required.')
      return
    }
    if (!scheduleTime.trim()) {
      setScheduleError('Time is required.')
      return
    }
    const chosen = new Date(`${scheduleDate}T${scheduleTime}`)
    if (chosen < new Date()) {
      setScheduleError('Cannot select a past date and time.')
      return
    }
    setScheduleSending(true)
    setScheduleError('')
    try {
      const res = await scheduleInterview(
        Number(id),
        scheduleModalFor,
        scheduleDate,
        scheduleTime,
        scheduleCustomMessage.trim() || null
      )
      setSuccessModalMessage(
        res.email_sent
          ? `Interview scheduled for ${res.date} at ${res.time}. Email sent to ${res.interviewer_email}.`
          : `Interview scheduled for ${res.date} at ${res.time}. (Email not sent - check SMTP config.)`
      )
      closeScheduleModal()
    } catch (err) {
      closeScheduleModal()
      setErrorModalMessage(err.message || 'Failed to schedule')
    } finally {
      setScheduleSending(false)
    }
  }

  if (loading) return <p style={{ color: 'var(--text-muted)', padding: '2rem 0', fontSize: '1rem' }}>Loading…</p>
  if (!candidate) {
    if (errorModalMessage) {
      return (
        <>
          <Modal variant="error" title="Error" message={errorModalMessage} onClose={clearErrorModal} />
          <p style={{ color: 'var(--danger)' }}>Failed to load. Go back to candidates.</p>
        </>
      )
    }
    return null
  }

  const cardStyle = {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    padding: '1.35rem',
  }
  const explanationStyle = {
    margin: '0.75rem 0',
    padding: '0.85rem',
    background: 'var(--bg-subtle)',
    borderRadius: 'var(--radius-sm)',
    fontSize: '0.9rem',
    color: 'var(--text-muted)',
    fontStyle: 'italic',
  }

  return (
    <div>
      {candidate?.name && (
        <p style={{ margin: '0 0 0.25rem', fontSize: '0.95rem', color: 'var(--text-muted)' }}>
          Candidate Name: <strong style={{ color: 'var(--text)' }}>{candidate.name.replace(/\b\w/g, (c) => c.toUpperCase())}</strong>
        </p>
      )}
      <h1 style={{ fontSize: '1.6rem', fontWeight: 700, marginBottom: '1.5rem', letterSpacing: '-0.02em' }}>Candidate Match Results</h1>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Extracted skills</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {candidate.skills?.length
            ? candidate.skills.map((s, i) => (
                <span
                  key={i}
                  style={{
                    background: 'var(--surface)',
                    border: '1px solid var(--border)',
                    padding: '0.4rem 0.85rem',
                    borderRadius: 'var(--radius-sm)',
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
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1rem' }}>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 600, margin: 0, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Ranked interviewers (by match %)</h2>
          <input
            type="search"
            placeholder="Search by name, email, or skills…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: 280,
              padding: '0.65rem 1rem',
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text)',
              fontSize: '1rem',
            }}
            aria-label="Search matched interviewers"
          />
        </div>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {filteredMatches.map((m, rank) => (
            <li key={m.interviewer_id} className="card-hover" style={cardStyle}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ background: 'var(--accent-glow)', color: 'var(--accent)', padding: '0.25rem 0.6rem', borderRadius: 'var(--radius-sm)', fontWeight: 700, fontSize: '0.85rem' }}>#{rank + 1}</span>
                <span style={{ fontWeight: 600, color: 'var(--success)', fontSize: '0.95rem' }}>{m.score}% match</span>
              </div>
              <h3 style={{ margin: '0 0 0.25rem', fontSize: '1.1rem', fontWeight: 600 }}>{m.name}</h3>
              <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-muted)' }}>{m.email}</p>
              <p style={{ margin: '0.5rem 0', fontSize: '0.9rem' }}><strong>Skills:</strong> {formatSkillsString(m.skills)}</p>
              {m.matched_skills?.length > 0 && (
                <p style={{ margin: '0.25rem 0', fontSize: '0.85rem', color: 'var(--accent)' }}>Matched: {m.matched_skills.map(formatSkillLabel).join(', ')}</p>
              )}
              {m.explanation && <p style={explanationStyle}>{m.explanation}</p>}
              <button
                className="btn-primary"
                style={{ marginTop: '0.85rem', padding: '0.55rem 1.1rem', fontSize: '0.9rem' }}
                onClick={() => openScheduleModal(m.interviewer_id)}
              >
                Send Email
              </button>
            </li>
          ))}
        </ul>
        {filteredMatches.length === 0 && (
          <p style={{ color: 'var(--text-muted)', margin: 0 }}>
            {matches.length === 0 ? 'No interviewers in the system. Add some first.' : 'No matched interviewers match your search.'}
          </p>
        )}
      </div>

      {/* Schedule Interview Modal */}
      {scheduleModalFor != null && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.6)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
          onClick={scheduleSending ? undefined : closeScheduleModal}
        >
          <div
            style={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-xl)',
              padding: '1.75rem',
              maxWidth: 420,
              width: '90%',
              boxShadow: 'var(--shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ margin: '0 0 0.5rem', fontSize: '1.25rem', fontWeight: 700 }}>Schedule & Send Email</h3>
            <p style={{ margin: '0 0 1.25rem', fontSize: '0.95rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              Choose date and time for the interview. An email with Accept/Reject will be sent to the interviewer.
            </p>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.4rem', fontWeight: 600, fontSize: '0.9rem' }}>Date (required)</label>
              <DatePicker
                selected={scheduleDateObj}
                onChange={(d) => {
                  setScheduleDateObj(d)
                  if (!d) setScheduleDate('')
                  else {
                    const pad = (n) => (n < 10 ? '0' + n : '' + n)
                    setScheduleDate(`${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`)
                  }
                }}
                onKeyDown={(e) => e.preventDefault()}
                minDate={new Date()}
                dateFormat="MMMM d, yyyy"
                placeholderText="Select date"
                showMonthDropdown
                showYearDropdown
                dropdownMode="select"
                className="schedule-datepicker"
                calendarClassName="schedule-datepicker-calendar"
                popperClassName="schedule-datepicker-popper"
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.4rem', fontWeight: 600, fontSize: '0.9rem' }}>Time (required)</label>
              <DatePicker
                selected={scheduleTimeObj}
                onChange={(d) => {
                  setScheduleTimeObj(d)
                  if (!d) setScheduleTime('')
                  else {
                    const pad = (n) => (n < 10 ? '0' + n : '' + n)
                    setScheduleTime(`${pad(d.getHours())}:${pad(d.getMinutes())}`)
                  }
                }}
                onKeyDown={(e) => e.preventDefault()}
                showTimeSelect
                showTimeSelectOnly
                timeIntervals={15}
                timeCaption="Time"
                dateFormat="h:mm aa"
                placeholderText="Select time"
                className="schedule-datepicker schedule-timepicker"
                calendarClassName="schedule-datepicker-calendar"
                popperClassName="schedule-datepicker-popper"
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.4rem', fontWeight: 600, fontSize: '0.9rem' }}>Optional message</label>
              <textarea
                value={scheduleCustomMessage}
                onChange={(e) => setScheduleCustomMessage(e.target.value)}
                placeholder="Add a note for the interviewer…"
                rows={3}
                style={{
                  width: '100%',
                  padding: '0.65rem',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--bg)',
                  color: 'var(--text)',
                  resize: 'vertical',
                  fontSize: '1rem',
                }}
              />
            </div>
            {scheduleError && (
              <p style={{ color: 'var(--danger)', marginBottom: '1rem', fontSize: '0.9rem' }}>{scheduleError}</p>
            )}
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
              <button
                type="button"
                onClick={closeScheduleModal}
                disabled={scheduleSending}
                style={{
                  padding: '0.55rem 1.1rem',
                  background: 'var(--bg)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text)',
                  fontWeight: 500,
                }}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleScheduleAndSend}
                disabled={scheduleSending}
                className="btn-primary"
                style={{ padding: '0.55rem 1.1rem', fontSize: '0.95rem' }}
              >
                {scheduleSending ? 'Sending…' : 'Schedule & Send'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Success modal when email is sent */}
      {successModalMessage && (
        <Modal
          variant="success"
          title="Email sent"
          message={successModalMessage}
          onClose={clearSuccessModal}
        />
      )}

      {/* Error modal for any error */}
      {errorModalMessage && (
        <Modal
          variant="error"
          title="Error"
          message={errorModalMessage}
          onClose={clearErrorModal}
        />
      )}
    </div>
  )
}
