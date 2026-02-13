import { useState, useEffect } from 'react'
import { getInterviewers, createInterviewer, updateInterviewer, deleteInterviewer } from '../api'

function skillsStringToPayload(skillsStr) {
  if (!skillsStr || !String(skillsStr).trim()) return []
  return String(skillsStr)
    .split(',')
    .map((s) => ({ skill_name: s.trim(), skill_type: 'Primary' }))
    .filter((s) => s.skill_name)
}

export default function Interviewers() {
  const [list, setList] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState({ name: '', email: '', level: '', experience_range: '', skills: '' })
  const [submitting, setSubmitting] = useState(false)

  const filteredList = list.filter((inv) => {
    if (!search.trim()) return true
    const q = search.trim().toLowerCase()
    const name = (inv.name || '').toLowerCase()
    const email = (inv.email || '').toLowerCase()
    const skillsStr = Array.isArray(inv.skills)
      ? inv.skills.map((s) => s.skill_name).join(' ').toLowerCase()
      : (inv.skills || '').toLowerCase()
    return name.includes(q) || email.includes(q) || skillsStr.includes(q)
  })

  useEffect(() => {
    load()
  }, [])

  async function load() {
    try {
      const data = await getInterviewers()
      setList(data)
    } catch (err) {
      setError(err.message || 'Failed to load')
    } finally {
      setLoading(false)
    }
  }

  function closeForm() {
    setShowForm(false)
    setEditingId(null)
    setForm({ name: '', email: '', level: '', experience_range: '', skills: '' })
  }

  async function handleEdit(inv) {
    setEditingId(inv.id)
    setForm({
      name: inv.name || '',
      email: inv.email || '',
      level: inv.level || '',
      experience_range: inv.experience_range || '',
      skills: Array.isArray(inv.skills) ? inv.skills.map((s) => s.skill_name).join(', ') : '',
    })
    setShowForm(true)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    const payload = {
      name: form.name.trim(),
      email: form.email.trim(),
      level: form.level?.trim() || null,
      experience_range: form.experience_range?.trim() || null,
      skills: skillsStringToPayload(form.skills),
    }
    try {
      if (editingId) {
        await updateInterviewer(editingId, payload)
        closeForm()
      } else {
        await createInterviewer(payload)
        closeForm()
      }
      await load()
    } catch (err) {
      setError(err.message || (editingId ? 'Failed to update' : 'Failed to create'))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this interviewer?')) return
    try {
      await deleteInterviewer(id)
      await load()
    } catch (err) {
      setError(err.message || 'Failed to delete')
    }
  }

  if (loading) return <p style={{ color: 'var(--text-muted)' }}>Loading…</p>

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Interviewers</h1>
        <button style={styles.addBtn} onClick={() => (showForm ? closeForm() : setShowForm(true))}>
          {showForm ? 'Cancel' : '+ Add interviewer'}
        </button>
      </div>
      <div style={styles.searchRow}>
        <div style={styles.searchWrap}>
          <input
            type="search"
            placeholder="Search by name, email, or skills…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={styles.searchInput}
            aria-label="Search interviewers"
          />
        </div>
      </div>
      {error && <p style={styles.error}>{error}</p>}
      {showForm && (
        <form onSubmit={handleSubmit} style={styles.form}>
          {editingId && <p style={{ margin: '0 0 0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>Editing interviewer</p>}
          <input
            placeholder="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
            style={styles.input}
          />
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
            style={styles.input}
          />
          <input
            placeholder="Level (e.g. Senior, Lead)"
            value={form.level}
            onChange={(e) => setForm({ ...form, level: e.target.value })}
            style={styles.input}
          />
          <input
            placeholder="Experience range (e.g. 0-2, 3-5, 5-10 years)"
            value={form.experience_range}
            onChange={(e) => setForm({ ...form, experience_range: e.target.value })}
            style={styles.input}
          />
          <input
            placeholder="Skills (comma-separated, e.g. Python, React, SQL)"
            value={form.skills}
            onChange={(e) => setForm({ ...form, skills: e.target.value })}
            required
            style={styles.input}
          />
          <button type="submit" disabled={submitting} style={styles.submitBtn}>
            {submitting ? 'Saving…' : editingId ? 'Update' : 'Save'}
          </button>
        </form>
      )}
      <ul style={styles.list}>
        {filteredList.map((inv) => (
          <li key={inv.id} style={styles.card}>
            <div>
              <strong>{inv.name}</strong> — {inv.email}
            </div>
            <p style={styles.skills}>Skills: {Array.isArray(inv.skills) ? inv.skills.map(s => s.skill_name).join(', ') : (inv.skills || '')}</p>
            {((inv.level != null && inv.level !== '') || (inv.experience_range != null && inv.experience_range !== '')) && (
              <p style={styles.meta}>
                {[inv.level, inv.experience_range ? `Exp: ${inv.experience_range}` : null].filter(Boolean).join(' · ')}
              </p>
            )}
            <div style={styles.cardActions}>
              <button type="button" style={styles.editBtn} onClick={() => handleEdit(inv)}>
                Edit
              </button>
              <button type="button" style={styles.delBtn} onClick={() => handleDelete(inv.id)}>
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
      {filteredList.length === 0 && (
        <p style={{ color: 'var(--text-muted)' }}>
          {list.length === 0 && !showForm ? 'No interviewers yet. Add one to get started.' : 'No interviewers match your search.'}
        </p>
      )}
    </div>
  )
}

const styles = {
  container: {},
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' },
  title: { fontSize: '1.5rem', margin: 0 },
  addBtn: {
    padding: '0.5rem 1rem',
    background: 'var(--accent)',
    color: 'white',
    border: 'none',
    borderRadius: 8,
    fontWeight: 500,
  },
  error: { color: 'var(--danger)', marginBottom: '1rem' },
  searchRow: { display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' },
  searchWrap: {},
  searchInput: {
    width: 280,
    padding: '0.6rem 1rem',
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 8,
    color: 'var(--text)',
    fontSize: '1rem',
  },
  form: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 12,
    padding: '1.25rem',
    marginBottom: '1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  input: {
    padding: '0.6rem 0.75rem',
    background: 'var(--bg)',
    border: '1px solid var(--border)',
    borderRadius: 8,
    color: 'var(--text)',
    width: '100%',
  },
  submitBtn: {
    padding: '0.6rem 1rem',
    background: 'var(--accent)',
    color: 'white',
    border: 'none',
    borderRadius: 8,
    fontWeight: 500,
    alignSelf: 'flex-start',
  },
  list: { listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' },
  card: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 12,
    padding: '1rem',
  },
  skills: { margin: '0.5rem 0', fontSize: '0.9rem', color: 'var(--text-muted)' },
  meta: { margin: '0.25rem 0', fontSize: '0.85rem', color: 'var(--text-muted)' },
  cardActions: { display: 'flex', gap: '0.5rem', marginTop: '0.5rem' },
  editBtn: {
    padding: '0.35rem 0.75rem',
    background: 'var(--accent)',
    color: 'white',
    border: 'none',
    borderRadius: 6,
    fontSize: '0.85rem',
    cursor: 'pointer',
  },
  delBtn: {
    padding: '0.35rem 0.75rem',
    background: 'transparent',
    color: 'var(--danger)',
    border: '1px solid var(--danger)',
    borderRadius: 6,
    fontSize: '0.85rem',
    cursor: 'pointer',
  },
}
