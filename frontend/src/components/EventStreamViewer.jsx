import React, { useEffect, useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import HourglassBottomIcon from '@mui/icons-material/HourglassBottom'
import ErrorIcon from '@mui/icons-material/Error'

const statusColors = {
  started: 'info',
  completed: 'success',
  error: 'error',
}

const statusIcons = {
  started: <HourglassBottomIcon />,
  completed: <CheckCircleIcon />,
  error: <ErrorIcon />,
}

export default function EventStreamViewer({ planId }) {
  const [events, setEvents] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!planId) return

    const eventSource = new EventSource(`http://localhost:8000/stream/plan/${planId}`)

    eventSource.onopen = () => {
      setIsConnected(true)
      setError(null)
    }

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setEvents((prev) => [...prev, data])
      } catch (err) {
        console.error('Error parsing event:', err)
      }
    }

    eventSource.onerror = (err) => {
      console.error('EventSource error:', err)
      setIsConnected(false)
      setError('Connection lost')
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [planId])

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Event Planning Progress
          </Typography>
          {isConnected ? (
            <Chip label="Connected" color="success" size="small" />
          ) : (
            <Chip label="Disconnected" color="error" size="small" />
          )}
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        {events.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <CircularProgress />
            <Typography variant="body2" sx={{ mt: 1 }}>
              Waiting for events...
            </Typography>
          </Box>
        ) : (
          <List>
            {events.map((event, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {statusIcons[event.status]}
                </ListItemIcon>
                <ListItemText
                  primary={event.step}
                  secondary={
                    <>
                      <Chip
                        label={event.status}
                        size="small"
                        color={statusColors[event.status]}
                        variant="outlined"
                        sx={{ mr: 1 }}
                      />
                      {event.details && Object.keys(event.details).length > 0 && (
                        <Typography variant="caption">
                          {JSON.stringify(event.details).slice(0, 50)}...
                        </Typography>
                      )}
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  )
}