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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const serviceTypes = ['hotels', 'flights', 'venues', 'catering', 'entertainment', 'transportation']

export default function ServiceSearchPage() {
  const [serviceType, setServiceType] = useState('hotels')
  const [location, setLocation] = useState('')
  const [services, setServices] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(
        `${API_BASE_URL}/search/services`,
        null,
        {
          params: {
            service_type: serviceType,
            location,
          },
        }
      )
      setServices(response.data.results)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to search services')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const renderServiceTable = () => {
    if (!services || services.length === 0) return null

    const columns = Object.keys(services[0]).slice(0, 5)

    return (
      <TableContainer component={Paper} sx={{ mt: 3 }}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
              {columns.map((col) => (
                <TableCell key={col} sx={{ fontWeight: 'bold' }}>
                  {col.replace(/_/g, ' ').toUpperCase()}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {services.map((service, index) => (
              <TableRow key={index}>
                {columns.map((col) => (
                  <TableCell key={`${index}-${col}`}>
                    {typeof service[col] === 'object'
                      ? JSON.stringify(service[col]).slice(0, 30)
                      : String(service[col]).slice(0, 50)}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    )
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Service Search
        </Typography>

        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box component="form" onSubmit={handleSubmit}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Service Type</InputLabel>
                    <Select
                      value={serviceType}
                      label="Service Type"
                      onChange={(e) => setServiceType(e.target.value)}
                    >
                      {serviceTypes.map((type) => (
                        <MenuItem key={type} value={type}>
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Location"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g., Sydney, Australia"
                    required
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="contained"
                    color="primary"
                    type="submit"
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Search Services'}
                  </Button>
                </Grid>
              </Grid>
            </Box>
          </CardContent>
        </Card>

        {error && <Alert severity="error">{error}</Alert>}

        {services.length > 0 && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Found {services.length} {serviceType}
              </Typography>
              {renderServiceTable()}
            </CardContent>
          </Card>
        )}
      </Box>
    </Container>
  )
}