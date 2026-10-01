import React, { useState, useEffect, useCallback } from 'react'
import {
  Container, Box, Card, CardContent, CardActions, Typography, Grid,
  Button, TextField, Divider, Chip, Alert, CircularProgress, Stack,
  Tab, Tabs, Badge, ToggleButton, ToggleButtonGroup, FormControlLabel,
  Checkbox, Dialog, DialogTitle, DialogContent, DialogActions,
  DialogContentText, Tooltip,
} from '@mui/material'
import FlightIcon from '@mui/icons-material/Flight'
import HotelIcon from '@mui/icons-material/Hotel'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'
import ReceiptIcon from '@mui/icons-material/Receipt'
import AutorenewIcon from '@mui/icons-material/Autorenew'
import AttachMoneyIcon from '@mui/icons-material/AttachMoney'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import StarIcon from '@mui/icons-material/Star'
import StraightenIcon from '@mui/icons-material/Straighten'
import PaymentIcon from '@mui/icons-material/Payment'
import LocationSearch from '../components/LocationSearch'
import { apiClient } from '../api/client'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const FLIGHT_PREFERENCES = [
  { value: 'cheapest',    label: 'Cheapest',     icon: AttachMoneyIcon, color: 'success' },
  { value: 'earliest',    label: 'Earliest',     icon: AccessTimeIcon,  color: 'info'    },
  { value: 'most_luxury', label: 'Most Luxury',  icon: StarIcon,        color: 'warning' },
  { value: 'shortest',    label: 'Shortest',     icon: StraightenIcon,  color: 'primary' },
]

const HOTEL_PREFERENCES = [
  { value: 'cheapest',    label: 'Cheapest',     icon: AttachMoneyIcon, color: 'success' },
  { value: 'earliest',   label: 'Earliest Avail', icon: AccessTimeIcon, color: 'info'   },
  { value: 'most_luxury', label: 'Most Luxury',  icon: StarIcon,        color: 'warning' },
]

const STATUS_META = {
  pending_approval: { label: 'Awaiting Approval', color: 'warning', icon: HourglassEmptyIcon },
  confirmed:        { label: 'Confirmed',          color: 'success', icon: CheckCircleIcon   },
  rejected:         { label: 'Rejected',           color: 'error',   icon: CancelIcon        },
}

// ---------------------------------------------------------------------------
// PaymentReceipt modal
// ---------------------------------------------------------------------------
function PaymentReceiptDialog({ payment, open, onClose }) {
  if (!payment) return null
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <PaymentIcon color="success" /> Payment Receipt
      </DialogTitle>
      <DialogContent dividers>
        {[
          ['Status',         payment.status],
          ['Transaction ID', payment.transaction_id],
          ['Amount',         `$${payment.amount_charged?.toLocaleString()} ${payment.currency}`],
          ['Gateway',        payment.gateway],
          ['Timestamp',      payment.timestamp?.replace('T', ' ').slice(0, 19) + ' UTC'],
        ].map(([k, v]) => (
          <Box key={k} sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">{k}</Typography>
            <Typography variant="caption" sx={{ fontWeight: 600 }}>{v}</Typography>
          </Box>
        ))}
        <Divider sx={{ my: 1 }} />
        <Typography variant="caption" color="text.secondary">
          Receipt: <a href={payment.receipt_url} target="_blank" rel="noreferrer">{payment.receipt_url}</a>
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  )
}

// ---------------------------------------------------------------------------
// AutoApprove confirmation dialog
// ---------------------------------------------------------------------------
function AutoApproveConfirmDialog({ open, bookingType, onConfirm, onCancel }) {
  return (
    <Dialog open={open} onClose={onCancel} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <AutorenewIcon color="warning" /> Enable Auto-Approve?
      </DialogTitle>
      <DialogContent>
        <DialogContentText>
          With auto-approve enabled, the best {bookingType} will be booked and
          payment will be processed <strong>immediately</strong> without asking for
          your confirmation. Are you sure?
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel}>Cancel</Button>
        <Button onClick={onConfirm} variant="contained" color="warning">
          Yes, Enable Auto-Approve
        </Button>
      </DialogActions>
    </Dialog>
  )
}

// ---------------------------------------------------------------------------
// StatusChip
// ---------------------------------------------------------------------------
function StatusChip({ status }) {
  const meta = STATUS_META[status] ?? { label: status, color: 'default', icon: null }
  const Icon = meta.icon
  return (
    <Chip
      label={meta.label}
      color={meta.color}
      size="small"
      icon={Icon ? <Icon /> : undefined}
      sx={{ fontWeight: 600 }}
    />
  )
}

