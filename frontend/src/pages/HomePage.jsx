import React from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Box,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Grid,
} from '@mui/material'
import EventIcon from '@mui/icons-material/Event'
import CloudIcon from '@mui/icons-material/Cloud'
import MoneyIcon from '@mui/icons-material/Money'
import SettingsIcon from '@mui/icons-material/Settings'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'

export default function HomePage() {
  const navigate = useNavigate()

  const primaryColor = '#1976D2'
  const secondaryColor = '#42A5F5' // Lighter blue instead of red

  const features = [
    {
      id: 'event-planner',
      title: 'Event Planner',
      description: 'Plan your perfect event with dates, locations, guest count, and budget management.',
      icon: EventIcon,
      path: '/event-planner',
    },
    {
      id: 'weather',
      title: 'Weather Forecast',
      description: 'Check weather forecasts for your event location to ensure perfect planning.',
      icon: CloudIcon,
      path: '/weather',
    },
    {
      id: 'budget',
      title: 'Budget Manager',
      description: 'Track and manage your event budget with detailed cost breakdown.',
      icon: MoneyIcon,
      path: '/budget',
    },
    {
      id: 'services',
      title: 'Services',
      description: 'Browse and manage vendors and services for your event.',
      icon: SettingsIcon,
      path: '/services',
    },
  ]

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Hero Section with Primary Color Background */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${primaryColor} 0%, ${primaryColor}dd 100%)`,
          color: 'white',
          py: 8,
          px: 3,
          borderBottom: `4px solid ${secondaryColor}`,
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center' }}>
            <Typography
              variant="h2"
              gutterBottom
              sx={{
                fontWeight: 'bold',
                mb: 2,
                letterSpacing: '-0.5px',
              }}
            >
              Event Management Suite
            </Typography>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 300,
                opacity: 0.95,
                maxWidth: '600px',
                mx: 'auto',
              }}
            >
              Complete tools for planning and managing your events with ease
            </Typography>
          </Box>
        </Container>
      </Box>

      {/* Main Content */}
      <Box sx={{ flexGrow: 1, py: 8, px: 3 }}>
        <Container maxWidth="lg">
          {/* Features Grid */}
          <Grid container spacing={4} sx={{ mb: 8 }}>
            {features.map((feature) => {
              const IconComponent = feature.icon
              return (
                <Grid item xs={12} sm={6} md={6} lg={6} key={feature.id}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      cursor: 'pointer',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      border: `1px solid #e0e0e0`,
                      '&:hover': {
                        boxShadow: '0 12px 32px rgba(0, 0, 0, 0.15)',
                        transform: 'translateY(-8px)',
                        borderColor: secondaryColor,
                      },
                      borderTop: `5px solid ${secondaryColor}`,
                    }}
                    onClick={() => navigate(feature.path)}
                  >
                    {/* Icon Section with Secondary Color Background */}
                    <Box
                      sx={{
                        p: 3,
                        background: `linear-gradient(135deg, ${secondaryColor}10 0%, ${secondaryColor}05 100%)`,
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        borderBottom: `1px solid ${secondaryColor}20`,
                      }}
                    >
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'center',
                          alignItems: 'center',
                          width: 80,
                          height: 80,
                          borderRadius: '12px',
                          background: `${secondaryColor}15`,
                          transition: 'all 0.3s ease',
                        }}
                      >
                        <IconComponent
                          sx={{
                            fontSize: 48,
                            color: secondaryColor,
                          }}
                        />
                      </Box>
                    </Box>

                    {/* Content Section */}
                    <CardContent sx={{ flexGrow: 1, pb: 0 }}>
                      <Typography
                        variant="h5"
                        gutterBottom
                        sx={{
                          fontWeight: 600,
                          color: '#212121',
                          mb: 1,
                        }}
                      >
                        {feature.title}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          lineHeight: 1.6,
                          color: '#666',
                        }}
                      >
                        {feature.description}
                      </Typography>
                    </CardContent>

                    {/* Action Section */}
                    <CardActions sx={{ pt: 3 }}>
                      <Button
                        fullWidth
                        variant="contained"
                        endIcon={<ArrowForwardIcon />}
                        sx={{
                          backgroundColor: secondaryColor,
                          color: 'white',
                          fontWeight: 600,
                          py: 1.5,
                          borderRadius: '8px',
                          textTransform: 'none',
                          fontSize: '1rem',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            backgroundColor: primaryColor,
                            boxShadow: `0 8px 16px ${primaryColor}40`,
                            transform: 'translateX(4px)',
                          },
                        }}
                        onClick={() => navigate(feature.path)}
                      >
                        Open
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              )
            })}
          </Grid>

          {/* Info Section */}
          <Box
            sx={{
              p: 4,
              backgroundColor: '#fafafa',
              borderRadius: '12px',
              border: `1px solid #e0e0e0`,
              background: `linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%)`,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Box
                sx={{
                  width: 4,
                  height: 32,
                  backgroundColor: primaryColor,
                  borderRadius: '2px',
                  mr: 2,
                }}
              />
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  color: '#212121',
                }}
              >
                🚀 Getting Started
              </Typography>
            </Box>

            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                mb: 2.5,
                color: '#555',
                lineHeight: 1.6,
              }}
            >
              Welcome to the Event Management Suite! Here's how to get started:
            </Typography>

            <Grid container spacing={2}>
              {[
                {
                  number: '1',
                  text: 'Start with Event Planner to create and manage your event details',
                },
                {
                  number: '2',
                  text: 'Check Weather Forecast for your event location',
                },
                {
                  number: '3',
                  text: 'Use Budget Manager to track expenses',
                },
                {
                  number: '4',
                  text: 'Explore Services to find vendors and service providers',
                },
              ].map((item) => (
                <Grid item xs={12} sm={6} key={item.number}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                    <Box
                      sx={{
                        minWidth: 32,
                        height: 32,
                        borderRadius: '50%',
                        backgroundColor: primaryColor,
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 700,
                        fontSize: '0.875rem',
                        flexShrink: 0,
                      }}
                    >
                      {item.number}
                    </Box>
                    <Typography
                      variant="body2"
                      sx={{
                        color: '#555',
                        lineHeight: 1.6,
                        pt: 0.5,
                      }}
                    >
                      {item.text}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Container>
      </Box>
    </Box>
  )
}