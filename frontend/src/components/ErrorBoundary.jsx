import React from 'react'
import { Box, Card, CardContent, Typography, Button, Alert } from '@mui/material'
import ErrorIcon from '@mui/icons-material/Error'

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
    
    this.setState(prevState => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1
    }))

    // Log to error tracking service
    if (window.errorTracker) {
      window.errorTracker.logError({
        message: error.toString(),
        stack: errorInfo.componentStack,
        timestamp: new Date().toISOString()
      })
    }
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ m: 2 }}>
          <Card sx={{ backgroundColor: '#ffebee', borderColor: '#f44336', borderWidth: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 1 }}>
                <ErrorIcon color="error" />
                <Typography variant="h6" color="error">
                  Something went wrong
                </Typography>
              </Box>

              {this.state.error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {this.state.error.toString()}
                </Alert>
              )}

              {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                <Box sx={{ 
                  p: 2, 
                  backgroundColor: '#fafafa', 
                  borderRadius: 1, 
                  mb: 2,
                  fontFamily: 'monospace',
                  fontSize: '0.75rem',
                  maxHeight: '300px',
                  overflow: 'auto'
                }}>
                  <Typography variant="caption" component="pre">
                    {this.state.errorInfo.componentStack}
                  </Typography>
                </Box>
              )}

              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={this.resetError}
                >
                  Try Again
                </Button>
                
                <Button 
                  variant="outlined"
                  onClick={() => window.location.href = '/'}
                >
                  Go Home
                </Button>
              </Box>

              {this.state.errorCount > 3 && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  Multiple errors detected. Please refresh the page or contact support.
                </Alert>
              )}
            </CardContent>
          </Card>
        </Box>
      )
    }

    return this.props.children
  }
}