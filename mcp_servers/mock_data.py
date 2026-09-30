from datetime import datetime, timedelta
from typing import List, Dict, Any
import hashlib


def _seed_int(seed_str: str, lo: int, hi: int) -> int:
    """Deterministic 'random' int from a string seed — same inputs → same price."""
    h = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    return lo + (h % (hi - lo + 1))


class MockDataServer:
    """Mock MCP server for hotel, flight, and venue data.

    Prices are deterministic per (location/route, id) so repeated calls return
    the same values — avoids confusing the user with flickering numbers.
    """

    # ------------------------------------------------------------------
    # Hotels
    # ------------------------------------------------------------------

    @staticmethod
    def get_hotels(location: str, check_in: str, check_out: str) -> List[Dict[str, Any]]:
        """Return 5 mock hotels covering the full preference spectrum."""
        loc = location or "Unknown"
        s = lambda suffix, lo, hi: _seed_int(f"{loc}{suffix}", lo, hi)

        return [
            {
                "id": "h001",
                "name": f"Grand Luxury {loc}",
                "location": loc,
                "rating": 4.9,
                "stars": 5,
                "price_per_night": s("h001lux", 380, 550),
                "availability": True,
                "amenities": ["WiFi", "Infinity Pool", "Spa", "Fine Dining", "Concierge", "Gym"],
                "tier": "luxury",
                "earliest_available": check_in,
            },
            {
                "id": "h002",
                "name": f"Boutique Stay {loc}",
                "location": loc,
                "rating": 4.7,
                "stars": 4,
                "price_per_night": s("h002bou", 180, 260),
                "availability": True,
                "amenities": ["WiFi", "Rooftop Bar", "Breakfast", "Gym"],
                "tier": "premium",
                "earliest_available": check_in,
            },
            {
                "id": "h003",
                "name": f"Business Hotel {loc}",
                "location": loc,
                "rating": 4.5,
                "stars": 4,
                "price_per_night": s("h003biz", 130, 180),
                "availability": True,
                "amenities": ["WiFi", "Conference Rooms", "Business Center", "Restaurant"],
                "tier": "business",
                "earliest_available": check_in,
            },
            {
                "id": "h004",
                "name": f"Comfort Inn {loc}",
                "location": loc,
                "rating": 4.2,
                "stars": 3,
                "price_per_night": s("h004com", 85, 120),
                "availability": True,
                "amenities": ["WiFi", "Breakfast", "Parking"],
                "tier": "mid",
                "earliest_available": check_in,
            },
            {
                "id": "h005",
                "name": f"Budget Stay {loc}",
                "location": loc,
                "rating": 3.9,
                "stars": 2,
                "price_per_night": s("h005bud", 45, 80),
                "availability": True,
                "amenities": ["WiFi"],
                "tier": "budget",
                "earliest_available": check_in,
            },
        ]

    @staticmethod
    def select_hotel(
        hotels: List[Dict[str, Any]],
        preference: str = "cheapest",
    ) -> Dict[str, Any]:
        """
        Pick the best hotel according to the requested preference strategy.

        preference values:
          cheapest         — lowest price_per_night
          most_luxury      — highest stars, then highest rating
          earliest         — first available (all mock hotels available on check_in,
                             so falls back to cheapest to give a meaningful result)
        """
        available = [h for h in hotels if h.get("availability", True)]
        if not available:
            available = hotels

        if preference == "most_luxury":
            return max(available, key=lambda h: (h.get("stars", 0), h.get("rating", 0)))
        if preference == "earliest":
            # All mock hotels available same day; break tie by price ascending
            return min(available, key=lambda h: h.get("price_per_night", 9999))
        # default: cheapest
        return min(available, key=lambda h: h.get("price_per_night", 9999))

    # ------------------------------------------------------------------
    # Flights
    # ------------------------------------------------------------------

    @staticmethod
    def get_flights(departure: str, arrival: str, date: str) -> List[Dict[str, Any]]:
        """Return 5 mock flights covering the full preference spectrum."""
        dep = departure or "DEP"
        arr = arrival or "ARR"
        key = f"{dep}{arr}{date}"
        s = lambda suffix, lo, hi: _seed_int(f"{key}{suffix}", lo, hi)

        return [
            {
                "id": "f001",
                "airline": "Budget Air",
                "departure": dep,
                "arrival": arr,
                "date": date,
                "departure_time": "06:00",
                "arrival_time": f"{6 + s('f001dur', 8, 14):02d}:00",
                "price": s("f001p", 89, 180),
                "duration_minutes": s("f001dur", 480, 840),
                "stops": 2,
                "cabin_class": "economy",
                "tier": "budget",
            },
            {
                "id": "f002",
                "airline": "Value Wings",
                "departure": dep,
                "arrival": arr,
                "date": date,
                "departure_time": "07:30",
                "arrival_time": f"{7 + s('f002dur', 5, 10):02d}:30",
                "price": s("f002p", 150, 280),
                "duration_minutes": s("f002dur", 300, 600),
                "stops": 1,
                "cabin_class": "economy",
                "tier": "economy",
            },
            {
                "id": "f003",
                "airline": "Swift Connect",
                "departure": dep,
                "arrival": arr,
                "date": date,
                "departure_time": "09:00",
                "arrival_time": f"{9 + s('f003dur', 2, 6):02d}:00",
                "price": s("f003p", 280, 480),
                "duration_minutes": s("f003dur", 120, 360),
                "stops": 0,
                "cabin_class": "economy",
                "tier": "economy_nonstop",
            },
            {
                "id": "f004",
                "airline": "Premier Airways",
                "departure": dep,
                "arrival": arr,
                "date": date,
                "departure_time": "10:00",
                "arrival_time": f"{10 + s('f004dur', 2, 5):02d}:00",
                "price": s("f004p", 580, 900),
                "duration_minutes": s("f004dur", 120, 300),
                "stops": 0,
                "cabin_class": "business",
                "tier": "business",
            },
            {
                "id": "f005",
                "airline": "Elite Skies",
                "departure": dep,
                "arrival": arr,
                "date": date,
                "departure_time": "12:00",
                "arrival_time": f"{12 + s('f005dur', 2, 4):02d}:00",
                "price": s("f005p", 1200, 2200),
                "duration_minutes": s("f005dur", 120, 240),
                "stops": 0,
                "cabin_class": "first",
                "tier": "first_class",
            },
        ]

    @staticmethod
    def select_flight(
        flights: List[Dict[str, Any]],
        preference: str = "cheapest",
        cabin_class: str = "economy",
    ) -> Dict[str, Any]:
        """
        Pick the best flight according to the requested preference strategy.

        preference values:
          cheapest         — lowest total price (any cabin)
          earliest         — earliest departure_time
          most_luxury      — first class > business > economy; then cheapest within class
          shortest         — fewest duration_minutes, then fewest stops
        """
        # Filter by cabin class unless preference overrides it
        if preference == "most_luxury":
            cabin_priority = {"first": 0, "business": 1, "economy": 2}
            return min(flights, key=lambda f: (
                cabin_priority.get(f.get("cabin_class", "economy"), 2),
                f.get("price", 9999),
            ))

        candidates = [f for f in flights if f.get("cabin_class") == cabin_class]
        if not candidates:
            candidates = flights

        if preference == "earliest":
            return min(candidates, key=lambda f: f.get("departure_time", "99:99"))
        if preference == "shortest":
            return min(candidates, key=lambda f: (
                f.get("duration_minutes", 9999),
                f.get("stops", 9),
            ))
        # default: cheapest
        return min(candidates, key=lambda f: f.get("price", 9999))

    # ------------------------------------------------------------------
    # Payment (mock)
    # ------------------------------------------------------------------

    @staticmethod
    def process_payment(
        amount: float,
        currency: str = "USD",
        booking_id: str = "",
        booking_type: str = "",
    ) -> Dict[str, Any]:
        """Simulate a payment gateway response."""
        import uuid as _uuid
        transaction_id = f"TXN-{_uuid.uuid4().hex[:10].upper()}"
        return {
            "transaction_id": transaction_id,
            "status": "success",
            "amount_charged": round(amount, 2),
            "currency": currency,
            "booking_id": booking_id,
            "booking_type": booking_type,
            "gateway": "MockPay",
            "timestamp": datetime.utcnow().isoformat(),
            "receipt_url": f"https://mockpay.example.com/receipt/{transaction_id}",
        }

    # ------------------------------------------------------------------
    # Existing methods (unchanged)
    # ------------------------------------------------------------------

    @staticmethod
    def get_venues(location: str, capacity: int) -> List[Dict[str, Any]]:
        loc = location or "Unknown"
        s = lambda suffix, lo, hi: _seed_int(f"{loc}{suffix}", lo, hi)
        return [
            {
                "id": "v001",
                "name": f"Grand Ballroom {loc}",
                "location": loc,
                "capacity": capacity,
                "price_per_hour": s("v001", 500, 1500),
                "rating": 4.7,
                "type": "indoor",
                "amenities": ["Catering", "WiFi", "Parking", "AV Equipment"],
                "available_times": ["09:00-17:00", "18:00-23:00"],
            },
            {
                "id": "v002",
                "name": f"Outdoor Park {loc}",
                "location": loc,
                "capacity": capacity,
                "price_per_hour": s("v002", 200, 600),
                "rating": 4.5,
                "type": "outdoor",
                "amenities": ["Parking", "Picnic Tables", "Weather Coverage"],
                "available_times": ["06:00-18:00"],
            },
            {
                "id": "v003",
                "name": f"Conference Center {loc}",
                "location": loc,
                "capacity": capacity,
                "price_per_hour": s("v003", 300, 800),
                "rating": 4.6,
                "type": "indoor",
                "amenities": ["Multiple Rooms", "WiFi", "Catering", "Tech Support"],
                "available_times": ["08:00-22:00"],
            },
        ]

    @staticmethod
    def get_catering_options(location: str, guest_count: int) -> List[Dict[str, Any]]:
        loc = location or "Unknown"
        s = lambda suffix, lo, hi: _seed_int(f"{loc}{suffix}", lo, hi)
        return [
            {
                "id": "c001",
                "provider": "Gourmet Catering",
                "location": loc,
                "cuisine": "International",
                "price_per_person": s("c001", 50, 150),
                "menu_options": ["Buffet", "Plated", "Family Style"],
                "rating": 4.8,
                "minimum_guests": 20,
            },
            {
                "id": "c002",
                "provider": "Local Bites",
                "location": loc,
                "cuisine": "Local",
                "price_per_person": s("c002", 25, 80),
                "menu_options": ["Buffet", "Cocktail Style"],
                "rating": 4.5,
                "minimum_guests": 10,
            },
            {
                "id": "c003",
                "provider": "Premium Dining",
                "location": loc,
                "cuisine": "Fine Dining",
                "price_per_person": s("c003", 100, 250),
                "menu_options": ["Plated", "Tasting Menu"],
                "rating": 4.9,
                "minimum_guests": 30,
            },
        ]

    @staticmethod
    def get_entertainment_options(location: str) -> List[Dict[str, Any]]:
        loc = location or "Unknown"
        s = lambda suffix, lo, hi: _seed_int(f"{loc}{suffix}", lo, hi)
        return [
            {
                "id": "e001",
                "provider": "Live Band Pro",
                "type": "Live Music",
                "location": loc,
                "price": s("e001", 1000, 3000),
                "duration_hours": 4,
                "genres": ["Jazz", "Pop", "Rock"],
                "rating": 4.7,
            },
            {
                "id": "e002",
                "provider": "DJ Masters",
                "type": "DJ Service",
                "location": loc,
                "price": s("e002", 500, 1500),
                "duration_hours": 6,
                "styles": ["Club", "Wedding", "Corporate"],
                "rating": 4.6,
            },
            {
                "id": "e003",
                "provider": "Event Magicians",
                "type": "Entertainment",
                "location": loc,
                "price": s("e003", 300, 800),
                "duration_hours": 2,
                "acts": ["Magic", "Comedy", "Mentalism"],
                "rating": 4.8,
            },
        ]

    @staticmethod
    def get_transportation_options(
        departure: str, arrival: str, date: str, passengers: int
    ) -> List[Dict[str, Any]]:
        dep = departure or "DEP"
        arr = arrival or "ARR"
        key = f"{dep}{arr}{date}"
        s = lambda suffix, lo, hi: _seed_int(f"{key}{suffix}", lo, hi)
        return [
            {
                "id": "t001",
                "provider": "City Shuttle",
                "type": "shuttle",
                "departure": dep,
                "arrival": arr,
                "date": date,
                "price_per_person": s("t001", 20, 50),
                "capacity": 15,
                "departure_times": ["08:00", "12:00", "16:00", "20:00"],
                "rating": 4.5,
            },
            {
                "id": "t002",
                "provider": "Luxury Limousine",
                "type": "limousine",
                "departure": dep,
                "arrival": arr,
                "date": date,
                "price_per_person": s("t002", 80, 150),
                "capacity": 6,
                "departure_times": ["On demand"],
                "rating": 4.8,
            },
            {
                "id": "t003",
                "provider": "Coach Tours",
                "type": "coach",
                "departure": dep,
                "arrival": arr,
                "date": date,
                "price_per_person": s("t003", 30, 60),
                "capacity": 50,
                "departure_times": ["10:00", "14:00", "18:00"],
                "rating": 4.6,
            },
        ]

    @staticmethod
    def make_reservation(
        service_type: str, service_id: str, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        import uuid as _uuid
        reservation_id = f"RES{_uuid.uuid4().hex[:5].upper()}"
        return {
            "reservation_id": reservation_id,
            "service_type": service_type,
            "service_id": service_id,
            "status": "confirmed",
            "booking_date": datetime.utcnow().isoformat(),
            "details": details,
            "confirmation_code": f"CONF{_uuid.uuid4().hex[:4].upper()}",
            "notes": "Reservation confirmed. Check your email for booking details.",
        }

    @staticmethod
    def calculate_total_cost(
        venue_cost: float,
        catering_cost: float,
        entertainment_cost: float,
        transportation_cost: float = 0,
        accommodation_cost: float = 0,
        miscellaneous_cost: float = 0,
    ) -> Dict[str, Any]:
        total = (
            venue_cost + catering_cost + entertainment_cost
            + transportation_cost + accommodation_cost + miscellaneous_cost
        )
        return {
            "breakdown": {
                "venue": venue_cost,
                "catering": catering_cost,
                "entertainment": entertainment_cost,
                "transportation": transportation_cost,
                "accommodation": accommodation_cost,
                "miscellaneous": miscellaneous_cost,
            },
            "subtotal": total,
            "tax": round(total * 0.1, 2),
            "total": round(total * 1.1, 2),
            "currency": "USD",
        }

    @staticmethod
    def validate_budget(allocated_budget: float, calculated_cost: float) -> Dict[str, Any]:
        remaining = allocated_budget - calculated_cost
        percentage_used = (calculated_cost / allocated_budget * 100) if allocated_budget else 0
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
            "warning": warning,
        }

    @staticmethod
    def search_services(service_type: str, location: str, **filters) -> List[Dict[str, Any]]:
        service_map = {
            "hotels": lambda: MockDataServer.get_hotels(
                location, filters.get("check_in", ""), filters.get("check_out", "")
            ),
            "flights": lambda: MockDataServer.get_flights(
                filters.get("departure", ""), filters.get("arrival", ""), filters.get("date", "")
            ),
            "venues": lambda: MockDataServer.get_venues(location, filters.get("capacity", 100)),
            "catering": lambda: MockDataServer.get_catering_options(location, filters.get("guest_count", 50)),
            "entertainment": lambda: MockDataServer.get_entertainment_options(location),
            "transportation": lambda: MockDataServer.get_transportation_options(
                filters.get("departure", ""), filters.get("arrival", ""),
                filters.get("date", ""), filters.get("passengers", 1),
            ),
        }
        if service_type not in service_map:
            return []
        results = service_map[service_type]()
        if "min_rating" in filters:
            results = [r for r in results if r.get("rating", 0) >= filters["min_rating"]]
        if filters.get("sort_by") == "price":
            price_key = next(
                (k for k in ["price", "price_per_night", "price_per_hour", "price_per_person"]
                 if results and k in results[0]),
                None,
            )
            if price_key:
                results.sort(key=lambda x: x.get(price_key, 0))
        return results

    @staticmethod
    def create_event_plan(
        event_type: str,
        location: str,
        date: str,
        guest_count: int,
        budget: float,
        weather_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        venue_type = "outdoor" if weather_data and weather_data.get("is_favorable") else "indoor"
        venues = MockDataServer.get_venues(location, guest_count)
        catering = MockDataServer.get_catering_options(location, guest_count)
        entertainment = MockDataServer.get_entertainment_options(location)
        suitable_venues = [v for v in venues if v["type"] == venue_type]
        selected_venue = suitable_venues[0] if suitable_venues else venues[0]
        selected_catering = catering[0] if catering else None
        selected_entertainment = entertainment[0] if entertainment else None
        venue_cost = selected_venue["price_per_hour"] * 4 if selected_venue else 0
        catering_cost = (selected_catering["price_per_person"] * guest_count) if selected_catering else 0
        entertainment_cost = selected_entertainment["price"] if selected_entertainment else 0
        cost_breakdown = MockDataServer.calculate_total_cost(
            venue_cost=venue_cost,
            catering_cost=catering_cost,
            entertainment_cost=entertainment_cost,
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
                "entertainment": selected_entertainment,
            },
            "cost_breakdown": cost_breakdown,
            "budget_validation": budget_validation,
            "plan_status": "feasible" if budget_validation["status"] == "within_budget" else "needs_adjustment",
        }

    @staticmethod
    def get_event_summary(event_plan: Dict[str, Any]) -> Dict[str, Any]:
        if not event_plan or "plan_status" not in event_plan:
            return {"error": "Invalid event plan"}
        return {
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
            "plan_feasible": event_plan.get("plan_status") == "feasible",
        }

    @staticmethod
    def generate_mock_budget(event_type: str, guest_count: int) -> Dict[str, Any]:
        base_multiplier = {
            "wedding": 150, "conference": 100, "birthday": 50,
            "corporate": 120, "outdoor": 80,
        }
        multiplier = base_multiplier.get(event_type.lower(), 100)
        total_budget = guest_count * multiplier
        return {
            "total_budget": total_budget,
            "breakdown": {
                "venue": int(total_budget * 0.25),
                "catering": int(total_budget * 0.50),
                "entertainment": int(total_budget * 0.15),
                "miscellaneous": int(total_budget * 0.10),
            },
        }
