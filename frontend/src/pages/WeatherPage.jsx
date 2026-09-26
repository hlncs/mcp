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
import CloudIcon from '@mui/icons-material/Cloud'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export default function WeatherPage() {
  const [location, setLocation] = useState('')
  const [date, setDate] = useState('')
  const [weather, setWeather] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_BASE_URL}/weather`, {
        location,
        date,
      })
      setWeather(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch weather')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Weather Forecast
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box component="form" onSubmit={handleSubmit}>
                  <TextField
                    fullWidth
                    label="Location"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    margin="normal"
                    placeholder="e.g., Sydney, Australia"
                    required
                  />
                  <TextField
                    fullWidth
                    type="date"
                    label="Date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    margin="normal"
                    InputLabelProps={{ shrink: true }}
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
                    {loading ? <CircularProgress size={24} /> : 'Check Weather'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            {error && <Alert severity="error">{error}</Alert>}

            {weather && !weather.error && (
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CloudIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                    <Typography variant="h6">Weather Forecast</Typography>
                  </Box>

                  <Typography variant="body2">
                    <strong>Location:</strong> {weather.location}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Date:</strong> {weather.date}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Temperature:</strong> {weather.temperature}°C
                  </Typography>
                  <Typography variant="body2">
                    <strong>Condition:</strong> {weather.condition}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Confidence:</strong> {(weather.confidence * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="body2">
                    <strong>Humidity:</strong> {weather.humidity}%
                  </Typography>
                  <Typography variant="body2">
                    <strong>Wind Speed:</strong> {weather.wind_speed} km/h
                  </Typography>
                  <Typography
                    variant="body2"
                    sx={{
                      mt: 2,
                      color: weather.is_favorable ? 'green' : 'red',
                      fontWeight: 'bold',
                    }}
                  >
                    {weather.is_favorable
                      ? '✅ Favorable for outdoor events'
                      : '❌ Not ideal for outdoor events'}
                  </Typography>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </Box>
    </Container>
  )
}