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
  LinearProgress,
} from '@mui/material'
import AttachMoneyIcon from '@mui/icons-material/AttachMoney'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export default function BudgetPage() {
  const [allocatedBudget, setAllocatedBudget] = useState('')
  const [calculatedCost, setCalculatedCost] = useState('')
  const [validation, setValidation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_BASE_URL}/budget/validate`, {
        allocated_budget: parseFloat(allocatedBudget),
        calculated_cost: parseFloat(calculatedCost),
      })
      setValidation(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to validate budget')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Budget Manager
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box component="form" onSubmit={handleSubmit}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Allocated Budget (USD)"
                    value={allocatedBudget}
                    onChange={(e) => setAllocatedBudget(e.target.value)}
                    margin="normal"
                    required
                  />
                  <TextField
                    fullWidth
                    type="number"
                    label="Calculated Cost (USD)"
                    value={calculatedCost}
                    onChange={(e) => setCalculatedCost(e.target.value)}
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
                    {loading ? <CircularProgress size={24} /> : 'Validate Budget'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            {error && <Alert severity="error">{error}</Alert>}

            {validation && (
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <AttachMoneyIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                    <Typography variant="h6">Budget Analysis</Typography>
                  </Box>

                  <Typography variant="body2">
                    <strong>Allocated Budget:</strong> ${validation.allocated_budget?.toFixed(2)}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Calculated Cost:</strong> ${validation.calculated_cost?.toFixed(2)}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Remaining:</strong> ${validation.remaining?.toFixed(2)}
                  </Typography>

                  <Box sx={{ mt: 3 }}>
                    <Typography variant="body2" gutterBottom>
                      <strong>Budget Usage: {validation.percentage_used?.toFixed(1)}%</strong>
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min(validation.percentage_used, 100)}
                      sx={{
                        backgroundColor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor:
                            validation.status === 'within_budget' ? '#4caf50' : '#f44336',
                        },
                      }}
                    />
                  </Box>

                  {validation.warning && (
                    <Alert severity="warning" sx={{ mt: 2 }}>
                      {validation.warning}
                    </Alert>
                  )}

                  <Typography
                    variant="body2"
                    sx={{
                      mt: 2,
                      color: validation.status === 'within_budget' ? 'green' : 'red',
                      fontWeight: 'bold',
                    }}
                  >
                    Status: {validation.status === 'within_budget' ? '✅ Within Budget' : '❌ Over Budget'}
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