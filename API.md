# MCP API Documentation

## Overview

FastAPI-based Model Context Protocol implementation with full observability and testing.

## Quick Start

```bash
# Activate environment
source .venv/bin/activate

# Start server
python -m uvicorn backend.main:app --reload

# Run tests
pytest [test_main.py](http://_vscodecontentref_/0) -v

# Open API docs
open http://localhost:8000/docs
```

---

## Commit Documentation

```bash
cd /path/to//Projects/AI/mcp

git add API.md
git commit -m "docs: Add comprehensive API documentation

- Endpoint reference with curl examples
- Request/response examples
- Testing instructions
- Project structure overview
- Technology stack
- Performance metrics

Ready for team onboarding and deployment"

git push
```

# API Documentation

## Overview

The Event Management Suite uses a frontend-only architecture with mock data. Optional backend API endpoints are documented below for future implementation.

---

## Weather API

### Mock Data (Current Implementation)

**Supported Locations:**
- Sydney, Australia
- New York, USA
- London, UK
- Tokyo, Japan
- Paris, France

**Data Structure:**
```javascript
{
  name: "Sydney, Australia",
  lat: -33.8688,
  lng: 151.2093,
  temperature: 22,
  humidity: 65,
  windSpeed: 12,
  condition: "Partly Cloudy",
  pressure: 1013
}
```

### Search Endpoint (Future Backend)

```http
GET /api/weather/search?location=Sydney
```

**Request Parameters:**
```json
{
  "location": "Sydney, Australia",
  "units": "metric"  // or "imperial"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "Sydney, Australia",
    "lat": -33.8688,
    "lng": 151.2093,
    "temperature": 22,
    "humidity": 65,
    "windSpeed": 12,
    "condition": "Partly Cloudy",
    "pressure": 1013,
    "forecast": [
      {
        "date": "2026-09-27",
        "high": 24,
        "low": 18,
        "condition": "Sunny"
      }
    ]
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Location not found",
  "message": "Weather data not found for 'Melbourne'"
}
```

---

## Events API

### Create Event (Future Backend)

```http
POST /api/events
```

**Request Body:**
```json
{
  "name": "Summer Wedding",
  "description": "A beautiful outdoor wedding",
  "date": "2026-12-01",
  "time": "14:00",
  "location": "Sydney, Australia",
  "guestCount": 150,
  "budget": 25000
}
```

**Response:**
```json
{
  "success": true,
  "event": {
    "id": "evt_123456",
    "name": "Summer Wedding",
    "description": "A beautiful outdoor wedding",
    "date": "2026-12-01",
    "time": "14:00",
    "location": "Sydney, Australia",
    "guestCount": 150,
    "budget": 25000,
    "createdAt": "2026-09-27T10:30:00Z"
  }
}
```

---

### Get Events

```http
GET /api/events
```

**Response:**
```json
{
  "success": true,
  "events": [
    {
      "id": "evt_123456",
      "name": "Summer Wedding",
      "date": "2026-12-01",
      "location": "Sydney, Australia",
      "guestCount": 150,
      "budget": 25000
    }
  ],
  "total": 1
}
```

---

### Get Single Event

```http
GET /api/events/:id
```

**Response:**
```json
{
  "success": true,
  "event": {
    "id": "evt_123456",
    "name": "Summer Wedding",
    "description": "A beautiful outdoor wedding",
    "date": "2026-12-01",
    "time": "14:00",
    "location": "Sydney, Australia",
    "guestCount": 150,
    "budget": 25000,
    "expenses": [
      {
        "category": "Venue",
        "amount": 5000
      }
    ]
  }
}
```

---

### Update Event

```http
PUT /api/events/:id
```

**Request Body:**
```json
{
  "name": "Summer Wedding 2026",
  "guestCount": 160,
  "budget": 27000
}
```

**Response:**
```json
{
  "success": true,
  "event": { /* updated event */ }
}
```

---

### Delete Event

```http
DELETE /api/events/:id
```

**Response:**
```json
{
  "success": true,
  "message": "Event deleted successfully"
}
```

---

## Budget API

### Get Budget Breakdown

```http
GET /api/events/:id/budget
```

**Response:**
```json
{
  "success": true,
  "budget": {
    "eventId": "evt_123456",
    "total": 25000,
    "currency": "USD",
    "items": [
      {
        "category": "Venue",
        "planned": 5000,
        "spent": 4500,
        "percentage": 20
      },
      {
        "category": "Catering",
        "planned": 7500,
        "spent": 7200,
        "percentage": 30
      },
      {
        "category": "Decorations",
        "planned": 2500,
        "spent": 2300,
        "percentage": 10
      }
    ],
    "remaining": 2000
  }
}
```

