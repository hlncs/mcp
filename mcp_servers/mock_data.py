from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

class MockDataServer:
    """Mock MCP server for hotel, flight, and venue data"""
    
    @staticmethod
    def get_hotels(location: str, check_in: str, check_out: str) -> List[Dict[str, Any]]:
        """Mock hotel data with realistic pricing"""
        return [
            {
                "id": "h001",
                "name": f"Luxury Hotel {location}",
                "location": location,
                "rating": 4.8,
                "price_per_night": random.randint(150, 300),
                "availability": random.choice([True, False]),
                "amenities": ["WiFi", "Pool", "Gym", "Restaurant"]
            },
            {
                "id": "h002",
                "name": f"Budget Stay {location}",
                "location": location,
                "rating": 4.2,
                "price_per_night": random.randint(80, 120),
                "availability": True,
                "amenities": ["WiFi", "Breakfast"]
            },
            {
                "id": "h003",
                "name": f"Business Hotel {location}",
                "location": location,
                "rating": 4.5,
                "price_per_night": random.randint(120, 200),
                "availability": True,
                "amenities": ["WiFi", "Conference Rooms", "Business Center"]
            }
        ]
    
    @staticmethod
    def get_flights(departure: str, arrival: str, date: str) -> List[Dict[str, Any]]:
        """Mock flight data with realistic details"""
        return [
            {
                "id": "f001",
                "airline": "Air Express",
                "departure": departure,
                "arrival": arrival,
                "date": date,
                "departure_time": "08:00",
                "arrival_time": "12:00",
                "price": random.randint(200, 600),
                "duration_hours": random.randint(2, 8),
                "stops": random.choice([0, 1]),
                "cabin_class": "economy"
            },
            {
                "id": "f002",
                "airline": "Budget Airlines",
                "departure": departure,
                "arrival": arrival,
                "date": date,
                "departure_time": "14:00",
                "arrival_time": "20:00",
                "price": random.randint(100, 300),
                "duration_hours": random.randint(3, 10),
                "stops": random.choice([1, 2]),
                "cabin_class": "economy"
            },
            {
                "id": "f003",
                "airline": "Premium Airways",
                "departure": departure,
                "arrival": arrival,
                "date": date,
                "departure_time": "10:00",
                "arrival_time": "14:00",
                "price": random.randint(600, 1200),
                "duration_hours": random.randint(2, 4),
                "stops": 0,
                "cabin_class": "business"
            }
        ]
    
    @staticmethod
    def get_venues(location: str, capacity: int) -> List[Dict[str, Any]]:
        """Mock venue data"""
        return [
            {
                "id": "v001",
                "name": f"Grand Ballroom {location}",
                "location": location,
                "capacity": capacity,
                "price_per_hour": random.randint(500, 1500),
                "rating": 4.7,
                "type": "indoor",
                "amenities": ["Catering", "WiFi", "Parking", "AV Equipment"],
                "available_times": ["09:00-17:00", "18:00-23:00"]
            },
            {
                "id": "v002",
                "name": f"Outdoor Park {location}",
                "location": location,
                "capacity": capacity,
                "price_per_hour": random.randint(200, 600),
                "rating": 4.5,
                "type": "outdoor",
                "amenities": ["Parking", "Picnic Tables", "Weather Coverage"],
                "available_times": ["06:00-18:00"]
            },
            {
                "id": "v003",
                "name": f"Conference Center {location}",
                "location": location,
                "capacity": capacity,
                "price_per_hour": random.randint(300, 800),
                "rating": 4.6,
                "type": "indoor",
                "amenities": ["Multiple Rooms", "WiFi", "Catering", "Tech Support"],
                "available_times": ["08:00-22:00"]
            }
        ]
    
    @staticmethod
    def get_catering_options(location: str, guest_count: int) -> List[Dict[str, Any]]:
        """Mock catering service data"""
        return [
            {
                "id": "c001",
                "provider": "Gourmet Catering",
                "location": location,
                "cuisine": "International",
                "price_per_person": random.randint(50, 150),
                "menu_options": ["Buffet", "Plated", "Family Style"],
                "rating": 4.8,
                "minimum_guests": 20
            },
            {
                "id": "c002",
                "provider": "Local Bites",
                "location": location,
                "cuisine": "Local",
                "price_per_person": random.randint(25, 80),
                "menu_options": ["Buffet", "Cocktail Style"],
                "rating": 4.5,
                "minimum_guests": 10
            },
            {
                "id": "c003",
                "provider": "Premium Dining",
                "location": location,
                "cuisine": "Fine Dining",
                "price_per_person": random.randint(100, 250),
                "menu_options": ["Plated", "Tasting Menu"],
                "rating": 4.9,
                "minimum_guests": 30
            }
        ]
    
    @staticmethod
    def get_entertainment_options(location: str) -> List[Dict[str, Any]]:
        """Mock entertainment service data"""
        return [
            {
                "id": "e001",
                "provider": "Live Band Pro",
                "type": "Live Music",
                "location": location,
                "price": random.randint(1000, 3000),
                "duration_hours": 4,
                "genres": ["Jazz", "Pop", "Rock"],
                "rating": 4.7
            },
            {
                "id": "e002",
                "provider": "DJ Masters",
                "type": "DJ Service",
                "location": location,
                "price": random.randint(500, 1500),
                "duration_hours": 6,
                "styles": ["Club", "Wedding", "Corporate"],
                "rating": 4.6
            },
            {
                "id": "e003",
                "provider": "Event Magicians",
                "type": "Entertainment",
                "location": location,
                "price": random.randint(300, 800),
                "duration_hours": 2,
                "acts": ["Magic", "Comedy", "Mentalism"],
                "rating": 4.8
            }
        ]
    
    @staticmethod
    def get_transportation_options(departure: str, arrival: str, date: str, passengers: int) -> List[Dict[str, Any]]:
        """Mock transportation service data"""
        return [
            {
                "id": "t001",
                "provider": "City Shuttle",
                "type": "shuttle",
                "departure": departure,
                "arrival": arrival,
                "date": date,
                "price_per_person": random.randint(20, 50),
                "capacity": 15,
                "departure_times": ["08:00", "12:00", "16:00", "20:00"],
                "rating": 4.5
            },
            {
                "id": "t002",
                "provider": "Luxury Limousine",
                "type": "limousine",
                "departure": departure,
                "arrival": arrival,
                "date": date,
                "price_per_person": random.randint(80, 150),
                "capacity": 6,
                "departure_times": ["On demand"],
                "rating": 4.8
            },
            {
                "id": "t003",
                "provider": "Coach Tours",
                "type": "coach",
                "departure": departure,
                "arrival": arrival,
                "date": date,
                "price_per_person": random.randint(30, 60),
                "capacity": 50,
                "departure_times": ["10:00", "14:00", "18:00"],
                "rating": 4.6
            }
        ]
    
    @staticmethod
    def make_reservation(service_type: str, service_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Mock reservation confirmation"""
        reservation_id = f"RES{random.randint(10000, 99999)}"
        
        return {
            "reservation_id": reservation_id,
            "service_type": service_type,
            "service_id": service_id,
            "status": "confirmed",
            "booking_date": datetime.now().isoformat(),
            "details": details,
            "confirmation_code": f"CONF{random.randint(1000, 9999)}",
            "notes": "Reservation confirmed. Check your email for booking details."
        }
    
    @staticmethod
    def calculate_total_cost(
        venue_cost: float,
        catering_cost: float,
        entertainment_cost: float,
        transportation_cost: float = 0,
        accommodation_cost: float = 0,
        miscellaneous_cost: float = 0
    ) -> Dict[str, Any]:
        """Calculate total event cost with breakdown"""
        total = (
            venue_cost + catering_cost + entertainment_cost +
            transportation_cost + accommodation_cost + miscellaneous_cost
        )
        
        return {
            "breakdown": {
                "venue": venue_cost,
                "catering": catering_cost,
                "entertainment": entertainment_cost,
                "transportation": transportation_cost,
                "accommodation": accommodation_cost,
                "miscellaneous": miscellaneous_cost
            },
            "subtotal": total,
            "tax": round(total * 0.1, 2),
            "total": round(total * 1.1, 2),
            "currency": "USD"
        }
    
    @staticmethod
    def validate_budget(allocated_budget: float, calculated_cost: float) -> Dict[str, Any]:
        """Validate if costs fit within allocated budget"""
        remaining = allocated_budget - calculated_cost
        percentage_used = (calculated_cost / allocated_budget) * 100
        
        status = "within_budget" if remaining >= 0 else "over_budget"
        warning = None
        
        if percentage_used > 90:
            warning = "⚠️ Budget usage above 90%"
        elif remaining < 0:
            warning = f"❌ Budget exceeded by ${abs(remaining):.2f}"
        
        return {
            "allocated_budget": allocated_budget,
            "calculated_cost": calculated_cost,
            "remaining": max(remaining, 0),
            "percentage_used": round(percentage_used, 1),
            "status": status,
            "warning": warning
        }
    
    @staticmethod
    def generate_mock_budget(event_type: str, guest_count: int) -> Dict[str, Any]:
        """Generate a realistic mock budget based on event type"""
        base_multiplier = {
            "wedding": 150,
            "conference": 100,
            "birthday": 50,
            "corporate": 120,
            "outdoor": 80
        }
        
        multiplier = base_multiplier.get(event_type.lower(), 100)
        total_budget = guest_count * multiplier
        
        return {
            "total_budget": total_budget,
            "breakdown": {
                "venue": int(total_budget * 0.25),
                "catering": int(total_budget * 0.5),
                "entertainment": int(total_budget * 0.15),
                "miscellaneous": int(total_budget * 0.1)
            }
        }
    
    @staticmethod
    def search_services(service_type: str, location: str, **filters) -> List[Dict[str, Any]]:
        """Search and filter services by type and location"""
        service_map = {
            "hotels": MockDataServer.get_hotels,
            "flights": MockDataServer.get_flights,
            "venues": MockDataServer.get_venues,
            "catering": MockDataServer.get_catering_options,
            "entertainment": MockDataServer.get_entertainment_options,
            "transportation": MockDataServer.get_transportation_options
        }
        
        if service_type not in service_map:
            return []
        
        # Get base results
        if service_type == "hotels":
            results = service_map[service_type](location, filters.get("check_in", ""), filters.get("check_out", ""))
        elif service_type == "flights":
            results = service_map[service_type](filters.get("departure", ""), filters.get("arrival", ""), filters.get("date", ""))
        elif service_type == "venues":
            results = service_map[service_type](location, filters.get("capacity", 100))
        elif service_type == "catering":
            results = service_map[service_type](location, filters.get("guest_count", 50))
        elif service_type == "transportation":
            results = service_map[service_type](filters.get("departure", ""), filters.get("arrival", ""), filters.get("date", ""), filters.get("passengers", 1))
        else:
            results = service_map[service_type](location)
        
        # Apply rating filter if provided
        if "min_rating" in filters:
            results = [r for r in results if r.get("rating", 0) >= filters["min_rating"]]
        
        # Sort by price if requested
        if filters.get("sort_by") == "price":
            price_key = next((k for k in ["price", "price_per_night", "price_per_hour", "price_per_person"] if k in results[0]), None)
            if price_key:
                results.sort(key=lambda x: x.get(price_key, 0))
        
        return results
    
    @staticmethod
    def get_service_by_id(service_type: str, service_id: str, location: str = "", **params) -> Dict[str, Any]:
        """Retrieve a specific service by ID"""
        services = MockDataServer.search_services(service_type, location, **params)
        
        for service in services:
            if service.get("id") == service_id:
                return service
        
        return {"error": f"Service {service_id} not found"}
    
    @staticmethod
    def create_event_plan(
        event_type: str,
        location: str,
        date: str,
        guest_count: int,
        budget: float,
        weather_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a comprehensive event plan"""
        
        # Check if outdoor venue is suitable based on weather
        venue_type = "outdoor" if weather_data and weather_data.get("is_favorable") else "indoor"
        
        venues = MockDataServer.get_venues(location, guest_count)
        catering = MockDataServer.get_catering_options(location, guest_count)
        entertainment = MockDataServer.get_entertainment_options(location)
        
        # Filter venues by type
        suitable_venues = [v for v in venues if v["type"] == venue_type]
        
        selected_venue = suitable_venues[0] if suitable_venues else venues[0]
        selected_catering = catering[0] if catering else None
        selected_entertainment = entertainment[0] if entertainment else None
        
        # Calculate estimated costs
        venue_hours = 4
        venue_cost = selected_venue["price_per_hour"] * venue_hours if selected_venue else 0
        catering_cost = (selected_catering["price_per_person"] * guest_count) if selected_catering else 0
        entertainment_cost = selected_entertainment["price"] if selected_entertainment else 0
        
        cost_breakdown = MockDataServer.calculate_total_cost(
            venue_cost=venue_cost,
            catering_cost=catering_cost,
            entertainment_cost=entertainment_cost
        )
        
        budget_validation = MockDataServer.validate_budget(budget, cost_breakdown["total"])
        
        return {
            "event_type": event_type,
            "location": location,
            "date": date,
            "guest_count": guest_count,
            "venue_type": venue_type,
            "weather_favorable": weather_data.get("is_favorable", True) if weather_data else True,
            "selected_services": {
                "venue": selected_venue,
                "catering": selected_catering,
                "entertainment": selected_entertainment
            },
            "cost_breakdown": cost_breakdown,
            "budget_validation": budget_validation,
            "plan_status": "feasible" if budget_validation["status"] == "within_budget" else "needs_adjustment"
        }
    
    @staticmethod
    def get_event_summary(event_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the event plan"""
        if not event_plan or "plan_status" not in event_plan:
            return {"error": "Invalid event plan"}
        
        summary = {
            "event_type": event_plan.get("event_type"),
            "date": event_plan.get("date"),
            "location": event_plan.get("location"),
            "guest_count": event_plan.get("guest_count"),
            "venue": event_plan.get("selected_services", {}).get("venue", {}).get("name"),
            "catering": event_plan.get("selected_services", {}).get("catering", {}).get("provider"),
            "entertainment": event_plan.get("selected_services", {}).get("entertainment", {}).get("provider"),
            "total_cost": event_plan.get("cost_breakdown", {}).get("total"),
            "budget_status": event_plan.get("budget_validation", {}).get("status"),
            "weather_suitable": event_plan.get("weather_favorable"),
            "plan_feasible": event_plan.get("plan_status") == "feasible"
        }
        
        return summary
    
    @staticmethod
    def list_all_services(location: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all available services in a location"""
        return {
            "hotels": MockDataServer.get_hotels(location, "", ""),
            "flights": MockDataServer.get_flights("", "", ""),
            "venues": MockDataServer.get_venues(location, 100),
            "catering": MockDataServer.get_catering_options(location, 50),
            "entertainment": MockDataServer.get_entertainment_options(location),
            "transportation": MockDataServer.get_transportation_options("", "", "", 1)
        }