import { useState, useEffect, useCallback } from 'react'
import { getRecords, createRecord } from './api.js'
import RecordForm from './components/RecordForm.jsx'
import RecordList from './components/RecordList.jsx'

export default function App() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchRecords = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getRecords()
      // Most recent first
      const sorted = Array.isArray(data)
        ? [...data].sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
        : []
      setRecords(sorted)
    } catch (err) {
      // Generic message to user; full error logged only to console (OWASP A09)
      console.error('getRecords error:', err)
      setError('Kayıtlar yüklenirken bir hata oluştu. Lütfen sayfayı yenileyin.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchRecords()
  }, [fetchRecords])

  const handleSubmit = useCallback(async (title, content) => {
    // Input is already trimmed and validated in RecordForm (OWASP A03)
    await createRecord(title, content)
    await fetchRecords()
  }, [fetchRecords])

  return (
    <div>
      <header className="app-header">
        <h1>Kayıt Defteri</h1>
        <p>Notlarınızı güvenle saklayın</p>
      </header>

      <main className="app-container">
        {error && (
          <div className="error-banner" role="alert">
            <span>⚠</span>
            <span>{error}</span>
          </div>
        )}

        <RecordForm onSubmit={handleSubmit} />

        <section className="records-section">
          <h2>Kayıtlar</h2>
          <RecordList records={records} loading={loading} />
        </section>
      </main>
    </div>
  )
}
