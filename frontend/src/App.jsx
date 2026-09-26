import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Box from '@mui/material/Box'
import { CurrencyProvider } from './context/CurrencyContext'

import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import HomePage from './pages/HomePage'
import EventPlannerPage from './pages/EventPlannerPage'
import WeatherPage from './pages/WeatherPage'
import BudgetPage from './pages/BudgetPage'
import ServicesPage from './pages/ServicesPage'
import SettingsPage from './pages/SettingsPage'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976D2',
    },
    secondary: {
      main: '#42A5F5',
    },
  },
})

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <CurrencyProvider>
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
                {/* Home/Dashboard */}
                <Route path="/" element={<HomePage />} />

                {/* Feature Pages */}
                <Route path="/event-planner" element={<EventPlannerPage />} />
                <Route path="/weather" element={<WeatherPage />} />
                <Route path="/budget" element={<BudgetPage />} />
                <Route path="/services" element={<ServicesPage />} />
                <Route path="/settings" element={<SettingsPage />} />

                {/* Backwards compatibility */}
                <Route path="/plan" element={<Navigate to="/event-planner" replace />} />

                {/* Catch all */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Box>
          </Box>
        </Router>
      </CurrencyProvider>
    </ThemeProvider>
  )
}

export default App