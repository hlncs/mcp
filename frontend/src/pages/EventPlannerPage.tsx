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
  Tabs,
  Tab,
} from '@mui/material'
import { apiClient } from '../api/client'
import { useCurrency } from '../context/CurrencyContext'
import LocationSearch from '../components/LocationSearch'
import CombinedBookingForm from '../components/CombinedBookingForm'
import BookingManager from '../components/BookingManager'
import PlanDetails from '../components/PlanDetails'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box>{children}</Box>}
  </div>
)

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
  const [tabValue, setTabValue] = useState(0)

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
      const validatedPlans = plansData.map((p) => ({
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
      setPlans(
        plans.map((p) => (p.plan_id === plan.plan_id ? updatedPlan : p))
      )
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

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const handleBookingComplete = (flightId: string, hotelId: string) => {
    console.log('Bookings complete:', { flightId, hotelId })
    // Switch to booking manager tab to show results
    setTabValue(1)
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Event Planner
        </Typography>

        <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
          <Tab label="📋 Create Booking" />
          <Tab label="📦 Booking Manager" />
          <Tab label="📅 Plan Details" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <CombinedBookingForm onBookingComplete={handleBookingComplete} />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <BookingManager />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <PlanDetails />
        </TabPanel>
      </Box>
    </Container>
  )
}