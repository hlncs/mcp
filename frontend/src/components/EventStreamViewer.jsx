import React, { useEffect, useState, useCallback } from 'react'
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
  LinearProgress,
  Button,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import HourglassBottomIcon from '@mui/icons-material/HourglassBottom'
import ErrorIcon from '@mui/icons-material/Error'
import WarningIcon from '@mui/icons-material/Warning'
import RefreshIcon from '@mui/icons-material/Refresh'

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

// Default configuration
const DEFAULT_CONFIG = {
  timeoutMs: 30000,
  warningMs: 10000,
  checkIntervalMs: 1000,
  maxRetries: 3,
  retryDelay: 2000, // ms
}

// Add fallback UI function
const FallbackUI = ({ error, onRetry }) => (
  <Box sx={{ textAlign: 'center', py: 4 }}>
    <ErrorIcon sx={{ fontSize: 60, color: 'error.main', mb: 2 }} />
    <Typography variant="h6" gutterBottom>
      Unable to Connect
    </Typography>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
      {error || 'The connection could not be established'}
    </Typography>
    <Button 
      variant="contained" 
      color="primary"
      onClick={onRetry}
      startIcon={<RefreshIcon />}
    >
      Retry Connection
    </Button>
  </Box>
)

// Add defensive error handler
const handleConnectionError = (error, context) => {
  console.error('Connection error:', error)
  
  // Different handling based on error type
  if (error.type === 'TIMEOUT') {
    return 'Server took too long to respond'
  } else if (error.type === 'NETWORK') {
    return 'Network connection failed'
  } else if (error.type === 'PARSE') {
    return 'Invalid response from server'
  } else if (error.type === 'AUTH') {
    return 'Authentication required'
  } else {
    return 'Unexpected error occurred'
  }
}

