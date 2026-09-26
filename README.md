# Event Planning System - AI-Powered Multi-Agent Orchestration

A comprehensive event planning application powered by AI agents, featuring real-time progress streaming, weather forecasting, budget management, and intelligent service coordination.

## 🎯 Project Overview

This project implements a sophisticated multi-agent system using **Model Context Protocol (MCP)** to orchestrate AI agents for event planning. It combines a Python FastAPI backend with a React frontend, enhanced with **Server-Sent Events (SSE)** for real-time progress streaming.

**Key Features:**
- 🤖 Multi-agent orchestration (10+ specialized agents)
- ⚡ Real-time progress streaming with SSE
- 🌦️ Real-time weather forecasting
- 💰 Smart budget management & validation
- 🏨 Comprehensive service search (hotels, venues, flights, catering, etc.)
- 📋 AI-powered event planning
- 🎨 Modern React UI with Material-UI
- 🔌 MCP Server integration
- 📡 Live event tracking dashboard

## 📁 Project Structure

```
mcp/
├── backend/
│   ├── main.py                      # FastAPI application with SSE endpoints
│   └── sse.py                       # Server-Sent Events implementation
├── config/
│   ├── agents.py                    # Agent configurations & routing
│   └── __init__.py
├── mcp_servers/
│   ├── mock_data.py                 # Mock data provider & business logic
│   ├── event_planning_server.py     # MCP server with tool definitions
│   ├── tools.py                     # Tool schemas for all services
│   └── __init__.py
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── EventPlannerPage.jsx          # Main planning interface
│   │   │   ├── WeatherPage.jsx
│   │   │   ├── BudgetPage.jsx
│   │   │   └── ServiceSearchPage.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── EventStreamViewer.jsx         # Real-time progress viewer
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── .env.example
├── .gitignore
├── README.md
└── prompt.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** & **npm 9+**
- **Git**

### Backend Setup

```bash
# Navigate to project directory
cd /path/toProjects/AI/mcp

# Install Python dependencies
pip install fastapi uvicorn pydantic python-dotenv

# Start backend server
python backend/main.py
```

Backend runs on: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: **http://localhost:3000**

### Running Both Services

**Terminal 1 - Backend:**
```bash
cd /path/toProjects/AI/mcp
python backend/main.py
```

**Terminal 2 - Frontend:**
```bash
cd /path/toProjects/AI/mcp/frontend
npm run dev
```

Then access the application at: **http://localhost:3000** 🎉

## ⚡ Real-Time Streaming with SSE

The system uses **Server-Sent Events (SSE)** for real-time progress updates during event planning:

### Real-Time Event Flow

```
┌──────────────────┐
│   React Browser  │
│   (EventSource)  │
└────────┬─────────┘
         │ Subscribe to /stream/plan/{plan_id}
         │
┌────────▼─────────────────────┐
│   FastAPI Backend            │
│   - PlanningEventTracker     │
│   - EventStream Manager      │
└────────┬─────────────────────┘
         │
         ├─► log_step("validation", "started")
         ├─► log_step("weather_check", "started")
         ├─► log_step("venue_search", "completed")
         ├─► log_step("catering_search", "completed")
         └─► log_step("planning", "completed")
         
┌────────▼─────────────────────┐
│   Real-time Updates          │
│   ✓ Progress tracking        │
│   ✓ Status indicators        │
│   ✓ Error handling           │
└──────────────────────────────┘
```

### Planning Steps

When creating an event plan via `/plan/create-stream`, the system logs:

1. **Validation** - Checking input parameters
2. **Weather Check** - Fetching weather forecast
3. **Venue Search** - Finding available venues
4. **Catering Search** - Finding catering services
5. **Entertainment Search** - Finding entertainment options
6. **Plan Creation** - Generating comprehensive plan
7. **Summary Generation** - Creating event summary

Each step emits `started` and `completed` events with relevant details.

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Health Check
```bash
GET /health

Response: {
  "status": "healthy",
  "timestamp": "2026-09-26T10:30:00",
  "service": "Event Planning API"
}
```

### Agents
```bash
# List all agents
GET /agents

# Get agent routing configuration
GET /agents/routing
```

### Weather
```bash
POST /weather
Content-Type: application/json

Request:
{
  "location": "Sydney, Australia",
  "date": "2026-10-15"
}

Response:
{
  "location": "Sydney, Australia",
  "date": "2026-10-15",
  "temperature": 22,
  "condition": "sunny",
  "confidence": 0.85,
  "humidity": 55,
  "wind_speed": 12,
  "is_favorable": true
}
```

### Event Planning - With Streaming
```bash
POST /plan/create-stream
Content-Type: application/json

Request:
{
  "event_type": "wedding",
  "location": "Sydney, Australia",
  "date": "2026-10-15",
  "guest_count": 100,
  "budget": 50000
}

Response:
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "stream_url": "/stream/plan/550e8400-e29b-41d4-a716-446655440000",
  "plan": {...},
  "summary": {...}
}

