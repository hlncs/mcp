# Event Management Suite

A comprehensive web application for planning and managing events with weather forecasting, budget tracking, and vendor management capabilities.

## 🎯 Features

### 1. **Event Planner**
- Create and manage event details
- Set event dates, locations, and guest count
- Budget planning and tracking
- Real-time event information display

### 2. **Weather Forecast**
- Search for locations (Sydney, New York, London, Tokyo, Paris)
- Interactive OpenStreetMap display with location markers
- Temperature unit selection (Celsius/Fahrenheit)
- Weather details: temperature, humidity, wind speed, pressure, conditions
- Auto-temperature conversion based on selected unit

### 3. **Budget Manager**
- Track event expenses by category
- Visual budget breakdown with progress bars
- Currency support: USD, EUR, AUD, JPY, CAD, NZD
- Budget allocation percentages
- Currency preference persists across all pages

### 4. **Services**
- Browse vendors and service providers
- Service categorization and filtering
- Contact and pricing information
- Integration with budget tracking

### 5. **Settings**
- Global currency preference (USD, EUR, AUD, JPY, CAD, NZD)
- Persistent user preferences (localStorage)
- Responsive configuration interface

### 6. **Navigation**
- Persistent sidebar navigation
- Active page highlighting
- Quick access to all features
- Responsive mobile layout

---

## 🚀 Getting Started

### Prerequisites
- **Node.js**: v16+ or v18+
- **npm**: v8+
- **Browser**: Modern browser with ES6 support

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/event-management-suite.git
cd event-management-suite
```

#### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
```

#### 3. Install Map & Weather Dependencies
```bash
# Leaflet for maps (compatible with React 18)
npm install react-leaflet@4.2.1 leaflet@1.9.4
```

#### 4. Start Development Server
```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 📦 Project Structure

```
event-management-suite/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   └── Sidebar.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── EventPlannerPage.jsx
│   │   │   ├── WeatherPage.jsx
│   │   │   ├── BudgetPage.jsx
│   │   │   ├── ServicesPage.jsx
│   │   │   └── SettingsPage.jsx
│   │   ├── context/
│   │   │   └── CurrencyContext.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── README.md
├── DEPENDENCIES.md
├── API.md
└── .gitignore
```

---

## 🛠️ Technology Stack

### Frontend
- **React 18.3.1** - UI library
- **Material-UI (MUI)** - Component library with Material Design
- **React Router DOM** - Client-side routing
- **Leaflet + React-Leaflet** - Interactive maps
- **Vite** - Build tool and dev server

### Features
- Context API for global state management (Currency)
- localStorage for data persistence
- Responsive design (mobile-first)
- Professional UI with consistent color scheme

### Color Scheme
- **Primary Color**: #1976D2 (Dark Blue)
- **Secondary Color**: #42A5F5 (Light Blue)
- **Text**: #212121, #666, #555
- **Backgrounds**: #f5f5f5, #fafafa

---

## 📝 Usage Guide

### Creating an Event

1. Click **Event Planner** in the sidebar
2. Fill in event details:
   - Event name and description
   - Date and time
   - Location (autocomplete available)
   - Guest count
   - Budget
3. Click **Save Event** to persist

### Checking Weather

1. Go to **Weather Forecast**
2. Enter a location (e.g., "Sydney, Australia")
3. Select temperature unit (Celsius/Fahrenheit)
4. View:
   - Interactive map with location marker
   - Real-time weather conditions
   - Temperature, humidity, wind speed, pressure

### Managing Budget

1. Navigate to **Budget Manager**
2. View total event budget
3. See cost breakdown by category:
   - Venue
   - Catering
   - Decorations
   - Entertainment
   - Photography
   - Transport
4. Budget percentages update automatically

### Setting Preferences

1. Click **Settings** in the sidebar
2. Select your preferred currency:
   - USD ($) - US Dollar
   - EUR (€) - Euro
   - AUD (A$) - Australian Dollar
   - JPY (¥) - Japanese Yen
   - CAD (C$) - Canadian Dollar
   - NZD (NZ$) - New Zealand Dollar
3. Currency displays across all pages automatically

---

## 🗺️ Supported Weather Locations

| City | Country | Coordinates |
|------|---------|-------------|
| Sydney | Australia | -33.8688, 151.2093 |
| New York | USA | 40.7128, -74.0060 |
| London | UK | 51.5074, -0.1278 |
| Tokyo | Japan | 35.6762, 139.6503 |
| Paris | France | 48.8566, 2.3522 |

### Search Format
Accepts multiple formats:
- `Sydney`
- `Sydney, Australia`
- `New York, USA`
- `London, UK`

---

## 💱 Supported Currencies

| Code | Symbol | Full Name |
|------|--------|-----------|
| USD | $ | US Dollar |
| EUR | € | Euro |
| AUD | A$ | Australian Dollar |
| JPY | ¥ | Japanese Yen |
| CAD | C$ | Canadian Dollar |
| NZD | NZ$ | New Zealand Dollar |

**Note:** Currencies are stored in `localStorage` and persist across browser sessions.

---

## 🔧 Configuration

### Environment Variables (Optional Backend)

Create `.env` file in project root:
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_WEATHER_API_KEY=your_key_here
```

