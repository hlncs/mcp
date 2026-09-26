# Dependencies

Complete list of all project dependencies, their purposes, and installation instructions.

---

## Frontend Dependencies

### Core Framework
```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "react-router-dom": "^6.x"
}
```

**Purpose:**
- **react** - UI library for building interactive components
- **react-dom** - React rendering engine for web browsers
- **react-router-dom** - Client-side routing and navigation between pages

**Why These Versions:**
- React 18.3.1 - Latest stable version with hooks and concurrent features
- React Router 6.x - Latest major version with modern API

---

### UI Components & Styling
```json
{
  "@mui/material": "^5.x",
  "@mui/icons-material": "^5.x"
}
```

**Purpose:**
- **@mui/material** - Material Design component library (Cards, Buttons, Typography, Grid, etc.)
- **@mui/icons-material** - 5000+ Material Design icons (CloudIcon, EventIcon, MoneyIcon, etc.)

**Features Provided:**
- Pre-built responsive components
- Consistent design system
- Built-in styling with sx prop
- Accessibility support

---

### Maps & Location Features
```json
{
  "react-leaflet": "^4.2.1",
  "leaflet": "^1.9.4"
}
```

**Purpose:**
- **react-leaflet** - React wrapper for Leaflet, simplifies map integration
- **leaflet** - Lightweight interactive mapping library with OpenStreetMap support

**Features:**
- Interactive OpenStreetMap display
- Location markers and popups
- Zoom and pan controls
- Free, no API key required

**⚠️ Version Warning:**
- Do NOT use react-leaflet@5.x (requires React 19)
- Use react-leaflet@4.2.1 (compatible with React 18)

---

### Build Tool & Development
```json
{
  "vite": "^5.x",
  "@vitejs/plugin-react": "^4.x"
}
```

**Purpose:**
- **vite** - Ultra-fast build tool and dev server
- **@vitejs/plugin-react** - React Fast Refresh for instant HMR (Hot Module Replacement)

**Features:**
- Lightning-fast dev server startup
- Instant file update reflection
- Optimized production builds
- ES modules by default

---

### Optional Dev Dependencies
```json
{
  "eslint": "^8.x",
  "prettier": "^3.x"
}
```

**Purpose:**
- **eslint** - Code quality and style linting
- **prettier** - Code formatter for consistent style

---

## Installation Command

### Basic Installation
```bash
cd /Users/hien.luong/Projects/AI/mcp/frontend
npm install
```

### Full Installation with All Dependencies
```bash
npm install react@18.3.1 react-dom@18.3.1 react-router-dom@6.x \
  @mui/material@5.x @mui/icons-material@5.x \
  react-leaflet@4.2.1 leaflet@1.9.4 \
  vite@5.x @vitejs/plugin-react@4.x eslint@8.x prettier@3.x
```

### Verify Installation
```bash
npm list react @mui/material react-leaflet leaflet
```

Expected output:
```
├── react@18.3.1
├── @mui/material@5.x
├── react-leaflet@4.2.1
└── leaflet@1.9.4
```

---

## Backend Dependencies (Optional)

For building a REST API backend for the Event Management Suite.

### Core Framework
```python
Flask==3.0.0
Flask-CORS==4.0.0
python-dotenv==1.0.0
```

**Purpose:**
- **Flask** - Lightweight Python web framework
- **Flask-CORS** - Handle Cross-Origin Resource Sharing
- **python-dotenv** - Load environment variables from .env file

### Database Support
```python
Flask-SQLAlchemy==3.0.5
SQLAlchemy==2.0.23
```

**Purpose:**
- Database ORM for event, budget, and user data
- Support for SQLite, PostgreSQL, MySQL

### API Documentation
```python
Flasgger==0.9.7.1
```

**Purpose:**
- Auto-generate Swagger/OpenAPI documentation
- Interactive API testing interface

### Weather API Integration
```python
requests==2.31.0
```

**Purpose:**
- HTTP library for calling external weather APIs

### Testing
```python
pytest==7.4.3
pytest-cov==4.1.0
```

**Purpose:**
- Unit testing framework
- Code coverage reporting

### Installation
```bash
cd /Users/hien.luong/Projects/AI/mcp/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Version Compatibility Matrix

| Package | Version | React | Node | NPM | Reason |
|---------|---------|-------|------|-----|--------|
| react | 18.3.1 | - | 16+ | 8+ | Latest stable React 18 |
| react-dom | 18.3.1 | - | 16+ | 8+ | Must match React version |
| react-router-dom | 6.x | 16.8+ | 12+ | 6+ | Modern routing API |
| @mui/material | 5.x | 16.8+ | 12+ | 6+ | Material Design components |
| @mui/icons-material | 5.x | - | 12+ | 6+ | Material Design icons |
| react-leaflet | 4.2.1 | 18.x | 14+ | 6+ | ⚠️ NOT v5 (requires React 19) |
| leaflet | 1.9.4 | - | 12+ | 6+ | Base mapping library |
| vite | 5.x | - | 14.8+ | 6+ | Modern build tool |

---

## Known Issues & Solutions

### Issue 1: react-leaflet Version Conflict

**Error:**
```
npm error ERESOLVE unable to resolve dependency tree
npm error peer react@"^19.0.0" from react-leaflet@5.0.0
```

**Root Cause:**
- react-leaflet@5 requires React 19
- Project uses React 18

**Solution:**
```bash
# Use compatible version
npm install react-leaflet@4.2.1 leaflet@1.9.4