# Then open EventSource to:
# http://localhost:8000/stream/plan/550e8400-e29b-41d4-a716-446655440000
```

### Event Planning - Standard (No Streaming)
```bash
POST /plan/create
Content-Type: application/json

Request:
{
  "event_type": "wedding",
  "location": "Sydney, Australia",
  "date": "2026-10-15",
  "guest_count": 100,
  "budget": 50000
}

Response:
{
  "plan": {...},
  "summary": {...},
  "created_at": "2026-09-26T10:30:00"
}
```

### Event Streaming
```bash
# Stream specific plan events
GET /stream/plan/{plan_id}

# Stream global events
GET /stream/global

# Returns: text/event-stream with JSON objects
```

### Services Search
```bash
POST /search/services?service_type=hotels&location=Sydney

Request:
{
  "service_type": "hotels",
  "location": "Sydney, Australia"
}

Response:
{
  "service_type": "hotels",
  "location": "Sydney, Australia",
  "results": [...],
  "count": 3
}
```

### All Services
```bash
GET /services/all?location=Sydney

Response:
{
  "location": "Sydney, Australia",
  "services": {
    "hotels": [...],
    "venues": [...],
    "catering": [...],
    "entertainment": [...],
    "transportation": [...]
  }
}
```

### Budget Validation
```bash
POST /budget/validate
Content-Type: application/json

Request:
{
  "allocated_budget": 50000,
  "calculated_cost": 45000
}

Response:
{
  "allocated_budget": 50000,
  "calculated_cost": 45000,
  "remaining": 5000,
  "percentage_used": 90.0,
  "status": "within_budget",
  "warning": null
}
```

### Reservations
```bash
POST /reservation/make
Content-Type: application/json

Request:
{
  "service_type": "hotel",
  "service_id": "h001",
  "details": {
    "check_in": "2026-10-15",
    "check_out": "2026-10-17",
    "rooms": 2
  }
}

Response:
{
  "reservation_id": "RES12345",
  "service_type": "hotel",
  "service_id": "h001",
  "status": "confirmed",
  "booking_date": "2026-09-26T10:30:00",
  "confirmation_code": "CONF1234"
}
```

## 🎨 Frontend Pages

### Home Page
- Overview of system features
- Quick navigation cards
- Feature descriptions

### Event Planner
- Event details form (type, location, date, guests, budget)
- Real-time progress streaming with EventStreamViewer
- Event plan summary with cost breakdown
- Budget status indicator

### Weather
- Location & date input
- Weather forecast display
- Suitability for outdoor events
- Temperature, humidity, wind speed

### Budget Manager
- Budget input forms
- Cost breakdown analysis
- Linear progress visualization
- Budget status (within/over budget)
- Warnings for high usage

### Service Search
- Service type selector
- Location input
- Results table display
- Filtering capabilities

## 🤖 Agent System

| Agent | Description | Skills |
|-------|-------------|--------|
| **Planner** | Main orchestrator | Event management, coordination |
| **Weather Forecaster** | Weather analysis | Forecast retrieval, analysis |
| **Venue Booker** | Venue coordination | Venue search, booking |
| **Catering Service** | Food & beverage | Menu selection, pricing |
| **Entertainment Coordinator** | Entertainment | Booking, coordination |
| **Hotel Reservation Agent** | Accommodation | Hotel search, booking |
| **Transportation Coordinator** | Travel logistics | Transport search, booking |
| **Flight Booking Agent** | Air travel | Flight search, booking |
| **Budget Manager** | Financial management | Cost tracking, analysis |
| **Plan Summarizer** | Report generation | Summary creation |

## 📦 Build & Deployment

### Build Frontend
```bash
cd frontend
npm run build
```

Output: `frontend/dist/`

### Production Server
```bash
cd /path/toProjects/AI/mcp
python backend/main.py --host 0.0.0.0 --port 8000
```

## 🧪 Testing

### Test SSE Connection
```javascript
// In browser console
const es = new EventSource('http://localhost:8000/stream/global');
es.onmessage = (e) => console.log(JSON.parse(e.data));
```

### Test Event Plan Creation
```bash
curl -X POST http://localhost:8000/plan/create-stream \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "conference",
    "location": "Sydney, Australia",
    "date": "2026-11-20",
    "guest_count": 200,
    "budget": 100000
  }'
```

### Test in Frontend
1. Navigate to http://localhost:3000/planner
2. Fill out event form
3. Click "Create Plan"
4. Watch progress in EventStreamViewer
5. View final summary

## 📋 Environment Variables

Create `.env` file:

```env
# Backend
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
LOG_LEVEL=INFO

# Weather
OPENMETEO_API_URL=https://api.open-meteo.com/v1
WEATHER_CONFIDENCE_THRESHOLD=0.80
IDEAL_TEMP_MIN=20
IDEAL_TEMP_MAX=25

# Frontend (.env in frontend/ directory)
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Event Planning System

