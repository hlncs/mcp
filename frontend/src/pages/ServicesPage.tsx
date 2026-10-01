import React from 'react'
import { Container, Box, Card, CardContent, Typography, Button } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'

export default function ServicesPage() {
  const navigate = useNavigate()

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/')}
          sx={{ mb: 3 }}
        >
          Back to Home
        </Button>

        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
          Services
        </Typography>

        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Services & Vendors Coming Soon
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Browse and manage vendors and services for your event.
            </Typography>
            <Typography variant="body2" sx={{ mt: 2 }}>
              Features:
            </Typography>
            <Box component="ul" sx={{ pl: 2 }}>
              <Typography component="li" variant="body2">
                Vendor directory
              </Typography>
              <Typography component="li" variant="body2">
                Service comparison
              </Typography>
              <Typography component="li" variant="body2">
                Booking management
              </Typography>
              <Typography component="li" variant="body2">
                Contract tracking
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}