### Vite Configuration

Located in `frontend/vite.config.js`:
```javascript
import react from '@vitejs/plugin-react'

export default {
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: false,
  },
}
```

---

## 🧪 Testing

### Run Development Server
```bash
cd frontend
npm run dev
```

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

---

## 📚 Component Documentation

### CurrencyContext
Provides global currency state management.

**Usage:**
```javascript
import { useCurrency } from '../context/CurrencyContext'

function MyComponent() {
  const { currency, setCurrency, getCurrencySymbol } = useCurrency()
  
  return <div>{getCurrencySymbol()} 1000</div>
}
```

**Available Methods:**
- `currency` - Current selected currency
- `setCurrency(curr)` - Update currency
- `getCurrencySymbol()` - Get currency symbol
- `getCurrencyLabel()` - Get currency label
- `getCurrencyName()` - Get currency full name
- `currencyOptions` - Array of all currency options

### Sidebar Component
Navigation sidebar with active page highlighting.

**Features:**
- Active route highlighting
- Responsive collapse/expand
- Icon support
- Two-section menu (Main & Other)

### Weather Page
Interactive weather forecasting with maps.

**Features:**
- Location search with autocomplete suggestions
- OpenStreetMap integration
- Temperature unit toggle
- Real-time weather display
- Error handling and user guidance

---

## 🐛 Troubleshooting

### Issue: Map not displaying
```bash
# Verify leaflet installation
npm list react-leaflet leaflet

# Reinstall if needed
npm install react-leaflet@4.2.1 leaflet@1.9.4
```

### Issue: Currency not persisting
- Check browser localStorage is enabled
- Verify CurrencyProvider wraps your app
- Check browser console for errors

### Issue: Weather search not working
- Verify location name matches supported cities
- Try full format: "Sydney, Australia"
- Check browser console for error messages

### Issue: Icons not displaying
```bash
npm install @mui/icons-material@latest
```

---

## 📋 Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Full support |
| Firefox | 88+ | ✅ Full support |
| Safari | 14+ | ✅ Full support |
| Edge | 90+ | ✅ Full support |
| Mobile Chrome | Latest | ✅ Responsive |
| Mobile Safari | Latest | ✅ Responsive |

---

## 🔐 Security Notes

- **localStorage**: Used only for non-sensitive user preferences
- **API Keys**: Should be stored in backend environment variables
- **CORS**: Configure for production environment
- **Input Validation**: Implement server-side validation

---

## 📝 License

This project is licensed under the MIT License - see LICENSE.md for details.

---

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/yourusername/issues) page.

---

**Last Updated:** September 27, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
