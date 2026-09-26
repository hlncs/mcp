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
  timeoutMs: 30000, // 30 seconds
  warningMs: 10000, // Show warning after 10 seconds
  checkIntervalMs: 1000, // Check every 1 second
}

export default function EventStreamViewer({ 
  planId,
  timeoutMs = parseInt(import.meta.env.VITE_SSE_TIMEOUT || DEFAULT_CONFIG.timeoutMs),
  warningMs = parseInt(import.meta.env.VITE_SSE_WARNING || DEFAULT_CONFIG.warningMs),
  onTimeout = null,
  onError = null,
  autoRetry = true,
  maxRetries = 3,
}) {
  const [events, setEvents] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState(null)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [isTimeout, setIsTimeout] = useState(false)
  const [showWarning, setShowWarning] = useState(false)
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
      setIsTimeout(false)
      setShowWarning(false)
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
    let hasReceivedEvent = false

    const startConnection = () => {
      try {
        eventSource = new EventSource(`http://localhost:8000/stream/plan/${planId}`)
        setIsLoading(true)
        setIsConnected(false)
        setError(null)
        setIsTimeout(false)
        setShowWarning(false)
        hasReceivedEvent = false

        // Set timeout timer
        timeoutTimer = setTimeout(() => {
          if (!hasReceivedEvent) {
            setIsTimeout(true)
            setIsConnected(false)
            setError(`Connection timeout after ${formatTime(timeoutMs)}`)
            
            if (onTimeout) {
              onTimeout({
                planId,
                elapsedTime,
                retryCount,
              })
            }

            eventSource?.close()

            // Auto-retry if enabled
            if (autoRetry && retryCount < maxRetries) {
              setTimeout(retryConnection, 2000)
            }
          }
        }, timeoutMs)

        // Set warning timer
        warningTimer = setTimeout(() => {
          if (!hasReceivedEvent) {
            setShowWarning(true)
          }
        }, warningMs)

        // Start elapsed time counter
        elapsedTimer = setInterval(() => {
          setElapsedTime(prev => prev + DEFAULT_CONFIG.checkIntervalMs)
        }, DEFAULT_CONFIG.checkIntervalMs)

        eventSource.onopen = () => {
          setIsConnected(true)
          setIsLoading(false)
          setError(null)
          clearTimeout(timeoutTimer)
          clearTimeout(warningTimer)
        }

        eventSource.onmessage = (event) => {
          try {
            hasReceivedEvent = true
            setIsLoading(false)
            const data = JSON.parse(event.data)
            setEvents(prev => [...prev, data])
            
            // Clear warnings when first event arrives
            setShowWarning(false)
            setIsTimeout(false)
            
            // Reset timeout timer on each message
            if (timeoutTimer) clearTimeout(timeoutTimer)
            timeoutTimer = setTimeout(() => {
              setIsTimeout(true)
              setError(`Connection timeout after ${formatTime(timeoutMs)}`)
              eventSource?.close()
            }, timeoutMs)
          } catch (err) {
            console.error('Error parsing event:', err)
            setError(`Failed to parse event: ${err.message}`)
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
          console.error('EventSource error:', err)
          setIsConnected(false)
          setIsLoading(false)
          
          // Determine error type
          let errorMessage = 'Connection lost'
          if (err.type === 'error') {
            errorMessage = 'Server connection failed'
          }
          
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

          // Auto-retry if enabled
          if (autoRetry && retryCount < maxRetries) {
            setTimeout(retryConnection, 2000)
          }
        }
      } catch (err) {
        console.error('Error creating EventSource:', err)
        setError(`Failed to connect: ${err.message}`)
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
      if (eventSource) eventSource.close()
    }
  }, [planId, timeoutMs, warningMs, onTimeout, onError, autoRetry, maxRetries, retryCount])

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