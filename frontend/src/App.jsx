import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Box from '@mui/material/Box'

import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import HomePage from './pages/HomePage'
import EventPlannerPage from './pages/EventPlannerPage'
import WeatherPage from './pages/WeatherPage'
import BudgetPage from './pages/BudgetPage'
import ServiceSearchPage from './pages/ServiceSearchPage'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
})

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
          <Sidebar open={sidebarOpen} />
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              ml: sidebarOpen ? '240px' : '0',
              mt: '64px',
              transition: 'margin 0.3s ease',
            }}
          >
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/planner" element={<EventPlannerPage />} />
              <Route path="/weather" element={<WeatherPage />} />
              <Route path="/budget" element={<BudgetPage />} />
              <Route path="/services" element={<ServiceSearchPage />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  )
}

export default App