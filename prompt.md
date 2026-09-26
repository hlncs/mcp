# Event Planning System - AI Assistant Prompt

## System Context

You are an AI programming assistant helping with the **Event Planning System** - a comprehensive multi-agent event planning application built with:
- **Backend:** Python FastAPI + MCP (Model Context Protocol) + SSE (Server-Sent Events)
- **Frontend:** React + Material-UI + EventSource API
- **Infrastructure:** Mock data providers + agent orchestration + real-time streaming

## Project Structure

```
/path/to/Projects/AI/mcp/
├── backend/
│   ├── main.py                  # FastAPI server with SSE endpoints
│   └── sse.py                   # Server-Sent Events implementation
├── config/
│   └── agents.py                # Agent configurations
├── mcp_servers/
│   ├── mock_data.py            # Mock data & business logic
│   ├── event_planning_server.py # MCP tool definitions
│   └── tools.py                 # Tool schemas
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── EventPlannerPage.jsx  # Main event creation page
│   │   │   ├── WeatherPage.jsx
│   │   │   ├── BudgetPage.jsx
│   │   │   └── ServiceSearchPage.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── EventStreamViewer.jsx  # Real-time progress viewer
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── vite.config.js
│   ├── package.json
│   └── index.html
├── .gitignore
├── README.md
└── prompt.md
```

## Current Implementation Status

### ✅ Fully Implemented

**Backend**
- 10+ REST API endpoints
- SSE streaming for real-time plan creation
- Mock data provider with all services
- Agent configuration system
- Weather forecasting
- Budget validation
- Event planning orchestration
- Service search & filtering
- Real-time event tracking

**Frontend**
- 5 main pages with navigation
- Event creation form with streaming progress
- Real-time EventStreamViewer component
- Weather display with forecasts
- Budget analysis with visualization
- Service search with table display
- Material-UI components throughout
- Responsive design

**Real-Time Features**
- Server-Sent Events (SSE) implementation
- Plan creation progress tracking
- Step-by-step event logging
- Live connection status indicator
- Error handling with reconnection support

### 🔄 Partially Implemented

**MCP Server**
- Tool schemas fully defined (12+ tools)
- Tool dispatcher implemented
- Async operation support
- Needs real LLM integration

**Agent System**
- Agent routing configured
- Agent definitions created
- Needs actual AI model integration

## Available Commands

### Start All Services

**Terminal 1 - Backend:**
```bash
cd /path/to/Projects/AI/mcp
pip install fastapi uvicorn pydantic python-dotenv
python backend/main.py
```

**Terminal 2 - Frontend:**
```bash
cd /path/to/Projects/AI/mcp/frontend
npm install
npm run dev
```

**Access Application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List agents
curl http://localhost:8000/agents

# Get weather
curl -X POST http://localhost:8000/weather \
  -H "Content-Type: application/json" \
  -d '{"location":"Sydney, Australia","date":"2026-10-15"}'

# Create event plan (with streaming)
curl -X POST http://localhost:8000/plan/create-stream \
  -H "Content-Type: application/json" \
  -d '{
    "event_type":"wedding",
    "location":"Sydney, Australia",
    "date":"2026-10-15",
    "guest_count":100,
    "budget":50000
  }'

# Standard event plan (no streaming)
curl -X POST http://localhost:8000/plan/create \
  -H "Content-Type: application/json" \
  -d '{
    "event_type":"wedding",
    "location":"Sydney, Australia",
    "date":"2026-10-15",
    "guest_count":100,
    "budget":50000
  }'
