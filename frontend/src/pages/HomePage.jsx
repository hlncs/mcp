import React from 'react'
import {
  Container,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import EventIcon from '@mui/icons-material/Event'
import CloudIcon from '@mui/icons-material/Cloud'
import AttachMoneyIcon from '@mui/icons-material/AttachMoney'
import SearchIcon from '@mui/icons-material/Search'

const features = [
  {
    title: 'Event Planner',
    description: 'Create comprehensive event plans with AI assistance',
    icon: <EventIcon sx={{ fontSize: 40 }} />,
    path: '/planner',
  },
  {
    title: 'Weather Check',
    description: 'Check weather forecasts for your event location',
    icon: <CloudIcon sx={{ fontSize: 40 }} />,
    path: '/weather',
  },
  {
    title: 'Budget Manager',
    description: 'Track and validate your event budget',
    icon: <AttachMoneyIcon sx={{ fontSize: 40 }} />,
    path: '/budget',
  },
  {
    title: 'Service Search',
    description: 'Search hotels, venues, catering, and more',
    icon: <SearchIcon sx={{ fontSize: 40 }} />,
    path: '/services',
  },
]

export default function HomePage() {
  const navigate = useNavigate()

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 8 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Welcome to Event Planning System
        </Typography>
        <Typography
          variant="h6"
          align="center"
          color="textSecondary"
          sx={{ mb: 4 }}
        >
          AI-powered event planning with multi-agent orchestration
        </Typography>

        <Grid container spacing={3} sx={{ mt: 2 }}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: 4,
                  },
                }}
              >
                <CardContent sx={{ textAlign: 'center', flexGrow: 1 }}>
                  <Box sx={{ color: 'primary.main', mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography variant="h6" component="h2" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {feature.description}
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center' }}>
                  <Button
                    size="small"
                    variant="contained"
                    onClick={() => navigate(feature.path)}
                  >
                    Get Started
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  )
}