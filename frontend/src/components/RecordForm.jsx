import { useState } from 'react'

const TITLE_MAX = 200
const CONTENT_MAX = 5000

function charCountClass(current, max) {
  const ratio = current / max
  if (ratio >= 1) return 'char-count at-limit'
  if (ratio >= 0.9) return 'char-count near-limit'
  return 'char-count'
}

/**
 * RecordForm — controlled form for creating a new record.
 *
 * Security notes (OWASP A03 - Injection / Input Validation):
 *  - maxLength enforced both via HTML attribute and on submit
 *  - Whitespace trimmed server-side via trim() before submission
 *  - Server-side validation is the authoritative check; this is defence-in-depth
 *
 * Props:
 *  onSubmit(title: string, content: string): Promise<void>
 */
export default function RecordForm({ onSubmit }) {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitError(null)

    // Client-side trim + validation (OWASP A03 - defence in depth)
    const trimmedTitle = title.trim()
    const trimmedContent = content.trim()

    if (!trimmedTitle) {
      setSubmitError('Başlık boş bırakılamaz.')
      return
    }
    if (!trimmedContent) {
      setSubmitError('İçerik boş bırakılamaz.')
      return
    }
    if (trimmedTitle.length > TITLE_MAX) {
      setSubmitError(`Başlık en fazla ${TITLE_MAX} karakter olabilir.`)
      return
    }
    if (trimmedContent.length > CONTENT_MAX) {
      setSubmitError(`İçerik en fazla ${CONTENT_MAX} karakter olabilir.`)
      return
    }

    setSubmitting(true)
    try {
      await onSubmit(trimmedTitle, trimmedContent)
      // Clear form on success
      setTitle('')
      setContent('')
    } catch (err) {
      // Generic user-facing message; detail logged to console (OWASP A09)
      console.error('createRecord error:', err)
      const serverMsg = err?.response?.data?.detail
      setSubmitError(
        typeof serverMsg === 'string'
          ? serverMsg
          : 'Kayıt oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="form-card">
      <h2>Yeni Kayıt Ekle</h2>
      <form onSubmit={handleSubmit} noValidate>
        <div className="form-group">
          <label htmlFor="record-title">Başlık</label>
          <input
            id="record-title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={TITLE_MAX}
            placeholder="Kayıt başlığını girin..."
            required
            disabled={submitting}
            autoComplete="off"
          />
          <div className={charCountClass(title.length, TITLE_MAX)}>
            {title.length} / {TITLE_MAX}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="record-content">İçerik</label>
          <textarea
            id="record-content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            maxLength={CONTENT_MAX}
            placeholder="Kayıt içeriğini girin..."
            required
            disabled={submitting}
          />
          <div className={charCountClass(content.length, CONTENT_MAX)}>
            {content.length} / {CONTENT_MAX}
          </div>
        </div>

        {submitError && (
          <div className="form-error" role="alert">
            {submitError}
          </div>
        )}

        <button type="submit" className="submit-btn" disabled={submitting}>
          {submitting ? (
            <>
              <span className="spinner" aria-hidden="true" />
              Kaydediliyor...
            </>
          ) : (
            'Kaydet'
          )}
        </button>
      </form>
    </div>
  )
}