```

## Real-Time Streaming (SSE)

### How It Works

1. **Frontend** submits event plan via `/plan/create-stream`
2. **Backend** returns `plan_id` and creates `EventStreamViewer`
3. **Frontend** opens EventSource connection to `/stream/plan/{plan_id}`
4. **Backend** publishes progress events in real-time:
   - validation (started/completed)
   - weather_check (started/completed)
   - venue_search (started/completed)
   - catering_search (started/completed)
   - entertainment_search (started/completed)
   - plan_creation (started/completed)
   - summary_generation (started/completed)
   - planning (completed/error)
5. **Frontend** displays events as they arrive with status icons

### SSE Event Format

```json
{
  "plan_id": "uuid-here",
  "step": "venue_search",
  "status": "completed",
  "details": {
    "count": 3
  },
  "timestamp": 1234567890.123
}
```

## Code Structure Guidelines

### Adding New Endpoints

1. **Define Pydantic model:**
```python
class MyRequest(BaseModel):
    field1: str
    field2: int
```

2. **Add endpoint in `backend/main.py`:**
```python
@app.post("/my-endpoint")
async def my_endpoint(request: MyRequest):
    try:
        # Your logic
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

3. **Call from frontend with axios:**
```javascript
const response = await axios.post(`${API_BASE_URL}/my-endpoint`, data)
```

### Adding Real-Time Tracking

1. **Create tracker in endpoint:**
```python
tracker = PlanningEventTracker(plan_id)
await tracker.log_step("step_name", "started", {"detail": "value"})
await tracker.log_step("step_name", "completed", {"detail": "value"})
```

2. **Use EventStreamViewer in React:**
```jsx
<EventStreamViewer planId={plan_id} />
```

### Adding New Pages

1. **Create component in `frontend/src/pages/`**
2. **Add route in `frontend/src/App.jsx`:**
```jsx
<Route path="/my-page" element={<MyPage />} />
```
3. **Add menu item in `frontend/src/components/Sidebar.jsx`:**
```jsx
{ text: 'My Page', icon: <MyIcon />, path: '/my-page' }
```

### Adding New Mock Services

1. **Add method to `MockDataServer` in `mcp_servers/mock_data.py`:**
```python
@staticmethod
def get_my_service(location: str, param: int) -> List[Dict[str, Any]]:
    """Service description"""
    return [...]
```

2. **Add endpoint in `backend/main.py`:**
```python
@app.post("/search/my-service")
async def search_my_service(location: str, param: int):
    try:
        results = MockDataServer.get_my_service(location, param)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Component Reference

### EventStreamViewer
**Purpose:** Display real-time plan creation progress

**Props:**
- `planId` (string): The plan ID to stream events for

**Usage:**
```jsx
<EventStreamViewer planId={plan.plan_id} />
```

**Features:**
- Real-time event display
- Connection status indicator
- Icon-based status visualization (started/completed/error)
- Automatic event parsing
- Error handling

### EventPlannerPage
**Purpose:** Main event creation interface

**State:**
- `formData`: Event form inputs
- `plan`: Created plan data
- `loading`: Form submission state
- `error`: Error messages

**Flow:**
1. User fills form
2. Submit triggers `/plan/create-stream`
3. EventStreamViewer shows progress
4. Summary displays when complete

## Key Files & Their Purpose

| File | Purpose | Key Functions |
|------|---------|---------------|
| `backend/main.py` | FastAPI server | REST endpoints, SSE setup |
| `backend/sse.py` | Real-time events | EventStream, PlanningEventTracker |
| `config/agents.py` | Agent definitions | AGENTS, AGENT_ROUTING_CONFIG |
| `mcp_servers/mock_data.py` | Business logic | All search/create methods |
| `mcp_servers/event_planning_server.py` | MCP tools | Tool schemas & dispatcher |
| `mcp_servers/tools.py` | Tool definitions | Tool specs for each service |
| `frontend/src/App.jsx` | Main component | Routing, theming |
| `frontend/src/pages/EventPlannerPage.jsx` | Event creation | Form + streaming |
| `frontend/src/components/EventStreamViewer.jsx` | SSE viewer | Real-time display |

## Common Tasks

### Create Event Plan with Real-Time Progress
```javascript
// Frontend
const response = await axios.post(
  `${API_BASE_URL}/plan/create-stream`,
  {
    event_type: "wedding",
    location: "Sydney",
    date: "2026-10-15",
    guest_count: 100,
    budget: 50000
  }
)

