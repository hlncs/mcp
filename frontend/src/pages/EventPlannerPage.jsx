import React, { useState, useEffect } from 'react'
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
  LinearProgress,
} from '@mui/material'
import { apiClient } from '../api/client'
import { useCurrency } from '../context/CurrencyContext'

export default function EventPlannerPage() {
  const [formData, setFormData] = useState({
    query: '',
    event_date: '',
    event_location: '',
    num_people: '',
    budget: '',
  })
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [plans, setPlans] = useState([])
  const [refreshInterval, setRefreshInterval] = useState(null)

  const { getCurrencySymbol } = useCurrency()

  useEffect(() => {
    fetchPlans()
  }, [])

  // Auto-refresh plan status when processing
  useEffect(() => {
    if (plan && plan.status === 'processing') {
      const interval = setInterval(() => {
        refreshPlanStatus()
      }, 2000)
      
      setRefreshInterval(interval)
      return () => clearInterval(interval)
    } else if (refreshInterval) {
      clearInterval(refreshInterval)
      setRefreshInterval(null)
    }
  }, [plan])

  const fetchPlans = async () => {
    try {
      setLoading(true)
      const response = await apiClient.listPlans()
      const plansData = response.data.plans || []
      
      // Ensure all plans have required fields
      const validatedPlans = plansData.map(p => ({
        ...p,
        query: p.query || 'Untitled Plan',
        event_date: p.event_date || 'N/A',
        event_location: p.event_location || 'N/A',
        num_people: p.num_people || 0,
        budget: p.budget || 0,
        status: p.status || 'unknown',
        progress: p.progress || 0,
        created_at: p.created_at || new Date().toISOString(),
        updated_at: p.updated_at || new Date().toISOString(),
      }))
      
      setPlans(validatedPlans)
      setError(null)
    } catch (err) {
      console.error('Error fetching plans:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const refreshPlanStatus = async () => {
    if (!plan) return
    
    try {
      const response = await apiClient.getPlan(plan.plan_id)
      const updatedPlan = {
        ...response.data,
        query: response.data.query || 'Untitled Plan',
        event_date: response.data.event_date || 'N/A',
        event_location: response.data.event_location || 'N/A',
        num_people: response.data.num_people || 0,
        budget: response.data.budget || 0,
        status: response.data.status || 'unknown',
        progress: response.data.progress || 0,
      }
      
      setPlan(updatedPlan)
      
      // Update in plans list too
      setPlans(plans.map(p => 
        p.plan_id === plan.plan_id ? updatedPlan : p
      ))
    } catch (err) {
      console.error('Error refreshing plan:', err)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!formData.query.trim()) {
      setError('Please describe your event')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // Pass event details as third parameter
      const response = await apiClient.createPlan(
        formData.query,
        {},
        {
          event_date: formData.event_date,
          event_location: formData.event_location,
          num_people: parseInt(formData.num_people) || 0,
          budget: parseFloat(formData.budget) || 0,
        }
      )

      const newPlan = {
        ...response.data,
        event_date: formData.event_date,
        event_location: formData.event_location,
        num_people: parseInt(formData.num_people) || 0,
        budget: parseFloat(formData.budget) || 0,
        status: response.data.status || 'unknown',
        progress: response.data.progress || 0,
        result: response.data.result || {},
      }

      setPlans([newPlan, ...plans])
      setPlan(newPlan)
      setFormData({
        query: '',
        event_date: '',
        event_location: '',
        num_people: '',
        budget: '',
      })
    } catch (err) {
      console.error('Error creating plan:', err)
      setError(err.message || 'Failed to create plan')
    } finally {
      setLoading(false)
    }
  }

  const handleViewPlan = async (planId) => {
    try {
      setLoading(true)
      const response = await apiClient.getPlan(planId)
      const viewPlan = {
        ...response.data,
        query: response.data.query || 'Untitled Plan',
        event_date: response.data.event_date || 'N/A',
        event_location: response.data.event_location || 'N/A',
        num_people: response.data.num_people || 0,
        budget: response.data.budget || 0,
        status: response.data.status || 'unknown',
        progress: response.data.progress || 0,
      }
      setPlan(viewPlan)
      window.scrollTo(0, 0)
    } catch (err) {
      console.error('Error fetching plan:', err)
      setError(err.message || 'Failed to fetch plan')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    try {
      if (!dateString || dateString === 'N/A') return dateString
      return new Date(dateString).toLocaleString()
    } catch {
      return dateString || 'N/A'
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount || 0)
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'processing':
        return 'orange'
      case 'completed':
        return 'green'
      case 'failed':
        return 'red'
      default:
        return 'gray'
    }
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Event Planner
        </Typography>

        <Grid container spacing={3}>
          {/* Form Section */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Create Event Plan
                </Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                  <TextField
                    fullWidth
                    label="Event Description"
                    name="query"
                    value={formData.query}
                    onChange={handleChange}
                    margin="normal"
                    placeholder="e.g., Birthday party, Wedding, Corporate event"
                    multiline
                    rows={3}
                    required
                  />

                  <TextField
                    fullWidth
                    label="Event Date"
                    name="event_date"
                    type="date"
                    value={formData.event_date}
                    onChange={handleChange}
                    margin="normal"
                    InputLabelProps={{ shrink: true }}
                  />

                  <TextField
                    fullWidth
                    label="Event Location"
                    name="event_location"
                    value={formData.event_location}
                    onChange={handleChange}
                    margin="normal"
                    placeholder="e.g., Downtown Hotel, Community Center"
                  />

                  <TextField
                    fullWidth
                    label="Number of Guests"
                    name="num_people"
                    type="number"
                    value={formData.num_people}
                    onChange={handleChange}
                    margin="normal"
                    placeholder="e.g., 50"
                    inputProps={{ min: '0' }}
                  />

                  <TextField
                    fullWidth
                    label="Budget ($)"
                    name="budget"
                    type="number"
                    value={formData.budget}
                    onChange={handleChange}
                    margin="normal"
                    placeholder="e.g., 5000"
                    inputProps={{ min: '0', step: '0.01' }}
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

          {/* Plan Display Section */}
          <Grid item xs={12} md={6}>
            {error && <Alert severity="error">{error}</Alert>}

            {plan && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Plan Details
                  </Typography>
                  
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Plan ID:</strong> {plan.plan_id}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Event:</strong> {plan.query || 'N/A'}
                    </Typography>

                    <Box sx={{ mt: 2, p: 1.5, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>📅 Date:</strong> {plan.event_date || 'TBD'}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>📍 Location:</strong> {plan.event_location || 'TBD'}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>👥 Guests:</strong> {plan.num_people || 0} people
                      </Typography>
                      <Typography variant="body2">
                        <strong>💰 Budget:</strong> {formatCurrency(plan.budget)}
                      </Typography>
                    </Box>
                    
                    {/* Status with color */}
                    <Typography variant="body2" sx={{ mb: 1, mt: 2 }}>
                      <strong>Status:</strong>{' '}
                      <span style={{ 
                        color: getStatusColor(plan.status),
                        fontWeight: 'bold',
                        textTransform: 'uppercase'
                      }}>
                        {plan.status}
                      </span>
                    </Typography>

                    {/* Progress bar */}
                    <Box sx={{ mt: 2, mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">
                          <strong>Progress:</strong>
                        </Typography>
                        <Typography variant="body2">
                          {plan.progress || 0}%
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={plan.progress || 0}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>

                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Created:</strong> {formatDate(plan.created_at)}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Updated:</strong> {formatDate(plan.updated_at)}
                    </Typography>

                    {/* Results when completed */}
                    {plan.result && Object.keys(plan.result).length > 0 && (
                      <>
                        <Typography variant="body2" sx={{ mt: 2, fontWeight: 'bold' }}>
                          Results:
                        </Typography>
                        <Box sx={{ ml: 2, mt: 1 }}>
                          <pre style={{ 
                            fontSize: '12px', 
                            backgroundColor: '#f5f5f5', 
                            padding: '8px',
                            borderRadius: '4px',
                            maxHeight: '200px',
                            overflow: 'auto'
                          }}>
                            {JSON.stringify(plan.result, null, 2)}
                          </pre>
                        </Box>
                      </>
                    )}

                    {/* Loading indicator when processing */}
                    {plan.status === 'processing' && (
                      <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CircularProgress size={20} />
                        <Typography variant="body2" color="text.secondary">
                          Processing your plan...
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>

        {/* Budget Display */}
        <Box sx={{ mt: 2, p: 2, backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
          <Typography variant="caption" color="text.secondary">
            Budget
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: '#333' }}>
              {getCurrencySymbol()}
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#333' }}>
              {parseFloat(formData.budget || 0).toLocaleString()}
            </Typography>
          </Box>
        </Box>

        {/* All Plans Section */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            All Plans ({plans.length})
          </Typography>

          {plans.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No plans found. Create a new plan to get started.
            </Typography>
          ) : (
            <Grid container spacing={3}>
              {plans.map((p) => (
                <Grid item xs={12} sm={6} md={4} key={p.plan_id}>
                  <Card sx={{ 
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      boxShadow: 4,
                      transform: 'translateY(-4px)'
                    }
                  }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {(p.query || 'Untitled Plan').substring(0, 30)}
                        {(p.query || '').length > 30 ? '...' : ''}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(p.created_at)}
                      </Typography>
                      
                      <Box sx={{ my: 1, p: 1, backgroundColor: '#f9f9f9', borderRadius: 0.5 }}>
                        <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                          📅 {p.event_date || 'N/A'}
                        </Typography>
                        <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                          📍 {p.event_location || 'N/A'}
                        </Typography>
                        <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                          👥 {p.num_people} guests
                        </Typography>
                        <Typography variant="caption" sx={{ display: 'block' }}>
                          💰 {formatCurrency(p.budget)}
                        </Typography>
                      </Box>

                      <Typography variant="body2" sx={{ mt: 1 }}>
                        <strong>Status:</strong>{' '}
                        <span style={{ 
                          color: getStatusColor(p.status),
                          fontWeight: 'bold'
                        }}>
                          {p.status}
                        </span>
                      </Typography>
                      
                      <Box sx={{ mt: 1, mb: 1 }}>
                        <Typography variant="body2" sx={{ mb: 0.5 }}>
                          <strong>Progress:</strong> {p.progress || 0}%
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={p.progress || 0}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>

                      <Button
                        fullWidth
                        size="small"
                        color="primary"
                        onClick={() => handleViewPlan(p.plan_id)}
                        sx={{ mt: 2 }}
                      >
                        View Details
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </Box>
    </Container>
  )
}