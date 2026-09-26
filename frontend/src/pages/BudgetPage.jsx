import React from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import MoneyIcon from '@mui/icons-material/Money'
import { useCurrency } from '../context/CurrencyContext'

export default function BudgetPage() {
  const navigate = useNavigate()
  const { currency, getCurrencySymbol, getCurrencyLabel } = useCurrency()
  const primaryColor = '#1976D2'
  const secondaryColor = '#42A5F5'

  // Sample budget data
  const budgetItems = [
    { name: 'Venue', amount: 2000 },
    { name: 'Catering', amount: 1500 },
    { name: 'Decorations', amount: 500 },
    { name: 'Entertainment', amount: 800 },
    { name: 'Photography', amount: 1200 },
    { name: 'Transport', amount: 300 },
  ]

  const totalBudget = budgetItems.reduce((sum, item) => sum + item.amount, 0)
  const currencySymbol = getCurrencySymbol()

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
            <MoneyIcon sx={{ fontSize: 32, color: secondaryColor }} />
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#212121' }}>
              Budget Manager
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Track and manage your event budget with detailed cost breakdown. Currency: {getCurrencyLabel()}
          </Typography>
        </Box>

        {/* Total Budget Card */}
        <Card sx={{ mb: 4, border: `1px solid #e0e0e0`, backgroundColor: `${secondaryColor}10` }}>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: '#212121' }}>
              Total Budget
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
              <Typography variant="h3" sx={{ fontWeight: 700, color: primaryColor }}>
                {currencySymbol}
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700, color: primaryColor }}>
                {totalBudget.toLocaleString()}
              </Typography>
            </Box>
          </CardContent>
        </Card>

        {/* Budget Items Grid */}
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, color: '#212121' }}>
          Budget Breakdown
        </Typography>

        <Grid container spacing={2} sx={{ mb: 4 }}>
          {budgetItems.map((item, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card sx={{ border: `1px solid #e0e0e0` }}>
                <CardContent>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {item.name}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: primaryColor }}>
                      {currencySymbol}
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: primaryColor }}>
                      {item.amount.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box sx={{ mt: 2, height: '4px', backgroundColor: '#e0e0e0', borderRadius: '2px' }}>
                    <Box
                      sx={{
                        height: '100%',
                        width: `${(item.amount / totalBudget) * 100}%`,
                        backgroundColor: secondaryColor,
                        borderRadius: '2px',
                        transition: 'width 0.3s ease',
                      }}
                    />
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    {((item.amount / totalBudget) * 100).toFixed(1)}% of total
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Info Section */}
        <Card sx={{ border: `1px solid #e0e0e0`, backgroundColor: '#fafafa' }}>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              💡 Budget Tips
            </Typography>
            <Box component="ul" sx={{ pl: 2, mb: 0 }}>
              <Typography component="li" variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Allocate 40-50% of budget to venue and catering
              </Typography>
              <Typography component="li" variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Keep 10-15% as contingency for unexpected expenses
              </Typography>
              <Typography component="li" variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Review and adjust budget regularly as event approaches
              </Typography>
              <Typography component="li" variant="body2" color="text.secondary">
                Compare quotes from multiple vendors to get best value
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}