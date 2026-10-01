import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Step,
  StepLabel,
  Stepper,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Autocomplete,
} from '@mui/material';
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import HotelIcon from '@mui/icons-material/Hotel';

interface CombinedBookingFormProps {
  onBookingComplete?: (flightBookingId: string, hotelBookingId: string) => void;
  apiUrl?: string;
}

interface FlightData {
  departure: string;
  arrival: string;
  date: string;
  passengers: number;
  cabin_class: 'economy' | 'business' | 'first';
  preference: 'cheapest' | 'earliest' | 'most_luxury' | 'shortest';
  auto_approve: boolean;
}

interface HotelData {
  location: string;
  check_in: string;
  check_out: string;
  guests: number;
  preference: 'cheapest' | 'earliest' | 'most_luxury';
  auto_approve: boolean;
  flight_booking_id?: string;
}

const STEPS = ['Flight Details', 'Hotel Details', 'Review & Confirm'];

// TabPanel component for stepper steps
interface TabPanelProps {
  children?: React.ReactNode
  value: number
  index: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box>{children}</Box>}
  </div>
)

const CombinedBookingForm: React.FC<CombinedBookingFormProps> = ({
  onBookingComplete,
  apiUrl = 'http://localhost:8000',
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [flightBookingId, setFlightBookingId] = useState<string | null>(null);
  const [hotelBookingId, setHotelBookingId] = useState<string | null>(null);

  const [flightData, setFlightData] = useState<FlightData>({
    departure: '',
    arrival: '',
    date: '',
    passengers: 1,
    cabin_class: 'economy',
    preference: 'cheapest',
    auto_approve: false,
  });

  const [hotelData, setHotelData] = useState<HotelData>({
    location: '',
    check_in: '',
    check_out: '',
    guests: 1,
    preference: 'cheapest',
    auto_approve: false,
  });

  // Location suggestions state
  const [departureOptions, setDepartureOptions] = useState<any[]>([]);
  const [arrivalOptions, setArrivalOptions] = useState<any[]>([]);
  const [hotelLocationOptions, setHotelLocationOptions] = useState<any[]>([]);
  const [loadingDeparture, setLoadingDeparture] = useState(false);
  const [loadingArrival, setLoadingArrival] = useState(false);
  const [loadingHotelLocation, setLoadingHotelLocation] = useState(false);

  const handleFlightChange = (field: keyof FlightData, value: any) => {
    setFlightData((prev) => ({ ...prev, [field]: value }));
  };

  const handleHotelChange = (field: keyof HotelData, value: any) => {
    setHotelData((prev) => ({ ...prev, [field]: value }));
  };

  const validateFlightData = (): boolean => {
    if (!flightData.departure.trim()) {
      setError('Departure city is required');
      return false;
    }
    if (!flightData.arrival.trim()) {
      setError('Arrival city is required');
      return false;
    }
    if (!flightData.date) {
      setError('Flight date is required');
      return false;
    }
    return true;
  };

  const validateHotelData = (): boolean => {
    if (!hotelData.location.trim()) {
      setError('Hotel location is required');
      return false;
    }
    if (!hotelData.check_in) {
      setError('Check-in date is required');
      return false;
    }
    if (!hotelData.check_out) {
      setError('Check-out date is required');
      return false;
    }
    if (new Date(hotelData.check_out) <= new Date(hotelData.check_in)) {
      setError('Check-out date must be after check-in date');
      return false;
    }
    return true;
  };

  const bookFlight = async (): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/mcp/tools/offer_flight`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(flightData),
      });
      if (!response.ok) throw new Error('Flight booking failed');
      const result = await response.json();
      setFlightBookingId(result.booking_id);
      setSuccessMessage(`Flight booking created: ${result.message}`);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to book flight');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const bookHotel = async (): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const hotelPayload = {
        ...hotelData,
        flight_booking_id: flightBookingId || undefined,
      };
      const response = await fetch(`${apiUrl}/mcp/tools/offer_hotel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(hotelPayload),
      });
      if (!response.ok) throw new Error('Hotel booking failed');
      const result = await response.json();
      setHotelBookingId(result.booking_id);
      setSuccessMessage(`Hotel booking created: ${result.message}`);
      if (result.location_warning) setError(result.location_warning);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to book hotel');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    setError(null);
    if (activeStep === 0) {
      if (!validateFlightData()) return;
      const success = await bookFlight();
      if (success) setActiveStep(1);
    } else if (activeStep === 1) {
      if (!validateHotelData()) return;
      const success = await bookHotel();
      if (success) {
        setActiveStep(2);
        if (onBookingComplete && flightBookingId && hotelBookingId) {
          onBookingComplete(flightBookingId, hotelBookingId);
        }
      }
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => Math.max(prev - 1, 0));
  };

  const handleReset = () => {
    setActiveStep(0);
    setFlightData({
      departure: '',
      arrival: '',
      date: '',
      passengers: 1,
      cabin_class: 'economy',
      preference: 'cheapest',
      auto_approve: false,
    });
    setHotelData({
      location: '',
      check_in: '',
      check_out: '',
      guests: 1,
      preference: 'cheapest',
      auto_approve: false,
    });
    setFlightBookingId(null);
    setHotelBookingId(null);
    setError(null);
    setSuccessMessage(null);
  };

  // Location search functions
    const searchLocations = async (query: string, setOptions: any, setLoading: any) => {
    if (!query || query.length < 2) {
      setOptions([]);
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/location/search?q=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        console.log('Location search response:', data);
        // Handle different response formats
        const results = data.suggestions || data.results || data.data || [];
        setOptions(Array.isArray(results) ? results : []);
      }
    } catch (err) {
      console.error('Location search error:', err);
      setOptions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDepartureSearch = (query: string) => {
    searchLocations(query, setDepartureOptions, setLoadingDeparture);
  };

  const handleArrivalSearch = (query: string) => {
    searchLocations(query, setArrivalOptions, setLoadingArrival);
  };

  const handleHotelLocationSearch = (query: string) => {
    searchLocations(query, setHotelLocationOptions, setLoadingHotelLocation);
  };

  return (
    <Card sx={{ maxWidth: 800, margin: 'auto', mt: 4, mb: 4 }}>
      <CardHeader
        title="Combined Flight & Hotel Booking"
        subheader="Book your flight and hotel together"
      />
      <Divider />
      <CardContent>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {STEPS.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {successMessage && <Alert severity="success" sx={{ mb: 2 }}>{successMessage}</Alert>}

        {activeStep === 0 && (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <FlightTakeoffIcon sx={{ mr: 2 }} />
              <Typography variant="h6">Flight Details</Typography>
            </Box>
            <Grid container spacing={2}>
                            <Grid item xs={12} sm={6}>
                <Autocomplete
                  freeSolo
                  options={departureOptions.map((opt: any) => opt.display_name || opt.name)}
                  loading={loadingDeparture}
                  onInputChange={(_, value) => {
                    handleFlightChange('departure', value);
                    handleDepartureSearch(value);
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Departure City"
                      placeholder="Search city, airport..."
                      InputProps={{
                        ...params.InputProps,
                        endAdornment: (
                          <>
                            {loadingDeparture ? <CircularProgress color="inherit" size={20} /> : null}
                            {params.InputProps.endAdornment}
                          </>
                        ),
                      }}
                    />
                  )}
                />
              </Grid>
                            <Grid item xs={12} sm={6}>
                <Autocomplete
                  freeSolo
                  options={arrivalOptions.map((opt: any) => opt.display_name || opt.name)}
                  loading={loadingArrival}
                  onInputChange={(_, value) => {
                    handleFlightChange('arrival', value);
                    handleArrivalSearch(value);
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Arrival City"
                      placeholder="Search city, airport..."
                      InputProps={{
                        ...params.InputProps,
                        endAdornment: (
                          <>
                            {loadingArrival ? <CircularProgress color="inherit" size={20} /> : null}
                            {params.InputProps.endAdornment}
                          </>
                        ),
                      }}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Date"
                  value={flightData.date}
                  onChange={(e) => handleFlightChange('date', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Passengers"
                  value={flightData.passengers}
                  onChange={(e) => handleFlightChange('passengers', parseInt(e.target.value) || 1)}
                  inputProps={{ min: 1 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Cabin</InputLabel>
                  <Select
                    value={flightData.cabin_class}
                    onChange={(e) => handleFlightChange('cabin_class', e.target.value)}
                    label="Cabin"
                  >
                    <MenuItem value="economy">Economy</MenuItem>
                    <MenuItem value="business">Business</MenuItem>
                    <MenuItem value="first">First</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Preference</InputLabel>
                  <Select
                    value={flightData.preference}
                    onChange={(e) => handleFlightChange('preference', e.target.value)}
                    label="Preference"
                  >
                    <MenuItem value="cheapest">Cheapest</MenuItem>
                    <MenuItem value="earliest">Earliest</MenuItem>
                    <MenuItem value="most_luxury">Most Luxury</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        )}

        {activeStep === 1 && (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <HotelIcon sx={{ mr: 2 }} />
              <Typography variant="h6">Hotel Details</Typography>
            </Box>
            
                        <Alert severity="info" sx={{ mb: 2 }}>
              Hotel location must match flight destination: {flightData.arrival}
            </Alert>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Autocomplete
                  freeSolo
                  options={hotelLocationOptions.map((opt: any) => opt.display_name || opt.name)}
                  loading={loadingHotelLocation}
                  onInputChange={(_, value) => {
                    handleHotelChange('location', value);
                    handleHotelLocationSearch(value);
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Hotel Location"
                      placeholder="Search city, venue, address..."
                      helperText="Should match flight destination"
                      InputProps={{
                        ...params.InputProps,
                        endAdornment: (
                          <>
                            {loadingHotelLocation ? <CircularProgress color="inherit" size={20} /> : null}
                            {params.InputProps.endAdornment}
                          </>
                        ),
                      }}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Guests"
                  value={hotelData.guests}
                  onChange={(e) => handleHotelChange('guests', parseInt(e.target.value) || 1)}
                  inputProps={{ min: 1 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Check-In"
                  value={hotelData.check_in}
                  onChange={(e) => handleHotelChange('check_in', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Check-Out"
                  value={hotelData.check_out}
                  onChange={(e) => handleHotelChange('check_out', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Preference</InputLabel>
                  <Select
                    value={hotelData.preference}
                    onChange={(e) => handleHotelChange('preference', e.target.value)}
                    label="Preference"
                  >
                    <MenuItem value="cheapest">Cheapest</MenuItem>
                    <MenuItem value="earliest">Earliest</MenuItem>
                    <MenuItem value="most_luxury">Most Luxury</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

          </Box>
        )}

        {activeStep === 2 && (
          <Box>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Booking Complete!
            </Typography>
            <Card sx={{ mb: 2, bgcolor: '#f5f5f5' }}>
              <CardContent>
                <Typography variant="subtitle1">Flight Booking ID: {flightBookingId}</Typography>
                <Typography variant="body2">{flightData.departure} to {flightData.arrival} on {flightData.date}</Typography>
              </CardContent>
            </Card>
            <Card sx={{ mb: 2, bgcolor: '#f5f5f5' }}>
              <CardContent>
                <Typography variant="subtitle1">Hotel Booking ID: {hotelBookingId}</Typography>
                <Typography variant="body2">{hotelData.location} ({hotelData.check_in} to {hotelData.check_out})</Typography>
              </CardContent>
            </Card>
          </Box>
        )}

        <Divider sx={{ my: 3 }} />

        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button disabled={activeStep === 0 || loading} onClick={handleBack}>
            Back
          </Button>
          {activeStep === 2 ? (
            <Button variant="contained" onClick={handleReset} disabled={loading}>
              Start Over
            </Button>
          ) : (
            <Button variant="contained" onClick={handleNext} disabled={loading}>
              {loading ? <CircularProgress size={20} sx={{ mr: 1 }} /> : null}
              {activeStep === 1 ? 'Complete' : 'Next'}
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default CombinedBookingForm;
