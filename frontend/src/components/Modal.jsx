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

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.5)',
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
          border: `1px solid ${isSuccess ? 'var(--success)' : 'var(--danger)'}`,
          borderRadius: 12,
          padding: '1.5rem',
          maxWidth: 420,
          width: '90%',
          boxShadow: '0 8px 24px rgba(0,0,0,0.3)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', marginBottom: '1rem' }}>
          <span
            style={{
              width: 40,
              height: 40,
              borderRadius: '50%',
              background: isSuccess ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              color: iconColor,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.25rem',
              flexShrink: 0,
            }}
            aria-hidden
          >
            {isSuccess ? '✓' : '!'}
          </span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <h3 id="modal-title" style={{ margin: 0, fontSize: '1.2rem', color: iconColor }}>
              {title}
            </h3>
            <p style={{ margin: '0.5rem 0 0', fontSize: '0.95rem', color: 'var(--text)', lineHeight: 1.5 }}>
              {message}
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: '0.5rem 1.25rem',
              background: iconColor,
              color: 'white',
              border: 'none',
              borderRadius: 8,
              fontWeight: 500,
            }}
          >
            OK
          </button>
        </div>
      </div>
    </div>
  )
}