# SSE Configuration (in milliseconds)
VITE_SSE_TIMEOUT=30000          # Connection timeout (default: 30s)
VITE_SSE_WARNING=10000          # Warning threshold (default: 10s)
```

### SSE Timeout Configuration

The EventStreamViewer component has configurable timeouts:

| Setting | Default | Description |
|---------|---------|-------------|
| `timeoutMs` | 30000 ms | Total timeout before connection is considered failed |
| `warningMs` | 10000 ms | Show warning to user after this delay |
| `autoRetry` | true | Automatically retry on failure |
| `maxRetries` | 3 | Maximum number of retry attempts |

**Set via environment variables or component props:**

```jsx
<EventStreamViewer
  planId={planId}
  timeoutMs={60000}        // 60 seconds
  warningMs={15000}        // Warn after 15 seconds
  autoRetry={true}
  maxRetries={5}
  onTimeout={(data) => console.log('Timeout:', data)}
  onError={(data) => console.error('Error:', data)}
/>
```

## 📚 Dependencies

### Backend
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **python-dotenv** - Environment management

### Frontend
- **react** - UI library
- **react-router-dom** - Routing
- **@mui/material** - UI components
- **axios** - HTTP client
- **vite** - Build tool

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│       React Frontend (Port 3000)        │
│  ├── HomePage                           │
│  ├── EventPlannerPage (SSE Consumer)   │
│  ├── WeatherPage                        │
│  ├── BudgetPage                         │
│  └── ServiceSearchPage                  │
│                                         │
│  Components:                            │
│  ├── Navbar                             │
│  ├── Sidebar                            │
│  └── EventStreamViewer (SSE Viewer)    │
└──────────────┬──────────────────────────┘
               │ HTTP/REST + SSE
               ▼
┌─────────────────────────────────────────┐
│     FastAPI Backend (Port 8000)         │
│  ├── REST Endpoints                     │
│  ├── SSE Event Streaming                │
│  ├── PlanningEventTracker               │
│  └── EventStream Manager                │
│                                         │
│  Modules:                               │
│  ├── main.py (FastAPI app)             │
│  ├── sse.py (Real-time events)         │
│  └── config/ (Agents & routing)        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    MCP Servers & Mock Data              │
│  ├── event_planning_server.py           │
│  ├── mock_data.py                       │
│  └── tools.py                           │
└─────────────────────────────────────────┘
```

## 🔐 Security

- Environment variables for sensitive data
- Input validation on all endpoints
- CORS configured for development (restrict in production)
- SSE connections validated by plan_id
- Error messages don't expose internals

## 🚦 Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Plan created successfully |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Unexpected error |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 📞 Support

- Check README.md for documentation
- Review prompt.md for development guidelines
- Check API docs at http://localhost:8000/docs
- Review existing endpoints for patterns

## 🗺️ Roadmap

### Phase 1 (✅ Complete)
- [x] MVP with FastAPI backend
- [x] React frontend with Material-UI
- [x] Mock data providers
- [x] Basic agent system
- [x] SSE real-time streaming
- [x] EventStreamViewer component

### Phase 2 (🔄 In Progress)
- [ ] Real database (PostgreSQL)
- [ ] User authentication
- [ ] Persistent storage
- [ ] Real LLM integration

### Phase 3 (📋 Planned)
- [ ] Payment integration (Stripe)
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Calendar integration
- [ ] Admin dashboard
- [ ] Reporting & analytics

### Phase 4 (🎯 Future)
- [ ] Mobile app (React Native)
- [ ] WebSockets for full-duplex communication
- [ ] Advanced search filters
- [ ] Recommendation engine
- [ ] Review & ratings system
- [ ] Multi-language support

## 📖 Documentation

- **API Docs:** http://localhost:8000/docs (Swagger)
- **README.md** - This file
- **prompt.md** - Development guidelines
- **Code comments** - Inline documentation

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Must be 3.11+

# Check dependencies
pip list | grep fastapi

# Reinstall
pip install -r requirements.txt
```

### Frontend won't load
```bash
# Clear node_modules
rm -rf node_modules
npm install

# Check Node version
node --version  # Must be 18+
```

### SSE not connecting
```bash
# Check backend is running
curl http://localhost:8000/health

# Check browser console for errors
# Check network tab for EventSource requests
```

### Services not appearing
```bash
# Check mock data provider
# Verify endpoint is called correctly
# Check browser network tab for responses
```

## 📞 Performance Tips

- SSE connections are persistent (not polling)
- Mock data is lightweight
- Async endpoints handle concurrent requests
- Frontend lazy-loads pages
- Material-UI uses CSS-in-JS for optimization

## 🎓 Learning Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Material-UI Docs](https://mui.com/)
- [SSE Guide](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [MCP Protocol](https://modelcontextprotocol.io/)

---

**Project Created:** September 26, 2026  
**Last Updated:** September 26, 2026  
**Status:** MVP Complete with Real-Time Streaming  
**Version:** 1.0.0

Made with ❤️ for event planning