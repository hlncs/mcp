import React from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  ToggleButton,
  ToggleButtonGroup,
  Grid,
  Divider,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import SettingsIcon from '@mui/icons-material/Settings'
import CurrencyExchangeIcon from '@mui/icons-material/CurrencyExchange'
import { useCurrency } from '../context/CurrencyContext'

export default function SettingsPage() {
  const navigate = useNavigate()
  const primaryColor = '#1976D2'
  const secondaryColor = '#42A5F5'

  const { currency, setCurrency, currencyOptions, getCurrencyName } = useCurrency()

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
            <SettingsIcon sx={{ fontSize: 32, color: secondaryColor }} />
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#212121' }}>
              Settings
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Configure your preferences for the Event Management Suite
          </Typography>
        </Box>

        {/* Currency Settings */}
        <Card sx={{ border: `1px solid #e0e0e0` }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
              <CurrencyExchangeIcon sx={{ color: secondaryColor }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Currency Preference
              </Typography>
            </Box>

            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Select your preferred currency for budget tracking and pricing displays
            </Typography>

            <ToggleButtonGroup
              value={currency}
              exclusive
              onChange={(e, newCurrency) => {
                if (newCurrency !== null) {
                  setCurrency(newCurrency)
                }
              }}
              sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}
            >
              {currencyOptions.map((option) => (
                <ToggleButton
                  key={option.value}
                  value={option.value}
                  sx={{
                    flex: '1 1 calc(33.333% - 8px)',
                    minWidth: '140px',
                    '&.Mui-selected': {
                      backgroundColor: secondaryColor,
                      color: 'white',
                      '&:hover': {
                        backgroundColor: secondaryColor,
                      },
                    },
                    border: `1px solid #e0e0e0`,
                    borderRadius: '8px',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      borderColor: secondaryColor,
                    },
                  }}
                >
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="caption" sx={{ fontWeight: 600 }}>
                      {option.label}
                    </Typography>
                    <Typography variant="caption" display="block" sx={{ opacity: 0.7 }}>
                      {option.name}
                    </Typography>
                  </Box>
                </ToggleButton>
              ))}
            </ToggleButtonGroup>

            <Divider sx={{ my: 3 }} />

            {/* Selected Currency Display */}
            <Box sx={{ p: 2, backgroundColor: `${secondaryColor}10`, borderRadius: '8px' }}>
              <Typography variant="caption" color="text.secondary">
                Currently Selected
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: primaryColor }}>
                    {currencyOptions.find(c => c.value === currency)?.label}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {getCurrencyName()}
                  </Typography>
                </Box>
                <Typography
                  variant="h4"
                  sx={{
                    fontWeight: 700,
                    color: secondaryColor,
                    ml: 'auto',
                  }}
                >
                  {currencyOptions.find(c => c.value === currency)?.symbol}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Info Section */}
        <Card sx={{ mt: 4, border: `1px solid #e0e0e0`, backgroundColor: '#fafafa' }}>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              ℹ️ About Settings
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.8 }}>
              Your preferences are saved automatically and will be used throughout the Event Management Suite.
              Choose your preferred currency to see all prices and budgets displayed in that currency.
              You can change these settings at any time, and your preference will persist even after closing the browser.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}