/**
 * Reusable modal for success or error messages.
 * @param {string} variant - 'success' | 'error'
 * @param {string} title - Modal title
 * @param {string} message - Body text
 * @param {function} onClose - Called when user dismisses (e.g. OK click or backdrop click)
 */
export default function Modal({ variant = 'success', title, message, onClose }) {
  const isSuccess = variant === 'success'
  const iconColor = isSuccess ? 'var(--success)' : 'var(--danger)'
  const iconBg = isSuccess ? 'var(--success-dim)' : 'var(--danger-dim)'

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.6)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1100,
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'var(--surface)',
          border: `1px solid ${iconColor}`,
          borderRadius: 'var(--radius-xl)',
          padding: '1.75rem',
          maxWidth: 420,
          width: '90%',
          boxShadow: 'var(--shadow-lg)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', marginBottom: '1.25rem' }}>
          <span
            style={{
              width: 44,
              height: 44,
              borderRadius: '50%',
              background: iconBg,
              color: iconColor,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.35rem',
              flexShrink: 0,
              fontWeight: 700,
            }}
            aria-hidden
          >
            {isSuccess ? '✓' : '!'}
          </span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <h3 id="modal-title" style={{ margin: 0, fontSize: '1.2rem', fontWeight: 700, color: iconColor }}>
              {title}
            </h3>
            <p style={{ margin: '0.5rem 0 0', fontSize: '0.95rem', color: 'var(--text)', lineHeight: 1.55 }}>
              {message}
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: '0.55rem 1.35rem',
              background: iconColor,
              color: 'white',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              fontSize: '0.95rem',
            }}
          >
            OK
          </button>
        </div>
      </div>
    </div>
  )
}