# DO NOT USE these:
npm install react-leaflet@latest  # Would install v5
npm install react-leaflet --force  # Ignores peer dependencies
```

**Alternative (Not Recommended):**
```bash
# Only if you must upgrade React
npm install react@19 react-dom@19 react-leaflet leaflet
```

---

### Issue 2: Material-UI Icons Not Displaying

**Error:** Icons show as empty or don't render

**Solution:**
```bash
npm install @mui/icons-material@latest

# Verify installation
npm list @mui/icons-material
```

---

### Issue 3: Leaflet Map Not Showing

**Symptoms:**
- Blank gray area where map should be
- Console errors about Leaflet resources

**Solution:**
```bash
# 1. Verify versions
npm list react-leaflet leaflet

# 2. Clear browser cache
# 3. Verify Leaflet CSS is imported in component
import 'leaflet/dist/leaflet.css'

# 4. Reinstall if needed
rm -rf node_modules package-lock.json
npm install
```

---

### Issue 4: Currency Context Not Persisting

**Symptoms:**
- Currency selection resets on page refresh
- Different currency displays on different pages

**Solution:**
1. Verify `CurrencyContext.jsx` uses `localStorage`
2. Verify `CurrencyProvider` wraps entire app in `App.jsx`
3. Check browser localStorage is enabled
4. Check browser console for errors

```javascript
// Verify in browser console
localStorage.getItem('selectedCurrency')  // Should return 'usd', 'eur', etc.
```

---

### Issue 5: npm install Fails

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Remove old dependencies
rm -rf node_modules package-lock.json

# Reinstall
npm install

# If peer dependency conflicts persist
npm install --legacy-peer-deps
```

---

## Dependency Update Guidelines

### Frontend Updates
```bash
# Check for outdated packages
npm outdated

# Update all non-major versions
npm update

# Update specific package
npm install @mui/material@5.14.0

# Major version update (be careful!)
npm install @mui/material@6  # Will bump major version
```

### Backend Updates
```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade Flask==3.1.0

# Update all packages
pip install -r requirements.txt --upgrade
```

---

## Project File Structure

```
frontend/
├── node_modules/          # Installed dependencies (git ignored)
├── public/                # Static assets
├── src/
│   ├── components/        # Reusable components
│   ├── context/           # React Context (CurrencyContext)
│   ├── pages/             # Page components
│   ├── App.jsx            # Main app component
│   ├── main.jsx           # Entry point
│   └── index.css           # Global styles
├── package.json           # Dependencies list
├── package-lock.json      # Locked versions (git tracked)
├── vite.config.js         # Vite configuration
└── .gitignore             # Files to ignore in git
```

---

## Lock Files

### package-lock.json
- **Purpose:** Locks exact versions of all npm dependencies
- **Should be committed:** YES (in version control)
- **When to regenerate:** After `npm install` or `npm update`

### package.json
- **Purpose:** Lists direct project dependencies with version ranges
- **Should be committed:** YES
- **When to update:** When adding new packages with `npm install package-name`

### requirements.txt (Backend)
- **Purpose:** Locks exact versions of Python dependencies
- **Should be committed:** YES
- **Generate with:** `pip freeze > requirements.txt`

---

## Performance Optimization

### Bundle Size
```bash
# Analyze bundle size
npm run build

# Use vite's built-in analysis
npm install -D vite-plugin-visualizer
```

### Lazy Loading
Implemented in React Router for code splitting:
```javascript
const EventPlannerPage = lazy(() => import('./pages/EventPlannerPage'))
```

---

## Security Considerations

### npm Vulnerabilities
```bash
# Check for security vulnerabilities
npm audit

# Fix automatically (if possible)
npm audit fix

# Fix with major version changes
npm audit fix --force
```

### Backend Security
```bash
# Check Python packages
pip install safety
safety check
```

---

## Troubleshooting Checklist

- [ ] Node version: `node --version` (should be 16+)
- [ ] npm version: `npm --version` (should be 8+)
- [ ] Clear cache: `npm cache clean --force`
- [ ] Delete node_modules: `rm -rf node_modules`
- [ ] Delete lock file: `rm package-lock.json`
- [ ] Reinstall: `npm install`
- [ ] Check for typos in package names
- [ ] Use exact version numbers from DEPENDENCIES.md
- [ ] Verify no conflicting global packages

---

## Support & Resources

- **React Docs:** https://react.dev
- **Material-UI Docs:** https://mui.com/material-ui/getting-started/
- **Leaflet Docs:** https://leafletjs.com/
- **Vite Docs:** https://vitejs.dev/
- **npm Registry:** https://www.npmjs.com/

---

**Last Updated:** September 27, 2026  
**Maintained By:** Development Team  
**Status:** Active & Current