// Main component with better error handling
export default function EventStreamViewer({ 
  planId,
  timeoutMs = DEFAULT_CONFIG.timeoutMs,
  warningMs = DEFAULT_CONFIG.warningMs,
  autoRetry = true,
  maxRetries = DEFAULT_CONFIG.maxRetries,
  onTimeout = null,
  onError = null,
}) {
  const [events, setEvents] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState(null)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [retryCount, setRetryCount] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  // Format time display
  const formatTime = (ms) => {
    const seconds = Math.floor(ms / 1000)
    return `${seconds}s`
  }

  // Retry connection
  const retryConnection = useCallback(() => {
    if (retryCount < maxRetries) {
      setRetryCount(prev => prev + 1)
      setError(null)
      setElapsedTime(0)
      setEvents([])
    }
  }, [retryCount, maxRetries])

  useEffect(() => {
    if (!planId) return

    let timeoutTimer = null
    let warningTimer = null
    let elapsedTimer = null
    let eventSource = null

    const startConnection = () => {
      try {
        // Validate planId
        if (typeof planId !== 'string' || planId.trim().length === 0) {
          throw new Error('Invalid plan ID')
        }

        const url = `http://localhost:8000/stream/plan/${encodeURIComponent(planId)}`
        
        logger.info(`Connecting to event stream: ${url}`)
        eventSource = new EventSource(url)
        setIsLoading(true)
        setIsConnected(false)
        setError(null)

        // Set timeout
        timeoutTimer = setTimeout(() => {
          setError(`Connection timeout after ${timeoutMs}ms`)
          eventSource?.close()

          if (onTimeout) {
            onTimeout({ planId, elapsedTime, retryCount })
          }

          if (autoRetry && retryCount < maxRetries) {
            setTimeout(retryConnection, DEFAULT_CONFIG.retryDelay)
          }
        }, timeoutMs)

        // Set warning
        warningTimer = setTimeout(() => {
          if (events.length === 0) {
            setError('Server is taking longer than expected')
          }
        }, warningMs)

        // Track elapsed time
        elapsedTimer = setInterval(() => {
          setElapsedTime(prev => prev + DEFAULT_CONFIG.checkIntervalMs)
        }, DEFAULT_CONFIG.checkIntervalMs)

        eventSource.onopen = () => {
          logger.info('Event stream connected')
          setIsConnected(true)
          setIsLoading(false)
          setError(null)
          if (timeoutTimer) clearTimeout(timeoutTimer)
        }

        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            setEvents(prev => [...prev, data])
            setIsLoading(false)
            setError(null)
          } catch (err) {
            const parseError = new Error(`Failed to parse event: ${err.message}`)
            logger.error('Parse error:', parseError)
            setError(handleConnectionError({ type: 'PARSE' }))
            
            if (onError) {
              onError({
                type: 'PARSE_ERROR',
                message: err.message,
                planId,
              })
            }
          }
        }

        eventSource.onerror = (err) => {
          logger.error('EventSource error:', err)
          setIsConnected(false)
          setIsLoading(false)

          const errorMessage = handleConnectionError({ type: 'NETWORK' })
          setError(errorMessage)

          if (onError) {
            onError({
              type: 'CONNECTION_ERROR',
              message: errorMessage,
              planId,
              retryCount,
            })
          }

          eventSource.close()

          if (autoRetry && retryCount < maxRetries) {
            setTimeout(retryConnection, DEFAULT_CONFIG.retryDelay)
          }
        }

      } catch (err) {
        logger.error('Connection setup error:', err)
        const errorMessage = handleConnectionError({ type: 'SETUP' })
        setError(errorMessage)
        setIsLoading(false)

        if (onError) {
          onError({
            type: 'SETUP_ERROR',
            message: err.message,
            planId,
          })
        }
      }
    }

    startConnection()

    return () => {
      if (timeoutTimer) clearTimeout(timeoutTimer)
      if (warningTimer) clearTimeout(warningTimer)
      if (elapsedTimer) clearInterval(elapsedTimer)
      if (eventSource) {
        try {
          eventSource.close()
        } catch (err) {
          logger.error('Error closing EventSource:', err)
        }
      }
    }
  }, [planId, timeoutMs, warningMs, onTimeout, onError, autoRetry, maxRetries, retryCount])

  if (error && events.length === 0) {
    return (
      <Card>
        <CardContent>
          <FallbackUI 
            error={error}
            onRetry={retryConnection}
          />
        </CardContent>
      </Card>
    )
  }

  const progressPercentage = Math.min((elapsedTime / timeoutMs) * 100, 100)

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h6">
              Event Planning Progress
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
              {formatTime(elapsedTime)} / {formatTime(timeoutMs)}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {isConnected ? (
              <Chip label="Connected" color="success" size="small" />
            ) : isLoading ? (
              <Chip icon={<CircularProgress size={16} />} label="Connecting..." size="small" />
            ) : (
              <Chip label="Disconnected" color="error" size="small" />
            )}
            
            {retryCount > 0 && (
              <Chip 
                label={`Retry ${retryCount}/${maxRetries}`}
                size="small"
                variant="outlined"
              />
            )}
          </Box>
        </Box>

        {/* Progress bar */}
        <Box sx={{ mb: 2 }}>
          <LinearProgress 
            variant="determinate" 
            value={progressPercentage}
            sx={{
              backgroundColor: '#e0e0e0',
              '& .MuiLinearProgress-bar': {
                backgroundColor: isTimeout ? '#f44336' : isConnected ? '#4caf50' : '#2196f3',
              }
            }}
          />
        </Box>

        {/* Error alert */}
        {error && (
          <Alert 
            severity={isTimeout ? "warning" : "error"}
            sx={{ mb: 2 }}
            action={
              autoRetry && retryCount < maxRetries ? (
                <Button 
                  color="inherit" 
                  size="small"
                  onClick={retryConnection}
                >
                  Retry
                </Button>
              ) : retryCount >= maxRetries ? (
                <Button 
                  color="inherit" 
                  size="small"
                  onClick={() => setRetryCount(0)}
                >
                  Reset
                </Button>
              ) : null
            }
          >
            {error}
          </Alert>
        )}

        {/* Warning alert */}
        {showWarning && !hasReceivedEvent && (
          <Alert 
            severity="warning"
            icon={<WarningIcon />}
            sx={{ mb: 2 }}
          >
            Still waiting for server response ({formatTime(elapsedTime)}). 
            If this takes longer than {formatTime(timeoutMs)}, the connection will timeout.
          </Alert>
        )}

        {/* Events list or loading state */}
        {events.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <CircularProgress />
            <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>
              {isLoading ? 'Connecting to server...' : 'Waiting for events...'}
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mt: 1 }}>
              Timeout in {formatTime(Math.max(0, timeoutMs - elapsedTime))}
            </Typography>
          </Box>
        ) : (
          <List>
            {events.map((event, index) => (
              <ListItem key={index} sx={{ py: 1 }}>
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {statusIcons[event.status]}
                </ListItemIcon>
                <ListItemText
                  primary={event.step}
                  secondary={
                    <Box sx={{ mt: 0.5 }}>
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
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        )}

        {/* Retry information */}
        {retryCount > 0 && (
          <Box sx={{ mt: 2, p: 1, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Connection attempt {retryCount} of {maxRetries}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}