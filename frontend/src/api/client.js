import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance with default config
const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Request interceptor
client.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('[API] Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
client.interceptors.response.use(
  (response) => {
    console.log(`[API] Response:`, response.status, response.data)
    return response
  },
  (error) => {
    console.error('[API] Response error:', error.message)
    if (error.response) {
      console.error('[API] Status:', error.response.status)
      console.error('[API] Data:', error.response.data)
    }
    return Promise.reject(error)
  }
)

// API methods
export const apiClient = {
  // Health
  getHealth: () => client.get('/health'),

  // Plans
  createPlan: (query, context = {}, eventDetails = {}) =>
    client.post('/plan/create', {
      query,
      context,
      event_date: eventDetails.event_date,
      event_location: eventDetails.event_location,
      num_people: eventDetails.num_people,
      budget: eventDetails.budget,
    }),

  getPlan: (planId) => client.get(`/plan/${planId}`),

  listPlans: () => client.get('/plans'),

  // Weather
  getWeather: (query) => client.post('/weather', { query, context: {} }),

  getWeatherByLocation: (location) => client.get(`/weather/${location}`),

  // Location search (OpenStreetMap Nominatim)
  searchLocation: (query) => client.get('/location/search', { params: { q: query } }),

  // Bookings (human-in-the-loop)
  listBookings: (planId) =>
    client.get('/bookings', planId ? { params: { plan_id: planId } } : {}),

  getBooking: (bookingId) => client.get(`/bookings/${bookingId}`),

  decideBooking: (bookingId, approved, note = '') =>
    client.put(`/bookings/${bookingId}/decision`, { approved, note }),

  // MCP tools
  executeMcpTool: (toolName, args) => client.post(`/mcp/tools/${toolName}`, args),

  // Metrics
  getMetrics: () => client.get('/metrics'),
}

export default client