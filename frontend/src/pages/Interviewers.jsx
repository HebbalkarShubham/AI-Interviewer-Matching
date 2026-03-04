import { useState, useEffect } from 'react'
import { getInterviewers, createInterviewer, updateInterviewer, deleteInterviewer } from '../api'
import { formatSkillsString } from '../utils/skillsFormat'

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
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState({ name: '', email: '', level: '', experience_range: '', skills: '' })
  const [initialForm, setInitialForm] = useState(null) // snapshot when edit modal opened, for dirty check
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

  function openAddModal() {
    setForm({ name: '', email: '', level: '', experience_range: '', skills: '' })
    setShowAddModal(true)
  }

  function closeAddModal() {
    setShowAddModal(false)
    setForm({ name: '', email: '', level: '', experience_range: '', skills: '' })
  }

  function openEditModal(inv) {
    const formData = {
      name: inv.name || '',
      email: inv.email || '',
      level: inv.level || '',
      experience_range: inv.experience_range || '',
      skills: Array.isArray(inv.skills) ? inv.skills.map((s) => s.skill_name).join(', ') : '',
    }
    setEditingId(inv.id)
    setForm(formData)
    setInitialForm(formData)
  }

  function closeEditModal() {
    setEditingId(null)
    setInitialForm(null)
    setForm({ name: '', email: '', level: '', experience_range: '', skills: '' })
  }

  const isEditDirty = initialForm && (
    form.name.trim() !== initialForm.name.trim() ||
    form.email.trim() !== initialForm.email.trim() ||
    (form.level || '').trim() !== (initialForm.level || '').trim() ||
    (form.experience_range || '').trim() !== (initialForm.experience_range || '').trim() ||
    form.skills.trim() !== initialForm.skills.trim()
  )

  async function handleAddSave(e) {
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
      await createInterviewer(payload)
      closeAddModal()
      await load()
    } catch (err) {
      setError(err.message || 'Failed to create')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleEditSave(e) {
    e.preventDefault()
    if (!editingId) return
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
      await updateInterviewer(editingId, payload)
      closeEditModal()
      await load()
    } catch (err) {
      setError(err.message || 'Failed to update')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDeleteFromModal() {
    if (!editingId) return
    if (!confirm('Delete this interviewer?')) return
    try {
      await deleteInterviewer(editingId)
      closeEditModal()
      await load()
    } catch (err) {
      setError(err.message || 'Failed to delete')
    }
  }

  if (loading) {
    return (
      <div style={styles.loading}>
        <span style={styles.loadingDot}>Loading…</span>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <div style={styles.pageHeader}>
        <h1 style={styles.title}>Interviewers</h1>
      </div>
      <div style={styles.actionBar}>
        <div style={styles.actionBarLeft}>
          <input
            type="search"
            placeholder="Search by name, email, or skills…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={styles.searchInput}
            aria-label="Search interviewers"
          />
        </div>
        <div style={styles.actionBarRight}>
          <button className="btn-primary" style={styles.addBtn} onClick={openAddModal}>
            + Add interviewer
          </button>
        </div>
      </div>
      {error && <p style={styles.error}>{error}</p>}
      <div style={styles.tableWrap}>
        {filteredList.length > 0 ? (
          <>
          <table className="interviewers-table" aria-label="Interviewers list">
            <thead>
              <tr>
                <th style={styles.thActions}>Actions</th>
                <th style={styles.thIcon}></th>
                <th>Name</th>
                <th>Email</th>
                <th>Skills</th>
                <th>Level</th>
                <th>Experience</th>
              </tr>
            </thead>
            <tbody>
              {filteredList.map((inv) => (
                <tr key={inv.id}>
                  <td className="cell-actions" style={styles.cellActions}>
                    <button type="button" style={styles.editBtn} onClick={() => openEditModal(inv)}>Edit</button>
                  </td>
                  <td style={styles.tdIcon}>
                    <span style={styles.avatar}>
                      {(inv.name || '?').charAt(0).toUpperCase()}
                    </span>
                  </td>
                  <td style={styles.cellName}>{inv.name}</td>
                  <td style={styles.cellEmail}>{inv.email}</td>
                  <td style={styles.cellSkills}>
                    {formatSkillsString(Array.isArray(inv.skills) ? inv.skills.map(s => s.skill_name).join(', ') : (inv.skills || '')) || '—'}
                  </td>
                  <td>{inv.level || '—'}</td>
                  <td>{inv.experience_range || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p style={styles.tableFooter}>
            Showing {filteredList.length} interviewer{filteredList.length !== 1 ? 's' : ''}
          </p>
          </>
        ) : (
          <p style={styles.empty}>
            {list.length === 0 ? 'No interviewers yet. Add one to get started.' : 'No interviewers match your search.'}
          </p>
        )}
      </div>

      {/* Edit interviewer modal */}
      {editingId != null && (
        <div
          style={styles.modalBackdrop}
          onClick={closeEditModal}
        >
          <div
            style={styles.modalPanel}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={styles.modalTitle}>Edit interviewer</h3>
            <form onSubmit={handleEditSave} style={styles.modalForm}>
              <label style={styles.modalLabel}>Name</label>
              <input
                placeholder="Name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                style={styles.input}
              />
              <label style={styles.modalLabel}>Email</label>
              <input
                type="email"
                placeholder="Email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
                style={styles.input}
              />
              <label style={styles.modalLabel}>Level (e.g. Senior, Lead)</label>
              <input
                placeholder="Level"
                value={form.level}
                onChange={(e) => setForm({ ...form, level: e.target.value })}
                style={styles.input}
              />
              <label style={styles.modalLabel}>Experience range</label>
              <input
                placeholder="e.g. 0-2, 3-5, 5-10 years"
                value={form.experience_range}
                onChange={(e) => setForm({ ...form, experience_range: e.target.value })}
                style={styles.input}
              />
              <label style={styles.modalLabel}>Skills (comma-separated)</label>
              <input
                placeholder="e.g. Python, React, SQL"
                value={form.skills}
                onChange={(e) => setForm({ ...form, skills: e.target.value })}
                required
                style={styles.input}
              />
              <div style={styles.modalActions}>
                <button type="button" style={styles.modalDelBtn} onClick={handleDeleteFromModal}>
                  Delete
                </button>
                <button type="button" style={styles.modalCancelBtn} onClick={closeEditModal}>
                  Cancel
                </button>
                {isEditDirty && (
                  <button type="submit" disabled={submitting} className="btn-primary" style={styles.modalSaveBtn}>
                    {submitting ? 'Saving…' : 'Save'}
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add interviewer modal */}
      {showAddModal && (
        <div style={styles.modalBackdrop} onClick={closeAddModal}>
          <div style={styles.modalPanel} onClick={(e) => e.stopPropagation()}>
            <h3 style={styles.modalTitle}>Add interviewer</h3>
            <form onSubmit={handleAddSave} style={styles.modalForm}>
              <label style={styles.modalLabel}>Name</label>
              <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required style={styles.input} />
              <label style={styles.modalLabel}>Email</label>
              <input type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required style={styles.input} />
              <label style={styles.modalLabel}>Level (e.g. Senior, Lead)</label>
              <input placeholder="Level" value={form.level} onChange={(e) => setForm({ ...form, level: e.target.value })} style={styles.input} />
              <label style={styles.modalLabel}>Experience range</label>
              <input placeholder="e.g. 0-2, 3-5, 5-10 years" value={form.experience_range} onChange={(e) => setForm({ ...form, experience_range: e.target.value })} style={styles.input} />
              <label style={styles.modalLabel}>Skills (comma-separated)</label>
              <input placeholder="e.g. Python, React, SQL" value={form.skills} onChange={(e) => setForm({ ...form, skills: e.target.value })} required style={styles.input} />
              <div style={styles.modalActions}>
                <button type="button" style={styles.modalCancelBtn} onClick={closeAddModal}>Cancel</button>
                <button type="submit" disabled={submitting} className="btn-primary" style={styles.modalSaveBtn}>
                  {submitting ? 'Saving…' : 'Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

const styles = {
  container: { width: '100%', minHeight: '70vh' },
  loading: { padding: '2rem 0', color: 'var(--text-muted)' },
  loadingDot: { fontSize: '1rem' },
  pageHeader: { marginBottom: '0.5rem' },
  title: { fontSize: '1.75rem', fontWeight: 700, margin: 0, letterSpacing: '-0.02em', color: 'var(--text)' },
  tabsRow: {
    display: 'flex',
    gap: '0.5rem',
    marginBottom: '1rem',
    borderBottom: '1px solid var(--border)',
  },
  tabActive: {
    padding: '0.5rem 0',
    marginBottom: '-1px',
    borderBottom: '2px solid var(--accent)',
    fontSize: '0.9rem',
    fontWeight: 600,
    color: 'var(--accent)',
  },
  actionBar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '1rem',
    marginBottom: '1rem',
    flexWrap: 'wrap',
  },
  actionBarLeft: { flex: '1 1 240px', minWidth: 0 },
  actionBarRight: { flexShrink: 0 },
  addBtn: { padding: '0.55rem 1.1rem', borderRadius: 'var(--radius-md)', fontSize: '0.9rem' },
  error: { color: 'var(--danger)', marginBottom: '1rem', fontSize: '0.95rem' },
  searchInput: {
    width: '100%',
    maxWidth: 320,
    padding: '0.6rem 0.9rem',
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
    color: 'var(--text)',
    fontSize: '0.95rem',
  },
  form: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    padding: '1.5rem',
    marginBottom: '1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.85rem',
  },
  input: {
    padding: '0.65rem 0.9rem',
    background: 'var(--bg)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
    color: 'var(--text)',
    width: '100%',
    fontSize: '1rem',
  },
  submitBtn: { padding: '0.65rem 1.1rem', alignSelf: 'flex-start', fontSize: '0.95rem' },
  tableWrap: { marginTop: 0, overflowX: 'auto', width: '100%' },
  tableFooter: {
    margin: 0,
    padding: '0.6rem 1rem',
    borderTop: '1px solid var(--border)',
    fontSize: '0.8rem',
    color: 'var(--text-muted)',
    background: 'var(--bg-subtle)',
  },
  thIcon: { width: 44 },
  thActions: { width: 80 },
  tdIcon: { width: 44, paddingRight: 0 },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: '50%',
    background: 'var(--accent-glow)',
    color: 'var(--accent)',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '0.85rem',
    fontWeight: 600,
  },
  cellName: { fontWeight: 600 },
  cellEmail: { color: 'var(--text-muted)', fontSize: '0.9rem' },
  cellSkills: { color: 'var(--text-muted)', fontSize: '0.85rem' },
  cellActions: {},
  editBtn: {
    padding: '0.3rem 0.65rem',
    background: 'var(--accent)',
    color: 'white',
    border: 'none',
    borderRadius: 'var(--radius-sm)',
    fontSize: '0.8rem',
    fontWeight: 500,
  },
  delBtn: {
    padding: '0.3rem 0.65rem',
    background: 'transparent',
    color: 'var(--danger)',
    border: '1px solid var(--danger)',
    borderRadius: 'var(--radius-sm)',
    fontSize: '0.8rem',
    fontWeight: 500,
  },
  empty: { color: 'var(--text-muted)', margin: 0, padding: '2rem 0' },
  modalBackdrop: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.6)',
    backdropFilter: 'blur(4px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modalPanel: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-xl)',
    padding: '1.75rem',
    maxWidth: 420,
    width: '90%',
    boxShadow: 'var(--shadow-lg)',
  },
  modalTitle: { margin: '0 0 1.25rem', fontSize: '1.25rem', fontWeight: 700 },
  modalForm: { display: 'flex', flexDirection: 'column', gap: '0.85rem' },
  modalLabel: { fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-muted)' },
  modalActions: {
    display: 'flex',
    gap: '0.75rem',
    marginTop: '0.5rem',
    justifyContent: 'flex-end',
    flexWrap: 'wrap',
  },
  modalDelBtn: {
    padding: '0.5rem 1rem',
    background: 'transparent',
    color: 'var(--danger)',
    border: '1px solid var(--danger)',
    borderRadius: 'var(--radius-md)',
    fontSize: '0.9rem',
    fontWeight: 500,
    marginRight: 'auto',
  },
  modalCancelBtn: {
    padding: '0.5rem 1rem',
    background: 'var(--bg)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)',
    color: 'var(--text)',
    fontSize: '0.9rem',
  },
  modalSaveBtn: { padding: '0.5rem 1.25rem', fontSize: '0.9rem' },
}
