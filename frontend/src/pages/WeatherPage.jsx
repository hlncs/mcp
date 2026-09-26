import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Grid,
  ToggleButton,
  ToggleButtonGroup,
  Alert,
  CircularProgress,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import SearchIcon from '@mui/icons-material/Search'
import CloudIcon from '@mui/icons-material/Cloud'
import ThermostatIcon from '@mui/icons-material/Thermostat'
import LocationOnIcon from '@mui/icons-material/LocationOn'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix Leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

export default function WeatherPage() {
  const navigate = useNavigate()
  const primaryColor = '#1976D2'
  const secondaryColor = '#42A5F5'

  const [location, setLocation] = useState('')
  const [temperatureUnit, setTemperatureUnit] = useState('celsius')
  const [selectedLocation, setSelectedLocation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Mock weather data with coordinates
  const weatherDatabase = {
    'sydney': {
      name: 'Sydney, Australia',
      lat: -33.8688,
      lng: 151.2093,
      temperature: 22,
      humidity: 65,
      windSpeed: 12,
      condition: 'Partly Cloudy',
      pressure: 1013,
    },
    'new york': {
      name: 'New York, USA',
      lat: 40.7128,
      lng: -74.0060,
      temperature: 15,
      humidity: 70,
      windSpeed: 8,
      condition: 'Cloudy',
      pressure: 1015,
    },
    'london': {
      name: 'London, UK',
      lat: 51.5074,
      lng: -0.1278,
      temperature: 12,
      humidity: 75,
      windSpeed: 10,
      condition: 'Rainy',
      pressure: 1010,
    },
    'tokyo': {
      name: 'Tokyo, Japan',
      lat: 35.6762,
      lng: 139.6503,
      temperature: 18,
      humidity: 60,
      windSpeed: 5,
      condition: 'Clear',
      pressure: 1018,
    },
    'paris': {
      name: 'Paris, France',
      lat: 48.8566,
      lng: 2.3522,
      temperature: 14,
      humidity: 68,
      windSpeed: 9,
      condition: 'Partly Cloudy',
      pressure: 1012,
    },
  }

  const handleSearch = () => {
    if (!location.trim()) {
      setError('Please enter a location')
      return
    }

    setLoading(true)
    setError(null)

    // Simulate API call
    setTimeout(() => {
      // Extract the city name from the input (e.g., "Sydney, Australia" → "sydney")
      const cityName = location.toLowerCase().split(',')[0].trim()
      const weatherData = weatherDatabase[cityName]

      if (weatherData) {
        setSelectedLocation(weatherData)
        setLocation('')
        setError(null)
      } else {
        const availableCities = Object.values(weatherDatabase)
          .map(w => w.name)
          .join(', ')
        setError(`Weather data not found for "${location}". Available locations: ${availableCities}`)
        setSelectedLocation(null)
      }

      setLoading(false)
    }, 500)
  }

  const convertTemperature = (celsius) => {
    if (temperatureUnit === 'fahrenheit') {
      return Math.round((celsius * 9/5) + 32)
    }
    return celsius
  }

  const getTemperatureSymbol = () => {
    return temperatureUnit === 'celsius' ? '°C' : '°F'
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Back Button */}
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/')}
          sx={{ mb: 3 }}
        >
          Back to Home
        </Button>

        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <CloudIcon sx={{ fontSize: 32, color: secondaryColor }} />
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#212121' }}>
              Weather Forecast
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Search for a location to view weather forecasts and find vendors nearby
          </Typography>
        </Box>

        {/* Search Section */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {/* Search Card */}
          <Grid item xs={12} md={6}>
            <Card sx={{ border: `1px solid #e0e0e0` }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  Search Location
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <TextField
                    fullWidth
                    label="Enter location"
                    placeholder="e.g., Sydney, Australia"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    onKeyPress={handleKeyPress}
                    variant="outlined"
                    size="small"
                    InputProps={{
                      startAdornment: (
                        <LocationOnIcon sx={{ mr: 1, color: 'text.secondary' }} />
                      ),
                    }}
                  />
                </Box>

                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<SearchIcon />}
                  onClick={handleSearch}
                  disabled={loading}
                  sx={{
                    backgroundColor: primaryColor,
                    '&:hover': {
                      backgroundColor: primaryColor,
                      opacity: 0.9,
                    },
                  }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Search'}
                </Button>

                {error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Temperature Unit Selection */}
          <Grid item xs={12} md={6}>
            <Card sx={{ border: `1px solid #e0e0e0` }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  Temperature Unit
                </Typography>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <ThermostatIcon sx={{ color: secondaryColor }} />
                  <ToggleButtonGroup
                    value={temperatureUnit}
                    exclusive
                    onChange={(e, newUnit) => {
                      if (newUnit !== null) {
                        setTemperatureUnit(newUnit)
                      }
                    }}
                    fullWidth
                  >
                    <ToggleButton
                      value="celsius"
                      sx={{
                        '&.Mui-selected': {
                          backgroundColor: secondaryColor,
                          color: 'white',
                          '&:hover': {
                            backgroundColor: secondaryColor,
                          },
                        },
                      }}
                    >
                      Celsius (°C)
                    </ToggleButton>
                    <ToggleButton
                      value="fahrenheit"
                      sx={{
                        '&.Mui-selected': {
                          backgroundColor: secondaryColor,
                          color: 'white',
                          '&:hover': {
                            backgroundColor: secondaryColor,
                          },
                        },
                      }}
                    >
                      Fahrenheit (°F)
                    </ToggleButton>
                  </ToggleButtonGroup>
                </Box>

                <Typography variant="caption" color="text.secondary">
                  Select your preferred temperature unit for weather displays
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Map and Weather Info */}
        {selectedLocation && (
          <>
            {/* Map Section */}
            <Card sx={{ mb: 4, border: `1px solid #e0e0e0`, overflow: 'hidden' }}>
              <Box sx={{ height: '400px', width: '100%' }}>
                <MapContainer
                  center={[selectedLocation.lat, selectedLocation.lng]}
                  zoom={13}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  />
                  <Marker
                    position={[selectedLocation.lat, selectedLocation.lng]}
                  >
                    <Popup>
                      <Box sx={{ p: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {selectedLocation.name}
                        </Typography>
                        <Typography variant="caption">
                          {selectedLocation.condition}
                        </Typography>
                      </Box>
                    </Popup>
                  </Marker>
                </MapContainer>
              </Box>
            </Card>

            {/* Weather Details */}
            <Card sx={{ border: `1px solid #e0e0e0` }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                  Weather Details for {selectedLocation.name}
                </Typography>

                <Grid container spacing={3}>
                  {/* Temperature */}
                  <Grid item xs={12} sm={6} md={3}>
                    <Box
                      sx={{
                        p: 2,
                        backgroundColor: `${secondaryColor}10`,
                        borderRadius: '8px',
                        border: `1px solid ${secondaryColor}20`,
                      }}
                    >
                      <Typography variant="caption" color="text.secondary">
                        Temperature
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
                        <Typography variant="h5" sx={{ fontWeight: 700, color: primaryColor }}>
                          {convertTemperature(selectedLocation.temperature)}
                        </Typography>
                        <Typography variant="body2" sx={{ color: primaryColor }}>
                          {getTemperatureSymbol()}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>

                  {/* Humidity */}
                  <Grid item xs={12} sm={6} md={3}>
                    <Box
                      sx={{
                        p: 2,
                        backgroundColor: `${secondaryColor}10`,
                        borderRadius: '8px',
                        border: `1px solid ${secondaryColor}20`,
                      }}
                    >
                      <Typography variant="caption" color="text.secondary">
                        Humidity
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
                        <Typography variant="h5" sx={{ fontWeight: 700, color: primaryColor }}>
                          {selectedLocation.humidity}
                        </Typography>
                        <Typography variant="body2" sx={{ color: primaryColor }}>
                          %
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>

                  {/* Wind Speed */}
                  <Grid item xs={12} sm={6} md={3}>
                    <Box
                      sx={{
                        p: 2,
                        backgroundColor: `${secondaryColor}10`,
                        borderRadius: '8px',
                        border: `1px solid ${secondaryColor}20`,
                      }}
                    >
                      <Typography variant="caption" color="text.secondary">
                        Wind Speed
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
                        <Typography variant="h5" sx={{ fontWeight: 700, color: primaryColor }}>
                          {selectedLocation.windSpeed}
                        </Typography>
                        <Typography variant="body2" sx={{ color: primaryColor }}>
                          km/h
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>

                  {/* Pressure */}
                  <Grid item xs={12} sm={6} md={3}>
                    <Box
                      sx={{
                        p: 2,
                        backgroundColor: `${secondaryColor}10`,
                        borderRadius: '8px',
                        border: `1px solid ${secondaryColor}20`,
                      }}
                    >
                      <Typography variant="caption" color="text.secondary">
                        Pressure
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
                        <Typography variant="h5" sx={{ fontWeight: 700, color: primaryColor }}>
                          {selectedLocation.pressure}
                        </Typography>
                        <Typography variant="body2" sx={{ color: primaryColor }}>
                          mb
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>

                  {/* Condition */}
                  <Grid item xs={12}>
                    <Box
                      sx={{
                        p: 2,
                        backgroundColor: `${secondaryColor}10`,
                        borderRadius: '8px',
                        border: `1px solid ${secondaryColor}20`,
                      }}
                    >
                      <Typography variant="caption" color="text.secondary">
                        Condition
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600, color: primaryColor }}>
                        {selectedLocation.condition}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </>
        )}

        {/* No Location Selected Message */}
        {!selectedLocation && !error && (
          <Card sx={{ border: `1px solid #e0e0e0` }}>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <CloudIcon sx={{ fontSize: 48, color: secondaryColor, mb: 2 }} />
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                Search for a location
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Enter a city name above to view weather forecast and see it on the map
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>
    </Container>
  )
}