// Display stream
<EventStreamViewer planId={response.data.plan_id} />
```

### Add New Planning Step
```python
# In event_planning_server.py endpoint
await tracker.log_step("my_step", "started", {"info": "value"})
# ... do work ...
await tracker.log_step("my_step", "completed", {"result": "value"})
```

### Subscribe to Global Events
```javascript
useEffect(() => {
  const eventSource = new EventSource('http://localhost:8000/stream/global')
  eventSource.onmessage = (e) => {
    console.log(JSON.parse(e.data))
  }
}, [])
```

### Broadcast Event to All Clients
```python
await event_stream.broadcast({
  "type": "announcement",
  "message": "New feature available"
})
```

## Performance Considerations

- SSE connections are persistent (not HTTP polling)
- Mock data generated on-the-fly (minimal memory)
- No database queries (instant responses)
- Async endpoints handle concurrent requests
- Each SSE stream maintains separate queue
- Memory scales with connected clients

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads on localhost:3000
- [ ] Health check returns 200 status
- [ ] Can create event plan
- [ ] Real-time progress appears in EventStreamViewer
- [ ] Weather displays correctly
- [ ] Budget validation works
- [ ] Service search returns results
- [ ] SSE connection shows "Connected" status
- [ ] No console errors in browser or terminal

## Debugging Tips

**SSE Not Connecting?**
- Check backend is running on :8000
- Verify CORS headers in main.py
- Check browser console for errors
- Look at backend logs for EventSource errors

**Events Not Appearing?**
- Verify plan_id matches stream endpoint
- Check event_stream.publish calls
- Monitor network tab for SSE messages
- Check EventStreamViewer component props

**Performance Issues?**
- Monitor memory with `free -h`
- Check for open file descriptors
- Review backend logs for errors
- Profile with browser DevTools

## API Response Format

All endpoints return JSON:

**Success:**
```json
{
  "plan_id": "uuid",
  "stream_url": "/stream/plan/uuid",
  "plan": {...},
  "summary": {...},
  "created_at": "2026-09-26T10:30:00"
}
```

**Error:**
```json
{
  "detail": "Error message"
}
```

**SSE Event:**
```json
{
  "plan_id": "uuid",
  "step": "step_name",
  "status": "started|completed|error",
  "details": {...},
  "timestamp": 1234567890.123
}
```

## Security Reminders

- ❌ Never hardcode secrets
- ❌ Don't commit `.env` files
- ❌ Don't expose internal IDs directly
- ✅ Use environment variables
- ✅ Validate all inputs
- ✅ Sanitize API responses
- ✅ Use HTTPS in production
- ✅ Implement rate limiting

## Deployment Notes

**Production Checklist:**
- [ ] Set CORS to specific domains only
- [ ] Use environment variables for config
- [ ] Enable HTTPS with SSL certificates
- [ ] Set up logging to files
- [ ] Configure rate limiting
- [ ] Use proper database instead of mocks
- [ ] Add authentication/authorization
- [ ] Set up monitoring & alerts
- [ ] Configure nginx reverse proxy
- [ ] Use systemd or supervisor for process management

## Next Steps for Enhancement

1. **Real Database:** PostgreSQL + SQLAlchemy ORM
2. **Authentication:** JWT tokens + user accounts
3. **Payments:** Stripe integration for bookings
4. **Real LLM:** Claude API or GPT-4 for agents
5. **Notifications:** Email/SMS alerts via SendGrid/Twilio
6. **File Storage:** AWS S3 for images/documents
7. **Testing:** pytest for backend, Jest for frontend
8. **CI/CD:** GitHub Actions pipeline
9. **Docker:** Containerization for deployment
10. **WebSockets:** Full-duplex real-time communication

---

**Last Updated:** September 26, 2026  
**Status:** MVP Complete with Real-Time Streaming  
**Next Phase:** Database Persistence + Real LLM Integration