/**
 * RecordList — displays records sorted newest-first (parent handles sort).
 *
 * Props:
 *  records: Array<{ id, title, content, created_at }>
 *  loading: boolean
 */
export default function RecordList({ records, loading }) {
  if (loading) {
    return (
      <div aria-busy="true" aria-label="Yükleniyor">
        {[1, 2, 3].map((n) => (
          <div key={n} className="skeleton-card">
            <div className="skeleton-line short" />
            <div className="skeleton-line long" />
            <div className="skeleton-line medium" />
          </div>
        ))}
      </div>
    )
  }

  if (!records || records.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📋</div>
        <p>Henüz kayıt yok</p>
      </div>
    )
  }

  return (
    <div>
      {records.map((record) => (
        <article key={record.id} className="record-card">
          <div className="record-title">{record.title}</div>
          <div className="record-content">{record.content}</div>
          <div className="record-meta">
            <span>🕐</span>
            <time dateTime={record.created_at}>
              {record.created_at
                ? new Date(record.created_at).toLocaleDateString('tr-TR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })
                : '—'}
            </time>
          </div>
        </article>
      ))}
    </div>
  )
}
