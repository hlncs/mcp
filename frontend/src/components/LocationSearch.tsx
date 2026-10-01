import React, { useState, useCallback, useRef, useEffect } from 'react'
import {
  Box,
  TextField,
  InputAdornment,
  CircularProgress,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  Chip,
  Alert,
} from '@mui/material'
import LocationOnIcon from '@mui/icons-material/LocationOn'
import SearchIcon from '@mui/icons-material/Search'
import { apiClient } from '../api/client'

/**
 * LocationSearch
 *
 * Props:
 *   value          {string}   Controlled input value
 *   onChange       {fn}       Called with the raw text as user types
 *   onSelect       {fn}       Called with a suggestion object when user picks one:
 *                               { display_name, city, country, short_name, lat, lon }
 *   label          {string}   TextField label  (default: "Location")
 *   placeholder    {string}   TextField placeholder
 *   disabled       {bool}
 *   error          {string}   External error message to show below the field
 *   size           {string}   "small" | "medium"
 */
export default function LocationSearch({
  value = '',
  onChange,
  onSelect,
  label = 'Location',
  placeholder = 'e.g. Sydney, Australia',
  disabled = false,
  error: externalError = '',
  size = 'small',
}) {
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const [internalError, setInternalError] = useState('')
  const [dropdownStyle, setDropdownStyle] = useState({})
  const debounceTimer = useRef(null)
  const inputRef = useRef(null)
  const containerRef = useRef(null)

  // Reposition the fixed dropdown to sit below the input
  const updateDropdownPosition = useCallback(() => {
    if (!inputRef.current) return
    const rect = inputRef.current.getBoundingClientRect()
    setDropdownStyle({
      position: 'fixed',
      top: rect.bottom + 4,
      left: rect.left,
      width: rect.width,
      zIndex: 1400,
    })
  }, [])

  useEffect(() => {
    if (!open) return
    updateDropdownPosition()
    window.addEventListener('scroll', updateDropdownPosition, true)
    window.addEventListener('resize', updateDropdownPosition)
    return () => {
      window.removeEventListener('scroll', updateDropdownPosition, true)
      window.removeEventListener('resize', updateDropdownPosition)
    }
  }, [open, updateDropdownPosition])

  const fetchSuggestions = useCallback(async (query) => {
    if (!query || query.trim().length < 2) {
      setSuggestions([])
      setOpen(false)
      return
    }

    setLoading(true)
    setInternalError('')
    try {
      const res = await apiClient.searchLocation(query.trim())
      const results = res.data?.suggestions ?? []
      setSuggestions(results)
      if (results.length > 0) {
        updateDropdownPosition()
        setOpen(true)
      } else {
        setOpen(false)
      }
    } catch {
      setInternalError('Could not reach location service. Please type your location manually.')
      setSuggestions([])
      setOpen(false)
    } finally {
      setLoading(false)
    }
  }, [updateDropdownPosition])

  const handleInputChange = (e) => {
    const v = e.target.value
    onChange?.(v)
    clearTimeout(debounceTimer.current)
    debounceTimer.current = setTimeout(() => fetchSuggestions(v), 350)
  }

  const handleSelect = (suggestion) => {
    onSelect?.(suggestion)
    onChange?.(suggestion.short_name)
    setSuggestions([])
    setOpen(false)
  }

  const handleBlur = () => {
    // Delay close so the click on a list item registers first
    setTimeout(() => setOpen(false), 180)
  }

  const displayError = externalError || internalError

  return (
    <Box ref={containerRef} sx={{ width: '100%' }}>
      <TextField
        fullWidth
        inputRef={inputRef}
        label={label}
        placeholder={placeholder}
        value={value}
        onChange={handleInputChange}
        onFocus={() => suggestions.length > 0 && setOpen(true)}
        onBlur={handleBlur}
        disabled={disabled}
        size={size}
        error={Boolean(displayError)}
        autoComplete="off"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <LocationOnIcon sx={{ color: 'text.secondary', fontSize: 18 }} />
            </InputAdornment>
          ),
          endAdornment: loading ? (
            <InputAdornment position="end">
              <CircularProgress size={16} />
            </InputAdornment>
          ) : null,
        }}
      />

      {/* Suggestions dropdown — rendered via fixed positioning to escape overflow:hidden parents */}
      {open && suggestions.length > 0 && (
        <Paper
          elevation={8}
          style={dropdownStyle}
          sx={{
            maxHeight: 280,
            overflowY: 'auto',
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
          }}
        >
          <List dense disablePadding>
            {suggestions.map((s, idx) => (
              <ListItem key={idx} disablePadding divider={idx < suggestions.length - 1}>
                <ListItemButton
                  onMouseDown={(e) => e.preventDefault()} // prevent input blur before click fires
                  onClick={() => handleSelect(s)}
                  sx={{ py: 0.75, px: 1.5 }}
                >
                  <LocationOnIcon
                    sx={{ mr: 1, color: 'primary.main', fontSize: 16, flexShrink: 0 }}
                  />
                  <ListItemText
                    primary={
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {s.short_name}
                      </Typography>
                    }
                    secondary={
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{
                          display: '-webkit-box',
                          WebkitBoxOrient: 'vertical',
                          WebkitLineClamp: 1,
                          overflow: 'hidden',
                        }}
                      >
                        {s.display_name}
                      </Typography>
                    }
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Error / service unavailable */}
      {displayError && (
        <Alert severity="warning" sx={{ mt: 1, py: 0.5 }}>
          <Typography variant="caption">{displayError}</Typography>
        </Alert>
      )}

      {/* "Did you mean?" chips — shown after dropdown closes with no selection */}
      {!open && !value && suggestions.length > 0 && (
        <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
          <Typography variant="caption" color="text.secondary" sx={{ width: '100%' }}>
            Did you mean:
          </Typography>
          {suggestions.slice(0, 4).map((s, idx) => (
            <Chip
              key={idx}
              label={s.short_name}
              size="small"
              icon={<SearchIcon />}
              onClick={() => handleSelect(s)}
              color="primary"
              variant="outlined"
            />
          ))}
        </Box>
      )}
    </Box>
  )
}