// ---------------------------------------------------------------------------
// BookingCard
// ---------------------------------------------------------------------------
function BookingCard({ booking, onDecision }) {
  const [deciding, setDeciding] = useState(false)
  const [receiptOpen, setReceiptOpen] = useState(false)
  const offer = booking.offer ?? {}
  const isPending = booking.status === 'pending_approval'
  const isFlight = booking.booking_type === 'flight'
  const payment = booking.payment

  const handleDecide = async (approved) => {
    setDeciding(true)
    try { await onDecision(booking.booking_id, approved) }
    finally { setDeciding(false) }
  }

  const prefLabel = booking.preference
    ? (isFlight ? FLIGHT_PREFERENCES : HOTEL_PREFERENCES)
        .find(p => p.value === booking.preference)?.label ?? booking.preference
    : null

  return (
    <Card
      variant="outlined"
      sx={{
        borderColor: isPending ? 'warning.main' : booking.status === 'confirmed' ? 'success.main' : 'error.light',
        borderWidth: isPending ? 2 : 1,
      }}
    >
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {isFlight ? <FlightIcon color="primary" /> : <HotelIcon sx={{ color: 'secondary.main' }} />}
            <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
              {isFlight ? offer.airline : offer.name}
            </Typography>
            {booking.auto_approve && (
              <Tooltip title="Booked automatically">
                <Chip icon={<AutorenewIcon />} label="Auto" size="small" color="warning" variant="outlined" />
              </Tooltip>
            )}
            {prefLabel && (
              <Chip label={prefLabel} size="small" variant="outlined" />
            )}
          </Box>
          <StatusChip status={booking.status} />
        </Box>

        <Divider sx={{ mb: 1.5 }} />

        {/* Flight details */}
        {isFlight && (
          <Grid container spacing={1}>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">Route</Typography>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {offer.departure} → {offer.arrival}
              </Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="text.secondary">Date</Typography>
              <Typography variant="body2">{offer.date}</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="text.secondary">Cabin</Typography>
              <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>{offer.cabin_class}</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="text.secondary">Departs</Typography>
              <Typography variant="body2">{offer.departure_time}</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="text.secondary">Arrives</Typography>
              <Typography variant="body2">{offer.arrival_time}</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="text.secondary">Duration</Typography>
              <Typography variant="body2">
                {offer.duration_minutes
                  ? `${Math.floor(offer.duration_minutes / 60)}h ${offer.duration_minutes % 60}m`
                  : '—'}
              </Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="text.secondary">Stops</Typography>
              <Typography variant="body2">{offer.stops === 0 ? 'Non-stop' : `${offer.stops} stop`}</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="text.secondary">Passengers</Typography>
              <Typography variant="body2">{offer.passengers}</Typography>
            </Grid>
          </Grid>
        )}

        {/* Hotel details */}
        {!isFlight && (
          <Grid container spacing={1}>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">Location</Typography>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>{offer.location}</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="text.secondary">Stars / Rating</Typography>
              <Typography variant="body2">{'★'.repeat(offer.stars ?? 0)} {offer.rating}</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="text.secondary">Guests</Typography>
              <Typography variant="body2">{offer.guests}</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="text.secondary">Check-in</Typography>
              <Typography variant="body2">{offer.check_in}</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="text.secondary">Check-out</Typography>
              <Typography variant="body2">{offer.check_out}</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="text.secondary">Nights</Typography>
              <Typography variant="body2">{offer.nights}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">Amenities</Typography>
              <Typography variant="body2">{(offer.amenities ?? []).join(', ')}</Typography>
            </Grid>
          </Grid>
        )}

        {/* Total + payment */}
        <Box sx={{ mt: 2, p: 1.5, backgroundColor: 'grey.50', borderRadius: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            {isFlight
              ? `${offer.passengers} × $${offer.price?.toLocaleString()}`
              : `${offer.nights} night${offer.nights !== 1 ? 's' : ''} × $${offer.price_per_night?.toLocaleString()}`}
          </Typography>
          <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
            Total: ${offer.total_price?.toLocaleString()}
          </Typography>
        </Box>

        {/* Confirmation */}
        {booking.status === 'confirmed' && booking.confirmation_code && (
          <Alert
            severity="success"
            icon={<ReceiptIcon />}
            sx={{ mt: 1.5 }}
            action={
              payment && (
                <Button size="small" onClick={() => setReceiptOpen(true)} startIcon={<PaymentIcon />}>
                  Receipt
                </Button>
              )
            }
          >
            Confirmation: <strong>{booking.confirmation_code}</strong>
            {payment && ` · Paid $${payment.amount_charged?.toLocaleString()}`}
          </Alert>
        )}

        {booking.status === 'rejected' && (
          <Alert severity="error" sx={{ mt: 1.5 }}>
            Booking rejected{booking.decision_note ? `: ${booking.decision_note}` : '.'}
          </Alert>
        )}
      </CardContent>

      {/* Approve / Reject — only for pending non-auto bookings */}
      {isPending && !booking.auto_approve && (
        <CardActions sx={{ px: 2, pb: 2, gap: 1 }}>
          <Button
            variant="contained" color="success" fullWidth
            startIcon={deciding ? <CircularProgress size={16} color="inherit" /> : <CheckCircleIcon />}
            onClick={() => handleDecide(true)} disabled={deciding}
          >
            Approve &amp; Pay
          </Button>
          <Button
            variant="outlined" color="error" fullWidth
            startIcon={<CancelIcon />}
            onClick={() => handleDecide(false)} disabled={deciding}
          >
            Reject
          </Button>
        </CardActions>
      )}

      <PaymentReceiptDialog payment={payment} open={receiptOpen} onClose={() => setReceiptOpen(false)} />
    </Card>
  )
}

// ---------------------------------------------------------------------------
// PreferenceSelector
// ---------------------------------------------------------------------------
function PreferenceSelector({ value, onChange, options }) {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
        Selection preference
      </Typography>
      <ToggleButtonGroup value={value} exclusive onChange={(_, v) => v && onChange(v)} size="small" sx={{ flexWrap: 'wrap', gap: 0.5 }}>
        {options.map(({ value: v, label, icon: Icon, color }) => (
          <ToggleButton
            key={v} value={v}
            sx={{
              borderRadius: '20px !important',
              border: '1px solid !important',
              px: 1.5,
              '&.Mui-selected': { backgroundColor: `${color}.main`, color: 'white', borderColor: `${color}.main !important` },
            }}
          >
            <Icon sx={{ fontSize: 14, mr: 0.5 }} />
            <Typography variant="caption">{label}</Typography>
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
    </Box>
  )
}

// ---------------------------------------------------------------------------
// AutoApproveCheckbox
// ---------------------------------------------------------------------------
function AutoApproveCheckbox({ checked, onChange, bookingType }) {
  const [confirmOpen, setConfirmOpen] = useState(false)

  const handleChange = (e) => {
    if (e.target.checked) {
      setConfirmOpen(true)
    } else {
      onChange(false)
    }
  }

  return (
    <>
      <FormControlLabel
        control={
          <Checkbox
            checked={checked}
            onChange={handleChange}
            color="warning"
            size="small"
          />
        }
        label={
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              Auto-approve &amp; pay
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Skip approval — book and charge immediately
            </Typography>
          </Box>
        }
      />
      <AutoApproveConfirmDialog
        open={confirmOpen}
        bookingType={bookingType}
        onConfirm={() => { setConfirmOpen(false); onChange(true) }}
        onCancel={() => setConfirmOpen(false)}
      />
    </>
  )
}

// ---------------------------------------------------------------------------
// FlightSearchForm
// ---------------------------------------------------------------------------
function FlightSearchForm({ onOfferCreated }) {
  const [form, setForm] = useState({ departure: '', arrival: '', date: '', passengers: 1, cabin_class: 'economy' })
  const [preference, setPreference] = useState('cheapest')
  const [autoApprove, setAutoApprove] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const set = (field) => (v) => setForm(f => ({ ...f, [field]: typeof v === 'string' ? v : v.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.departure || !form.arrival || !form.date) { setError('Please fill in all required fields.'); return }
    setLoading(true); setError('')
    try {
      const res = await apiClient.executeMcpTool('offer_flight', {
        ...form,
        passengers: Number(form.passengers),
        preference,
        auto_approve: autoApprove,
      })
      onOfferCreated(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to fetch flight offers.')
    } finally { setLoading(false) }
  }

  return (
    <Card variant="outlined">
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <FlightIcon color="primary" />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>Search Flights</Typography>
        </Box>
        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <LocationSearch value={form.departure} onChange={set('departure')} onSelect={s => set('departure')(s.short_name)} label="Departure city *" placeholder="e.g. Sydney, Australia" />
            </Grid>
            <Grid item xs={12} sm={6}>
              <LocationSearch value={form.arrival} onChange={set('arrival')} onSelect={s => set('arrival')(s.short_name)} label="Arrival city *" placeholder="e.g. London, UK" />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField fullWidth label="Date *" type="date" size="small" value={form.date} onChange={set('date')} InputLabelProps={{ shrink: true }} />
            </Grid>
            <Grid item xs={6} sm={4}>
              <TextField fullWidth label="Passengers" type="number" size="small" value={form.passengers} onChange={set('passengers')} inputProps={{ min: 1, max: 9 }} />
            </Grid>
            <Grid item xs={6} sm={4}>
              <TextField fullWidth select label="Cabin class" size="small" value={form.cabin_class} onChange={set('cabin_class')} SelectProps={{ native: true }}>
                {['economy', 'business', 'first'].map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <PreferenceSelector value={preference} onChange={setPreference} options={FLIGHT_PREFERENCES} />
            </Grid>

            <Grid item xs={12}>
              <Divider />
            </Grid>

            <Grid item xs={12}>
              <AutoApproveCheckbox checked={autoApprove} onChange={setAutoApprove} bookingType="flight" />
            </Grid>

            {error && <Grid item xs={12}><Alert severity="error">{error}</Alert></Grid>}
            <Grid item xs={12}>
              <Button fullWidth type="submit" variant="contained" disabled={loading}
                startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <FlightIcon />}>
                {loading ? 'Searching…' : autoApprove ? 'Book Best Flight Now' : 'Find Best Flight'}
              </Button>
            </Grid>
          </Grid>
        </Box>
      </CardContent>
    </Card>
  )
}

// ---------------------------------------------------------------------------
// HotelSearchForm
// ---------------------------------------------------------------------------
function HotelSearchForm({ onOfferCreated }) {
  const [form, setForm] = useState({ location: '', check_in: '', check_out: '', guests: 1 })
  const [preference, setPreference] = useState('cheapest')
  const [autoApprove, setAutoApprove] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const set = (field) => (v) => setForm(f => ({ ...f, [field]: typeof v === 'string' ? v : v.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.location || !form.check_in || !form.check_out) { setError('Please fill in all required fields.'); return }
    setLoading(true); setError('')
    try {
      const res = await apiClient.executeMcpTool('offer_hotel', {
        ...form,
        guests: Number(form.guests),
        preference,
        auto_approve: autoApprove,
      })
      onOfferCreated(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to fetch hotel offers.')
    } finally { setLoading(false) }
  }

  return (
    <Card variant="outlined">
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <HotelIcon sx={{ color: 'secondary.main' }} />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>Search Hotels</Typography>
        </Box>
        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <LocationSearch value={form.location} onChange={set('location')} onSelect={s => set('location')(s.short_name)} label="Destination *" placeholder="e.g. Paris, France" />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField fullWidth label="Check-in *" type="date" size="small" value={form.check_in} onChange={set('check_in')} InputLabelProps={{ shrink: true }} />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField fullWidth label="Check-out *" type="date" size="small" value={form.check_out} onChange={set('check_out')} InputLabelProps={{ shrink: true }} />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField fullWidth label="Guests" type="number" size="small" value={form.guests} onChange={set('guests')} inputProps={{ min: 1, max: 20 }} />
            </Grid>

            <Grid item xs={12}>
              <PreferenceSelector value={preference} onChange={setPreference} options={HOTEL_PREFERENCES} />
            </Grid>

            <Grid item xs={12}>
              <Divider />
            </Grid>

            <Grid item xs={12}>
              <AutoApproveCheckbox checked={autoApprove} onChange={setAutoApprove} bookingType="hotel" />
            </Grid>

            {error && <Grid item xs={12}><Alert severity="error">{error}</Alert></Grid>}
            <Grid item xs={12}>
              <Button fullWidth type="submit" variant="contained" color="secondary" disabled={loading}
                startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <HotelIcon />}>
                {loading ? 'Searching…' : autoApprove ? 'Book Best Hotel Now' : 'Find Best Hotel'}
              </Button>
            </Grid>
          </Grid>
        </Box>
      </CardContent>
    </Card>
  )
}

// ---------------------------------------------------------------------------
// BookingPage
// ---------------------------------------------------------------------------
export default function BookingPage() {
  const [tab, setTab] = useState(0)
  const [bookings, setBookings] = useState([])
  const [loadingBookings, setLoadingBookings] = useState(false)
  const [notification, setNotification] = useState(null)

  const pendingCount = bookings.filter(b => b.status === 'pending_approval').length

  const refreshBookings = useCallback(async () => {
    setLoadingBookings(true)
    try {
      const res = await apiClient.listBookings()
      setBookings(res.data.bookings ?? [])
    } catch { /* non-fatal */ }
    finally { setLoadingBookings(false) }
  }, [])

  useEffect(() => { refreshBookings() }, [refreshBookings])

  const handleOfferCreated = async (offerResponse) => {
    const autoApproved = offerResponse.auto_approved
    const payment = offerResponse.payment
    setNotification({
      severity: autoApproved ? 'success' : 'info',
      message: autoApproved
        ? `Booked automatically! Paid $${payment?.amount_charged?.toLocaleString()}. Confirmation: ${offerResponse.booking_id?.slice(0, 8)}…`
        : `Offer created — review and approve in the My Bookings tab.`,
    })
    await refreshBookings()
    setTab(2)
  }

  const handleDecision = async (bookingId, approved) => {
    try {
      const res = await apiClient.decideBooking(bookingId, approved)
      const updated = res.data
      setBookings(prev => prev.map(b => b.booking_id === bookingId ? updated : b))
      setNotification({
        severity: approved ? 'success' : 'warning',
        message: approved
          ? `Confirmed! Code: ${updated.confirmation_code} · Paid $${updated.payment?.amount_charged?.toLocaleString()}`
          : 'Booking rejected.',
      })
    } catch (err) {
      setNotification({ severity: 'error', message: err.response?.data?.detail ?? 'Could not record decision.' })
    }
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 0.5 }}>
          Flight &amp; Hotel Booking
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Choose a selection preference, optionally enable auto-approve to skip manual confirmation.
        </Typography>

        {notification && (
          <Alert severity={notification.severity} onClose={() => setNotification(null)} sx={{ mb: 2 }}>
            {notification.message}
          </Alert>
        )}

        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Flights" icon={<FlightIcon fontSize="small" />} iconPosition="start" />
          <Tab label="Hotels"  icon={<HotelIcon  fontSize="small" />} iconPosition="start" />
          <Tab
            label={pendingCount > 0
              ? <Badge badgeContent={pendingCount} color="warning">My Bookings</Badge>
              : 'My Bookings'}
            icon={<ReceiptIcon fontSize="small" />} iconPosition="start"
          />
        </Tabs>

        {tab === 0 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}><FlightSearchForm onOfferCreated={handleOfferCreated} /></Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1.5 }}>Preference guide</Typography>
                  <Stack spacing={1}>
                    {FLIGHT_PREFERENCES.map(({ label, icon: Icon, color, value }) => (
                      <Box key={value} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Icon fontSize="small" color={color} />
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>{label}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {value === 'cheapest'    && 'Lowest total price'}
                            {value === 'earliest'    && 'First departure of the day'}
                            {value === 'most_luxury' && 'First class > business > economy'}
                            {value === 'shortest'    && 'Least flying time + fewest stops'}
                          </Typography>
                        </Box>
                      </Box>
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {tab === 1 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}><HotelSearchForm onOfferCreated={handleOfferCreated} /></Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1.5 }}>Preference guide</Typography>
                  <Stack spacing={1}>
                    {HOTEL_PREFERENCES.map(({ label, icon: Icon, color, value }) => (
                      <Box key={value} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Icon fontSize="small" color={color} />
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>{label}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {value === 'cheapest'    && 'Lowest price per night'}
                            {value === 'earliest'    && 'First available check-in date'}
                            {value === 'most_luxury' && 'Highest star rating, then best rating score'}
                          </Typography>
                        </Box>
                      </Box>
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {tab === 2 && (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">All Bookings ({bookings.length})</Typography>
              <Button size="small" onClick={refreshBookings} disabled={loadingBookings}>
                {loadingBookings ? <CircularProgress size={16} /> : 'Refresh'}
              </Button>
            </Box>

            {bookings.length === 0 && !loadingBookings && (
              <Alert severity="info">No bookings yet. Use the Flights or Hotels tabs to create an offer.</Alert>
            )}

            {['pending_approval', 'confirmed', 'rejected'].map(status => {
              const group = bookings.filter(b => b.status === status)
              if (!group.length) return null
              const meta = STATUS_META[status]
              return (
                <Box key={status} sx={{ mb: 4 }}>
                  <Typography variant="subtitle2" color={`${meta.color}.main`}
                    sx={{ fontWeight: 700, mb: 1.5, textTransform: 'uppercase', letterSpacing: 1 }}>
                    {meta.label} ({group.length})
                  </Typography>
                  <Grid container spacing={2}>
                    {group.map(b => (
                      <Grid item xs={12} md={6} key={b.booking_id}>
                        <BookingCard booking={b} onDecision={handleDecision} />
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )
            })}
          </Box>
        )}
      </Box>
    </Container>
  )
}
