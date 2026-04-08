// OWASP A03 - Input validation is applied at the component level before these calls.
// All requests go through /api which nginx proxies to the backend.
import axios from 'axios'

const client = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json'
  },
  // Timeout to prevent hanging requests (OWASP A10)
  timeout: 15000
})

/**
 * Fetch all records from the backend.
 * @returns {Promise<Array>} Array of record objects
 * @throws Will throw an AxiosError on network or server error
 */
export async function getRecords() {
  const response = await client.get('/api/records')
  return response.data
}

/**
 * Create a new record.
 * @param {string} title - Record title (max 200 chars, trimmed)
 * @param {string} content - Record content (max 5000 chars, trimmed)
 * @returns {Promise<Object>} The created record object
 * @throws Will throw an AxiosError on network or server error
 */
export async function createRecord(title, content) {
  const response = await client.post('/api/records', { title, content })
  return response.data
}
