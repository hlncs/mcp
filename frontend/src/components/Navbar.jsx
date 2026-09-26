import React from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
} from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import EventNoteIcon from '@mui/icons-material/EventNote'

export default function Navbar({ onMenuClick }) {
  return (
    <AppBar position="fixed">
      <Toolbar>
        <IconButton
          color="inherit"
          edge="start"
          onClick={onMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        <EventNoteIcon sx={{ mr: 1 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Event Planning System
        </Typography>
      </Toolbar>
    </AppBar>
  )
}