import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Box,
  Card,
  CardContent,
  Button,
  Typography,
  Grid,
  ToggleButton,
  ToggleButtonGroup,
  Alert,
  CircularProgress,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import CloudIcon from '@mui/icons-material/Cloud'
import ThermostatIcon from '@mui/icons-material/Thermostat'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import LocationSearch from '../components/LocationSearch'

// Fix Leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Open-Meteo WMO code → human text (matches assistant-parser mapping)
const WMO_CODES = {
  0: 'Clear Sky', 1: 'Mainly Clear', 2: 'Partly Cloudy', 3: 'Overcast',
  45: 'Fog', 48: 'Depositing Rime Fog',
  51: 'Light Drizzle', 53: 'Moderate Drizzle', 55: 'Dense Drizzle',
  61: 'Slight Rain', 63: 'Moderate Rain', 65: 'Heavy Rain',
  71: 'Slight Snow', 73: 'Moderate Snow', 75: 'Heavy Snow',
  80: 'Slight Rain Showers', 81: 'Moderate Rain Showers', 82: 'Violent Rain Showers',
  95: 'Thunderstorm', 96: 'Thunderstorm with Slight Hail', 99: 'Thunderstorm with Heavy Hail',
}

async function fetchOpenMeteoWeather(lat, lon) {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Open-Meteo error ${res.status}`)
  const data = await res.json()
  const cw = data.current_weather
  return {
    temperature: cw.temperature,
    windSpeed: cw.windspeed,
    condition: WMO_CODES[cw.weathercode] ?? `Code ${cw.weathercode}`,
    time: cw.time,
  }
}

export default function WeatherPage() {
  const navigate = useNavigate()
  const primaryColor = '#1976D2'
  const secondaryColor = '#42A5F5'

  const [locationQuery, setLocationQuery] = useState('')
  const [selectedLocation, setSelectedLocation] = useState(null)   // OSM suggestion object
  const [weatherData, setWeatherData] = useState(null)
  const [temperatureUnit, setTemperatureUnit] = useState('celsius')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleLocationSelect = async (suggestion) => {
    setLocationQuery(suggestion.short_name)
    setSelectedLocation(suggestion)
    setWeatherData(null)
    setError(null)
    setLoading(true)
    try {
      const wx = await fetchOpenMeteoWeather(suggestion.lat, suggestion.lon)
      setWeatherData(wx)
    } catch (err) {
      setError(`Could not fetch weather data: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const convertTemperature = (celsius) =>
    temperatureUnit === 'fahrenheit' ? Math.round((celsius * 9) / 5 + 32) : celsius

  const tempSymbol = temperatureUnit === 'celsius' ? '°C' : '°F'

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/')} sx={{ mb: 3 }}>
          Back to Home
        </Button>

        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <CloudIcon sx={{ fontSize: 32, color: secondaryColor }} />
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#212121' }}>
              Weather Forecast
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Search any location — suggestions appear as you type. Weather data is live from Open-Meteo.
          </Typography>
        </Box>

        {/* Search + unit selector */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <Card sx={{ border: '1px solid #e0e0e0' }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  Search Location
                </Typography>
                <LocationSearch
                  value={locationQuery}
                  onChange={setLocationQuery}
                  onSelect={handleLocationSelect}
                  label="Enter location"
                  placeholder="e.g. Sydney, Austraila"
                  disabled={loading}
                />
                {loading && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2 }}>
                    <CircularProgress size={18} />
                    <Typography variant="caption" color="text.secondary">
                      Fetching weather…
                    </Typography>
                  </Box>
                )}
                {error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card sx={{ border: '1px solid #e0e0e0' }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  Temperature Unit
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <ThermostatIcon sx={{ color: secondaryColor }} />
                  <ToggleButtonGroup
                    value={temperatureUnit}
                    exclusive
                    onChange={(_, v) => v && setTemperatureUnit(v)}
                    fullWidth
                  >
                    {['celsius', 'fahrenheit'].map((unit) => (
                      <ToggleButton
                        key={unit}
                        value={unit}
                        sx={{
                          '&.Mui-selected': {
                            backgroundColor: secondaryColor,
                            color: 'white',
                            '&:hover': { backgroundColor: secondaryColor },
                          },
                        }}
                      >
                        {unit === 'celsius' ? 'Celsius (°C)' : 'Fahrenheit (°F)'}
                      </ToggleButton>
                    ))}
                  </ToggleButtonGroup>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  Select your preferred temperature unit
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Map + weather details */}
        {selectedLocation && weatherData && (
          <>
            <Card sx={{ mb: 4, border: '1px solid #e0e0e0', overflow: 'hidden' }}>
              <Box sx={{ height: 400, width: '100%' }}>
                <MapContainer
                  key={`${selectedLocation.lat}-${selectedLocation.lon}`}
                  center={[selectedLocation.lat, selectedLocation.lon]}
                  zoom={11}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  />
                  <Marker position={[selectedLocation.lat, selectedLocation.lon]}>
                    <Popup>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {selectedLocation.short_name}
                      </Typography>
                      <Typography variant="caption">{weatherData.condition}</Typography>
                    </Popup>
                  </Marker>
                </MapContainer>
              </Box>
            </Card>

            <Card sx={{ border: '1px solid #e0e0e0' }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                  Weather for {selectedLocation.short_name}
                </Typography>

                <Grid container spacing={2}>
                  {[
                    {
                      label: 'Temperature',
                      value: convertTemperature(weatherData.temperature),
                      unit: tempSymbol,
                    },
                    { label: 'Wind Speed', value: weatherData.windSpeed, unit: 'km/h' },
                    { label: 'Condition', value: weatherData.condition, unit: '' },
                    {
                      label: 'Observed at',
                      value: weatherData.time.replace('T', ' '),
                      unit: 'UTC',
                    },
                  ].map(({ label, value, unit }) => (
                    <Grid item xs={12} sm={6} md={3} key={label}>
                      <Box
                        sx={{
                          p: 2,
                          backgroundColor: `${secondaryColor}10`,
                          borderRadius: '8px',
                          border: `1px solid ${secondaryColor}20`,
                        }}
                      >
                        <Typography variant="caption" color="text.secondary">
                          {label}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5, mt: 0.5 }}>
                          <Typography variant="h5" sx={{ fontWeight: 700, color: primaryColor }}>
                            {value}
                          </Typography>
                          {unit && (
                            <Typography variant="body2" sx={{ color: primaryColor }}>
                              {unit}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </>
        )}

        {!selectedLocation && !error && (
          <Card sx={{ border: '1px solid #e0e0e0' }}>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <CloudIcon sx={{ fontSize: 48, color: secondaryColor, mb: 2 }} />
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                Search for any location
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Start typing a city name — suggestions will appear automatically.
                Misspellings are OK; we'll find the closest match.
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>
    </Container>
  )
}
