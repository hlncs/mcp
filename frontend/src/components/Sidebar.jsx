import React from 'react'
import { Link } from 'react-router-dom'
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
} from '@mui/material'
import HomeIcon from '@mui/icons-material/Home'
import EventIcon from '@mui/icons-material/Event'
import CloudIcon from '@mui/icons-material/Cloud'
import AttachMoneyIcon from '@mui/icons-material/AttachMoney'
import SearchIcon from '@mui/icons-material/Search'

const menuItems = [
  { text: 'Home', icon: <HomeIcon />, path: '/' },
  { text: 'Event Planner', icon: <EventIcon />, path: '/planner' },
  { text: 'Weather', icon: <CloudIcon />, path: '/weather' },
  { text: 'Budget', icon: <AttachMoneyIcon />, path: '/budget' },
  { text: 'Services', icon: <SearchIcon />, path: '/services' },
]

export default function Sidebar({ open }) {
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
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {menuItems.map((item) => (
            <ListItem
              button
              key={item.text}
              component={Link}
              to={item.path}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(25, 118, 210, 0.1)',
                },
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItem>
          ))}
        </List>
      </Box>
    </Drawer>
  )
}