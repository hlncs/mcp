import React from 'react'
import { Box, Typography, Card, CardContent, Alert } from '@mui/material'

export default function BookingManager() {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Booking Manager
      </Typography>
      <Alert severity="info">
        Your flight and hotel bookings will appear here once confirmed.
      </Alert>
      <Box sx={{ mt: 2 }}>
        <Card>
          <CardContent>
            <Typography color="textSecondary">
              No active bookings yet. Create a new booking in the "Create Booking" tab.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Box>
  )
}