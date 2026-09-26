import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  Divider,
} from '@mui/material'
import HomeIcon from '@mui/icons-material/Home'
import EventIcon from '@mui/icons-material/Event'
import CloudIcon from '@mui/icons-material/Cloud'
import MoneyIcon from '@mui/icons-material/Money'
import SettingsIcon from '@mui/icons-material/Settings'
import BuildIcon from '@mui/icons-material/Build'

export default function Sidebar({ open }) {
  const navigate = useNavigate()
  const location = useLocation()

  const mainMenuItems = [
    { label: 'Home', icon: HomeIcon, path: '/' },
    { label: 'Event Planner', icon: EventIcon, path: '/event-planner' },
    { label: 'Weather', icon: CloudIcon, path: '/weather' },
    { label: 'Budget', icon: MoneyIcon, path: '/budget' },
    { label: 'Services', icon: BuildIcon, path: '/services' },
  ]

  const secondaryMenuItems = [
    { label: 'Settings', icon: SettingsIcon, path: '/settings' },
  ]

  const renderMenuItems = (items) => {
    return items.map((item) => {
      const Icon = item.icon
      const isActive = location.pathname === item.path

      return (
        <ListItem
          button
          key={item.path}
          onClick={() => navigate(item.path)}
          sx={{
            backgroundColor: isActive ? 'rgba(25, 118, 210, 0.1)' : 'transparent',
            borderLeft: isActive ? '4px solid #1976D2' : '4px solid transparent',
            '&:hover': {
              backgroundColor: 'rgba(0, 0, 0, 0.04)',
            },
          }}
        >
          <ListItemIcon
            sx={{
              color: isActive ? '#1976D2' : 'inherit',
              minWidth: 40,
            }}
          >
            <Icon />
          </ListItemIcon>
          <ListItemText
            primary={item.label}
            sx={{
              color: isActive ? '#1976D2' : 'inherit',
              fontWeight: isActive ? 'bold' : 'normal',
            }}
          />
        </ListItem>
      )
    })
  }

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: 240,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 240,
          boxSizing: 'border-box',
          mt: '64px',
        },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
          Navigation
        </Typography>
      </Box>

      <List>
        {renderMenuItems(mainMenuItems)}
      </List>

      <Divider sx={{ my: 2 }} />

      <Box sx={{ p: 2 }}>
        <Typography variant="caption" sx={{ fontWeight: 'bold', color: 'text.secondary' }}>
          OTHER
        </Typography>
      </Box>

      <List>
        {renderMenuItems(secondaryMenuItems)}
      </List>
    </Drawer>
  )
}