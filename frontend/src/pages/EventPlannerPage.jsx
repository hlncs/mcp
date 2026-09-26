import React, { useState } from 'react'
import {
  Container,
  Box,
  TextField,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
} from '@mui/material'
import axios from 'axios'
import EventStreamViewer from '../components/EventStreamViewer'

const API_BASE_URL = 'http://localhost:8000'

export default function EventPlannerPage() {
  const [formData, setFormData] = useState({
    event_type: '',
    location: '',
    date: '',
    guest_count: '',
    budget: '',
  })
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(
        `${API_BASE_URL}/plan/create`,
        {
          ...formData,
          guest_count: parseInt(formData.guest_count),
          budget: parseFloat(formData.budget),
        }
      )

      setPlan(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create event plan')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSSETimeout = (data) => {
    console.warn('SSE Timeout:', data)
    // Show custom notification
  }

  const handleSSEError = (data) => {
    console.error('SSE Error:', data)
    // Handle different error types
    switch (data.type) {
      case 'PARSE_ERROR':
        // Handle JSON parsing errors
        break
      case 'CONNECTION_ERROR':
        // Handle connection errors
        break
      case 'SETUP_ERROR':
        // Handle setup errors
        break
    }
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Event Planner
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Event Details
                </Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                  <TextField
                    fullWidth
                    label="Event Type"
                    name="event_type"
                    value={formData.event_type}
                    onChange={handleChange}
                    margin="normal"
                    placeholder="e.g., wedding, conference, birthday"
                    required
                  />
                  <TextField
                    fullWidth
                    label="Location"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    margin="normal"
                    placeholder="e.g., Sydney, Australia"
                    required
                  />
                  <TextField
                    fullWidth
                    type="date"
                    label="Event Date"
                    name="date"
                    value={formData.date}
                    onChange={handleChange}
                    margin="normal"
                    InputLabelProps={{ shrink: true }}
                    required
                  />
                  <TextField
                    fullWidth
                    type="number"
                    label="Guest Count"
                    name="guest_count"
                    value={formData.guest_count}
                    onChange={handleChange}
                    margin="normal"
                    required
                  />
                  <TextField
                    fullWidth
                    type="number"
                    label="Budget (USD)"
                    name="budget"
                    value={formData.budget}
                    onChange={handleChange}
                    margin="normal"
                    required
                  />
                  <Button
                    fullWidth
                    variant="contained"
                    color="primary"
                    type="submit"
                    sx={{ mt: 3 }}
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Create Plan'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            {error && <Alert severity="error">{error}</Alert>}

            {plan && (
              <Grid container spacing={3} sx={{ mt: 2 }}>
                <Grid item xs={12}>
                  <EventStreamViewer
                    planId={plan.plan_id}
                    timeoutMs={30000} // 30 seconds
                    warningMs={10000} // Warn after 10 seconds
                    autoRetry={true}
                    maxRetries={3}
                    onTimeout={handleSSETimeout}
                    onError={handleSSEError}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Event Plan Summary
                      </Typography>

                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2">
                          <strong>Event:</strong> {plan.summary.event_type}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Location:</strong> {plan.summary.location}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Date:</strong> {plan.summary.date}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Guests:</strong> {plan.summary.guest_count}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Venue:</strong> {plan.summary.venue}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Catering:</strong> {plan.summary.catering}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Entertainment:</strong> {plan.summary.entertainment}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Total Cost:</strong> ${plan.summary.total_cost?.toFixed(2)}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Budget Status:</strong>{' '}
                          <span
                            style={{
                              color: plan.summary.budget_status === 'within_budget' ? 'green' : 'red',
                            }}
                          >
                            {plan.summary.budget_status}
                          </span>
                        </Typography>
                        <Typography variant="body2">
                          <strong>Weather Suitable:</strong>{' '}
                          {plan.summary.weather_suitable ? '✅ Yes' : '❌ No'}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}
          </Grid>
        </Grid>
      </Box>
    </Container>
  )
}