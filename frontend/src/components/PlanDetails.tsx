/**
 * Plan Details Component - Display event plan details, location geocoding & live weather
 * Location: frontend/src/components/PlanDetails.tsx
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Chip,
  Stack,
  Grid,
  Paper,
  Divider,
  Autocomplete,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import WbSunnyIcon from '@mui/icons-material/WbSunny';
import AirIcon from '@mui/icons-material/Air';
import LocationOnIcon from '@mui/icons-material/LocationOn';

interface PlanDetailsProps {
  planId?: string | null;
  selectedPlanId?: string | null;
}

interface WeatherInfo {
  location: string;
  latitude: number;
  longitude: number;
  is_fuzzy_suggestion?: boolean;
  current: {
    temperature: number;
    windspeed: number;
    weathercode: number;
    time: string;
  };
  forecast: Array<{
    date: string;
    temp_max: number;
    temp_min: number;
    precipitation_mm: number;
    weathercode: number;
  }>;
}

interface LocationOption {
  display_name: string;
  name: string;
  latitude: number;
  longitude: number;
  country?: string;
  city?: string;
}

const PlanDetails: React.FC<PlanDetailsProps> = ({ planId: propPlanId, selectedPlanId }) => {
  const activePlanId = propPlanId || selectedPlanId;

  const [plan, setPlan] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedPlan, setEditedPlan] = useState<any | null>(null);
  const [saving, setSaving] = useState(false);

  // Weather state
  const [weather, setWeather] = useState<WeatherInfo | null>(null);
  const [loadingWeather, setLoadingWeather] = useState(false);
  const [weatherError, setWeatherError] = useState<string | null>(null);

  // Location suggestions state
  const [locationOptions, setLocationOptions] = useState<LocationOption[]>([]);
  const [loadingLocations, setLoadingLocations] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Fetch plan details
  useEffect(() => {
    if (!activePlanId) {
      setPlan(null);
      setLoading(false);
      return;
    }

    let isMounted = true;

    const fetchPlanDetails = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${API_URL}/plan/${activePlanId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        const data = await response.json();
        if (isMounted) {
          setPlan(data);
          if (data.event_location) {
            fetchWeather(data.event_location);
          }
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Error fetching plan details');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchPlanDetails();

    return () => {
      isMounted = false;
    };
  }, [activePlanId, API_URL]);

  // Fetch live weather from API
  const fetchWeather = async (locationQuery: string) => {
    if (!locationQuery) return;
    setLoadingWeather(true);
    setWeatherError(null);

    try {
      const response = await fetch(`${API_URL}/weather?location=${encodeURIComponent(locationQuery)}`);
      if (!response.ok) throw new Error('Could not retrieve weather forecast');
      const data = await response.json();
      setWeather(data);
    } catch (err) {
      setWeatherError(err instanceof Error ? err.message : 'Weather fetch error');
      setWeather(null);
    } finally {
      setLoadingWeather(false);
    }
  };

  // Location search suggestions (OpenStreetMap Nominatim API via backend)
  const handleLocationSearch = async (query: string) => {
    if (!query || query.length < 2) return;
    setLoadingLocations(true);
    try {
      const response = await fetch(`${API_URL}/locations/search?query=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        setLocationOptions(data.results || []);
      }
    } catch (err) {
      console.error('Location search error:', err);
    } finally {
      setLoadingLocations(false);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
    setEditedPlan({ ...plan });
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedPlan(plan);
  };

  const handleSave = async () => {
    if (!activePlanId || !editedPlan) return;

    setSaving(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/plan/${activePlanId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editedPlan),
      });

      if (!response.ok) throw new Error(`Failed to update plan: ${response.statusText}`);

      const result = await response.json();
      setPlan(result.plan || editedPlan);
      setIsEditing(false);
      if (editedPlan.event_location) {
        fetchWeather(editedPlan.event_location);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error saving plan');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!activePlanId) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          Plan Details
        </Typography>
        <Alert severity="info">
          Event planning details will be displayed here.
        </Alert>
        <Box sx={{ mt: 2 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary">
                No plan selected yet. Create a new plan to see details here.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>
    );
  }

  if (!plan) {
    return <Alert severity="warning">{error || 'No plan details found.'}</Alert>;
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {error && <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>}

      <Card>
        <CardHeader
          title={`📋 ${plan.event_name || 'Event Plan'}`}
          subheader={`Plan ID: ${plan.plan_id}`}
          action={
            !isEditing ? (
              <Button startIcon={<EditIcon />} onClick={handleEdit} variant="outlined">
                Edit
              </Button>
            ) : null
          }
        />
        <CardContent>
          {!isEditing ? (
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="textSecondary">Event Name</Typography>
                <Typography variant="h6">{plan.event_name}</Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="textSecondary">Location</Typography>
                <Typography variant="h6">📍 {plan.event_location}</Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="textSecondary">Event Date</Typography>
                <Typography variant="h6">📅 {plan.event_date || 'N/A'}</Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="textSecondary">People & Budget</Typography>
                <Typography variant="h6">👥 {plan.num_people || 0} | 💰 ${plan.budget || 0}</Typography>
              </Grid>
            </Grid>
          ) : (
            <Stack spacing={2}>
              <TextField
                label="Event Name"
                value={editedPlan?.event_name || ''}
                onChange={(e) => setEditedPlan({ ...editedPlan, event_name: e.target.value })}
                fullWidth
              />

              <Autocomplete
                freeSolo
                options={locationOptions}
                getOptionLabel={(option) => (typeof option === 'string' ? option : option.display_name)}
                onInputChange={(_, value) => {
                  setEditedPlan({ ...editedPlan, event_location: value });
                  handleLocationSearch(value);
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Event Location (with auto-suggestions)"
                    placeholder="Search city, venue, or address..."
                    InputProps={{
                      ...params.InputProps,
                      endAdornment: (
                        <>
                          {loadingLocations ? <CircularProgress color="inherit" size={20} /> : null}
                          {params.InputProps.endAdornment}
                        </>
                      ),
                    }}
                  />
                )}
              />

              <Stack direction="row" spacing={1}>
                <Button variant="contained" color="success" startIcon={<SaveIcon />} onClick={handleSave} disabled={saving}>
                  {saving ? 'Saving...' : 'Save Changes'}
                </Button>
                <Button variant="outlined" startIcon={<CancelIcon />} onClick={handleCancelEdit} disabled={saving}>
                  Cancel
                </Button>
              </Stack>
            </Stack>
          )}
        </CardContent>
      </Card>

      {/* Weather Forecast Widget */}
      <Card>
        <CardHeader
          avatar={<WbSunnyIcon sx={{ color: '#f57c00' }} />}
          title={`🌤️ Live Weather Forecast for ${plan.event_location || 'Selected Location'}`}
          subheader="Powered by OpenStreetMap Geocoding & Open-Meteo"
        />
        <CardContent>
          {loadingWeather ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress size={30} />
            </Box>
          ) : weatherError ? (
            <Alert severity="warning">{weatherError}</Alert>
          ) : weather ? (
            <Stack spacing={2}>
              {weather.is_fuzzy_suggestion && (
                <Alert severity="info">
                  Showing corrected location result for: <strong>{weather.location}</strong>
                </Alert>
              )}

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, p: 2, bgcolor: '#e3f2fd', borderRadius: 2 }}>
                <Box>
                  <Typography variant="caption" color="textSecondary">Current Temp</Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#0288d1' }}>
                    {weather.current.temperature}°C
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="textSecondary">Wind Speed</Typography>
                  <Typography variant="body1" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <AirIcon fontSize="small" /> {weather.current.windspeed} km/h
                  </Typography>
                </Box>
                <Box sx={{ ml: 'auto' }}>
                  <Typography variant="caption" color="textSecondary">Coordinates</Typography>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    <LocationOnIcon fontSize="small" /> {weather.latitude.toFixed(2)}, {weather.longitude.toFixed(2)}
                  </Typography>
                </Box>
              </Box>

              <Divider />
              <Typography variant="subtitle2">7-Day Forecast</Typography>

              <Grid container spacing={1}>
                {weather.forecast.map((day) => (
                  <Grid item xs={6} sm={4} md={2.4} key={day.date}>
                    <Paper variant="outlined" sx={{ p: 1.5, textAlign: 'center' }}>
                      <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                        {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'numeric', day: 'numeric' })}
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#d32f2f', mt: 0.5 }}>
                        High: {day.temp_max}°C
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#1976d2' }}>
                        Low: {day.temp_min}°C
                      </Typography>
                      <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mt: 0.5 }}>
                        💧 {day.precipitation_mm} mm
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Stack>
          ) : (
            <Alert severity="info">No weather data available for this location.</Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default PlanDetails;