---

### Add Budget Item

```http
POST /api/events/:id/budget/items
```

**Request Body:**
```json
{
  "category": "Photography",
  "amount": 1200,
  "description": "Professional photographer"
}
```

**Response:**
```json
{
  "success": true,
  "item": {
    "id": "item_789",
    "category": "Photography",
    "amount": 1200,
    "description": "Professional photographer",
    "createdAt": "2026-09-27T10:30:00Z"
  }
}
```

---

## Currency API

### Get Supported Currencies

```http
GET /api/currencies
```

**Response:**
```json
{
  "success": true,
  "currencies": [
    {
      "code": "USD",
      "symbol": "$",
      "name": "US Dollar"
    },
    {
      "code": "EUR",
      "symbol": "€",
      "name": "Euro"
    },
    {
      "code": "AUD",
      "symbol": "A$",
      "name": "Australian Dollar"
    },
    {
      "code": "JPY",
      "symbol": "¥",
      "name": "Japanese Yen"
    },
    {
      "code": "CAD",
      "symbol": "C$",
      "name": "Canadian Dollar"
    },
    {
      "code": "NZD",
      "symbol": "NZ$",
      "name": "New Zealand Dollar"
    }
  ]
}
```

---

### Convert Currency

```http
GET /api/currencies/convert?from=USD&to=EUR&amount=1000
```

**Response:**
```json
{
  "success": true,
  "conversion": {
    "from": "USD",
    "to": "EUR",
    "fromAmount": 1000,
    "toAmount": 920,
    "rate": 0.92,
    "timestamp": "2026-09-27T10:30:00Z"
  }
}
```

---

## Services API

### Get Services

```http
GET /api/services?category=Catering&location=Sydney
```

**Response:**
```json
{
  "success": true,
  "services": [
    {
      "id": "svc_123",
      "name": "Sydney Catering Co.",
      "category": "Catering",
      "location": "Sydney, Australia",
      "rating": 4.8,
      "priceRange": "$50-$100 per person",
      "phone": "+61 2 1234 5678",
      "email": "info@sydneycatering.com",
      "website": "https://sydneycatering.com"
    }
  ],
  "total": 45
}
```

---

### Get Service Categories

```http
GET /api/services/categories
```

**Response:**
```json
{
  "success": true,
  "categories": [
    "Catering",
    "Venue",
    "Photography",
    "Decoration",
    "Entertainment",
    "Transportation",
    "Flowers",
    "Cake",
    "Music"
  ]
}
```

---

## Authentication API (Future)

### Register

```http
POST /api/auth/register
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "name": "John Doe"
}
```

---

### Login

```http
POST /api/auth/login
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "usr_123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

## Error Responses

### Generic Error Format

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "timestamp": "2026-09-27T10:30:00Z"
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `NOT_FOUND` | 404 | Resource not found |
| `INVALID_INPUT` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `CONFLICT` | 409 | Resource already exists |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting (Future)

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1632748800
```

---

## API Examples

### Example: Complete Event Creation Flow

```javascript
// 1. Create event
POST /api/events
{
  "name": "Birthday Party",
  "date": "2026-10-15",
  "location": "Sydney",
  "guestCount": 50,
  "budget": 5000
}

// 2. Get weather for location
GET /api/weather/search?location=Sydney

// 3. Get available services
GET /api/services?category=Catering&location=Sydney

// 4. Add budget items
POST /api/events/evt_123/budget/items
{
  "category": "Catering",
  "amount": 2500
}

// 5. Get budget summary
GET /api/events/evt_123/budget
```

---

## CORS Configuration

### Development
```javascript
// localhost:3000 allowed
CORS enabled for http://localhost:5173
```

### Production
```javascript
// Production domain only
CORS restricted to https://yourdomain.com
```

---

## Webhooks (Future)

### Event Created
```json
{
  "event": "event.created",
  "data": {
    "id": "evt_123",
    "name": "Wedding",
    "date": "2026-12-01"
  },
  "timestamp": "2026-09-27T10:30:00Z"
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 500 | Server Error |

---

## Pagination

Optional pagination for list endpoints:

```http
GET /api/events?page=1&limit=10&sort=date&order=desc
```

**Response:**
```json
{
  "success": true,
  "data": [ /* array of items */ ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "pages": 3
  }
}
```

---

**Last Updated:** September 27, 2026  
**Current Status:** Frontend-only (Mock data)  
**Backend Status:** Planned for future implementation
