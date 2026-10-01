"""
MCP tool definitions and dispatch for the Event Planning server.

New tools added:
  - search_location   : OSM Nominatim geocoding + suggestions
  - offer_flight      : present a flight offer pending human approval
  - offer_hotel       : present a hotel offer pending human approval
  - get_booking_status: poll approval state of a booking
"""
from __future__ import annotations

import logging
from typing import Any

from backend.booking_manager import BookingType, create_booking, get_booking
from backend.location_search import suggest_locations
from mcp_servers.mock_data import MockDataServer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool schema registry
# ---------------------------------------------------------------------------

TOOL_SCHEMAS: list[dict[str, Any]] = [
    # --- Location -----------------------------------------------------------
    {
        "name": "search_location",
        "description": (
            "Search for a location by name using OpenStreetMap. "
            "Returns up to 5 matching places. Use this to validate a user-entered "
            "location or to offer 'did you mean?' suggestions when the name looks misspelled."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Free-text location query, e.g. 'Sydney Australia'",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 5, max 10)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
    # --- Flight offer (human-in-the-loop) -----------------------------------
    {
        "name": "offer_flight",
        "description": (
            "Search for available flights and present an offer to the human. "
            "preference controls which flight is selected. "
            "If auto_approve=true the booking is confirmed immediately without human input."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "departure": {"type": "string", "description": "Departure city"},
                "arrival": {"type": "string", "description": "Arrival city"},
                "date": {"type": "string", "description": "Flight date (YYYY-MM-DD)"},
                "passengers": {"type": "integer", "default": 1},
                "cabin_class": {
                    "type": "string",
                    "enum": ["economy", "business", "first"],
                    "default": "economy",
                },
                "preference": {
                    "type": "string",
                    "enum": ["cheapest", "earliest", "most_luxury", "shortest"],
                    "default": "cheapest",
                    "description": "Selection strategy",
                },
                "auto_approve": {
                    "type": "boolean",
                    "default": False,
                    "description": "Skip human approval and confirm immediately",
                },
                "plan_id": {"type": "string"},
            },
            "required": ["departure", "arrival", "date"],
        },
    },
    # --- Hotel offer (human-in-the-loop) ------------------------------------
    {
        "name": "offer_hotel",
        "description": (
            "Search for available hotels and present an offer to the human. "
            "preference controls which hotel is selected. "
            "If auto_approve=true the booking is confirmed immediately without human input, "
            "UNLESS the hotel check-in date is before the flight arrival date — in that case "
            "auto_approve is overridden to false and the user must review and approve manually. "
            "Pass flight_booking_id or flight_arrival_date to enable the date validation check."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "check_in": {"type": "string", "description": "YYYY-MM-DD"},
                "check_out": {"type": "string", "description": "YYYY-MM-DD"},
                "guests": {"type": "integer", "default": 1},
                "preference": {
                    "type": "string",
                    "enum": ["cheapest", "earliest", "most_luxury"],
                    "default": "cheapest",
                    "description": "Selection strategy",
                },
                "auto_approve": {
                    "type": "boolean",
                    "default": False,
                    "description": "Skip human approval and confirm immediately",
                },
                "plan_id": {"type": "string"},
                "flight_booking_id": {
                    "type": "string",
                    "description": (
                        "booking_id of the associated flight booking. "
                        "Used to validate that hotel check-in is not before the flight arrival date."
                    ),
                },
                "flight_arrival_date": {
                    "type": "string",
                    "description": (
                        "Explicit flight arrival date (YYYY-MM-DD) if no flight_booking_id is available. "
                        "Used to validate hotel check-in date."
                    ),
                },
            },
            "required": ["location", "check_in", "check_out"],
        },
    },
    # --- Booking status poll ------------------------------------------------
    {
        "name": "get_booking_status",
        "description": (
            "Poll the approval status of a flight or hotel offer. "
            "Returns 'pending_approval', 'confirmed', or 'rejected'."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string", "description": "Booking ID returned by offer_flight / offer_hotel"},
            },
            "required": ["booking_id"],
        },
    },
    # --- Existing tools (unchanged) -----------------------------------------
    {
        "name": "get_hotels",
        "description": "Get available hotels in a location with check-in and check-out dates",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "check_in": {"type": "string", "description": "YYYY-MM-DD"},
                "check_out": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["location", "check_in", "check_out"],
        },
    },
    {
        "name": "get_flights",
        "description": "Get available flights between two cities",
        "inputSchema": {
            "type": "object",
            "properties": {
                "departure": {"type": "string"},
                "arrival": {"type": "string"},
                "date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["departure", "arrival", "date"],
        },
    },
    {
        "name": "get_venues",
        "description": "Get available event venues in a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "capacity": {"type": "integer"},
            },
            "required": ["location", "capacity"],
        },
    },
    {
        "name": "get_catering_options",
        "description": "Get catering service options in a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "guest_count": {"type": "integer"},
            },
            "required": ["location", "guest_count"],
        },
    },
    {
        "name": "get_entertainment_options",
        "description": "Get entertainment service options in a location",
        "inputSchema": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"],
        },
    },
    {
        "name": "get_transportation_options",
        "description": "Get transportation options between two locations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "departure": {"type": "string"},
                "arrival": {"type": "string"},
                "date": {"type": "string"},
                "passengers": {"type": "integer"},
            },
            "required": ["departure", "arrival", "date", "passengers"],
        },
    },
    {
        "name": "make_reservation",
        "description": "Make a reservation for a service (venue, catering, entertainment, transport)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_type": {"type": "string"},
                "service_id": {"type": "string"},
                "details": {"type": "object"},
            },
            "required": ["service_type", "service_id", "details"],
        },
    },
    {
        "name": "calculate_total_cost",
        "description": "Calculate total event cost with breakdown and tax",
        "inputSchema": {
            "type": "object",
            "properties": {
                "venue_cost": {"type": "number"},
                "catering_cost": {"type": "number"},
                "entertainment_cost": {"type": "number"},
                "transportation_cost": {"type": "number"},
                "accommodation_cost": {"type": "number"},
                "miscellaneous_cost": {"type": "number"},
            },
            "required": ["venue_cost", "catering_cost", "entertainment_cost"],
        },
    },
    {
        "name": "validate_budget",
        "description": "Validate if costs fit within allocated budget",
        "inputSchema": {
            "type": "object",
            "properties": {
                "allocated_budget": {"type": "number"},
                "calculated_cost": {"type": "number"},
            },
            "required": ["allocated_budget", "calculated_cost"],
        },
    },
    {
        "name": "create_event_plan",
        "description": "Create a comprehensive event plan",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_type": {"type": "string"},
                "location": {"type": "string"},
                "date": {"type": "string"},
                "guest_count": {"type": "integer"},
                "budget": {"type": "number"},
                "weather_data": {"type": "object"},
            },
            "required": ["event_type", "location", "date", "guest_count", "budget"],
        },
    },
    {
        "name": "get_event_summary",
        "description": "Generate a summary of the event plan",
        "inputSchema": {
            "type": "object",
            "properties": {"event_plan": {"type": "object"}},
            "required": ["event_plan"],
        },
    },
    {
        "name": "search_services",
        "description": "Search and filter services by type and location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_type": {
                    "type": "string",
                    "enum": ["hotels", "flights", "venues", "catering", "entertainment", "transportation"],
                },
                "location": {"type": "string"},
                "min_rating": {"type": "number"},
                "sort_by": {"type": "string", "enum": ["price", "rating"]},
            },
            "required": ["service_type", "location"],
        },
    },
]


# ---------------------------------------------------------------------------
# MCP server class
# ---------------------------------------------------------------------------


class MCPEventPlanningServer:
    """MCP Server for event planning operations."""

    def __init__(self) -> None:
        self.tools = TOOL_SCHEMAS

    def list_tools(self) -> list[dict[str, Any]]:
        return self.tools

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Dispatch a tool call. Async to support the location search HTTP call."""
        logger.info("mcp_tool_call", extra={"tool": name})

        # ---- Location search ------------------------------------------------
        if name == "search_location":
            query = arguments["query"]
            limit = min(int(arguments.get("limit", 5)), 10)
            suggestions = await suggest_locations(query, limit=limit)
            return {
                "query": query,
                "results": suggestions,
                "count": len(suggestions),
            }

        # ---- Flight offer (human-in-the-loop) ------------------------------
        if name == "offer_flight":
            flights = MockDataServer.get_flights(
                arguments["departure"],
                arguments["arrival"],
                arguments["date"],
            )
            preference = arguments.get("preference", "cheapest")
            cabin = arguments.get("cabin_class", "economy")
            passengers = int(arguments.get("passengers", 1))
            auto_approve = bool(arguments.get("auto_approve", False))

            best = MockDataServer.select_flight(flights, preference=preference, cabin_class=cabin)
            offer = {
                **best,
                "passengers": passengers,
                "total_price": best["price"] * passengers,
            }
            booking = create_booking(
                BookingType.FLIGHT,
                offer=offer,
                plan_id=arguments.get("plan_id"),
                preference=preference,
                auto_approve=auto_approve,
            )
            actual_auto_approved = booking.get("status") == "confirmed" or booking.get("auto_approved", False)
            status_msg = (
                "Flight booked and payment processed automatically."
                if actual_auto_approved
                else "Flight offer is awaiting human approval."
            )
            return {
                "booking_id": booking["booking_id"],
                "status": booking["status"],
                "auto_approved": actual_auto_approved,
                "message": status_msg,
                "preference_used": preference,
                "payment": booking.get("payment"),
                "offer_summary": {
                    "airline": offer.get("airline"),
                    "route": f"{offer.get('departure')} → {offer.get('arrival')}",
                    "date": offer.get("date"),
                    "departure_time": offer.get("departure_time"),
                    "arrival_time": offer.get("arrival_time"),
                    "cabin_class": offer.get("cabin_class"),
                    "passengers": offer.get("passengers"),
                    "duration_minutes": offer.get("duration_minutes"),
                    "stops": offer.get("stops"),
                    "price_per_person": offer.get("price"),
                    "total_price": offer.get("total_price"),
                },
            }

        # ---- Hotel offer (human-in-the-loop) --------------------------------
        if name == "offer_hotel":
            hotels = MockDataServer.get_hotels(
                arguments["location"],
                arguments["check_in"],
                arguments["check_out"],
            )
            preference = arguments.get("preference", "cheapest")
            guests = int(arguments.get("guests", 1))
            auto_approve = bool(arguments.get("auto_approve", False))

            best = MockDataServer.select_hotel(hotels, preference=preference)

            from datetime import date as _date
            try:
                check_in_date = _date.fromisoformat(arguments["check_in"])
                check_out_date = _date.fromisoformat(arguments["check_out"])
                nights = (check_out_date - check_in_date).days
            except ValueError:
                check_in_date = None
                nights = 1

            # ------------------------------------------------------------------
            # Flight arrival date validation
            # ------------------------------------------------------------------
            date_warning: str | None = None
            flight_arrival_date: _date | None = None

            # Resolve flight arrival date from booking_id or explicit param
            flight_booking_id = arguments.get("flight_booking_id")
            flight_arrival_date_str = arguments.get("flight_arrival_date")

            if flight_booking_id:
                flight_booking = get_booking(flight_booking_id)
                if flight_booking:
                    flight_offer = flight_booking.get("offer", {})
                    # The flight offer stores its date in "date" (YYYY-MM-DD).
                    # The actual arrival could span to the next day but we use
                    # the flight date as the earliest possible arrival day.
                    raw = flight_offer.get("date") or flight_offer.get("arrival_date")
                    if raw:
                        try:
                            flight_arrival_date = _date.fromisoformat(raw)
                        except ValueError:
                            pass

            if flight_arrival_date is None and flight_arrival_date_str:
                try:
                    flight_arrival_date = _date.fromisoformat(flight_arrival_date_str)
                except ValueError:
                    pass

            if flight_arrival_date and check_in_date:
                if check_in_date < flight_arrival_date:
                    date_warning = (
                        f"⚠️  Hotel check-in ({arguments['check_in']}) is before the flight arrival date "
                        f"({flight_arrival_date.isoformat()}). "
                        f"Please review this booking — the hotel room may not be needed until the flight lands. "
                        f"Auto-approval has been disabled. Please approve or reject this booking manually."
                    )
                    auto_approve = False  # Override: force human review
                    logger.warning(
                        "hotel_checkin_before_flight_arrival",
                        extra={
                            "check_in": arguments["check_in"],
                            "flight_arrival_date": flight_arrival_date.isoformat(),
                            "flight_booking_id": flight_booking_id,
                        },
                    )

            # resolve flight destination (if flight_booking provided)
            flight_destination = (
                flight_offer.get("arrival")
                or flight_offer.get("arrival_city")
                or flight_offer.get("destination")
            )

            # validate hotel location matches flight destination
            requested_location = (arguments.get("location") or "").strip()
            if flight_destination and requested_location:
                if requested_location.lower() != str(flight_destination).strip().lower():
                    location_warning = (
                        f"⚠️  Hotel location ({requested_location}) does not match the flight destination "
                        f"({flight_destination}). Auto-approval has been disabled. Please review this booking manually."
                    )
                    auto_approve = False
                    logger.warning("hotel_location_mismatch", extra={
                        "requested_location": requested_location,
                        "flight_destination": flight_destination,
                        "flight_booking_id": flight_booking_id,
                    })

            offer = {
                **best,
                "check_in": arguments["check_in"],
                "check_out": arguments["check_out"],
                "nights": nights,
                "guests": guests,
                "total_price": best["price_per_night"] * max(nights, 1),
            }
            # combine date/location warnings into one field stored on booking
            warnings = [w for w in (date_warning, location_warning) if w]
            combined_warning = "\n".join(warnings) if warnings else None

            booking = create_booking(
                BookingType.HOTEL,
                offer=offer,
                plan_id=arguments.get("plan_id"),
                preference=preference,
                auto_approve=auto_approve,
                date_warning=combined_warning,  # preserves existing create_booking API
            )
            actual_auto_approved = booking.get("status") == "confirmed" or booking.get("auto_approved", False)
            if actual_auto_approved:
                status_msg = "Hotel booked and payment processed automatically."
            elif location_warning:
                status_msg = location_warning
            elif date_warning:
                status_msg = date_warning
            else:
                status_msg = "Hotel offer is awaiting human approval."

            return {
                "booking_id": booking["booking_id"],
                "status": booking["status"],
                "auto_approved": actual_auto_approved,
                "date_warning": date_warning,
                "location_warning": location_warning,
                "message": status_msg,
                "preference_used": preference,
                "payment": booking.get("payment"),
                "requires_manual_review": date_warning is not None,
                "offer_summary": {
                    "hotel": offer.get("name"),
                    "tier": offer.get("tier"),
                    "stars": offer.get("stars"),
                    "location": offer.get("location"),
                    "rating": offer.get("rating"),
                    "check_in": offer.get("check_in"),
                    "check_out": offer.get("check_out"),
                    "nights": offer.get("nights"),
                    "guests": offer.get("guests"),
                    "price_per_night": offer.get("price_per_night"),
                    "total_price": offer.get("total_price"),
                    "amenities": offer.get("amenities"),
                },
            }

        # ---- Booking status poll -------------------------------------------
        if name == "get_booking_status":
            booking_id = arguments["booking_id"]
            booking = get_booking(booking_id)
            if booking is None:
                return {"error": f"Booking {booking_id!r} not found"}
            return {
                "booking_id": booking_id,
                "status": booking["status"],
                "booking_type": booking["booking_type"],
                "decided_at": booking.get("decided_at"),
                "confirmation_code": booking.get("confirmation_code"),
                "decision_note": booking.get("decision_note"),
                "date_warning": booking.get("date_warning"),
                "requires_manual_review": booking.get("date_warning") is not None,
            }

        # ---- Existing MockData tools ----------------------------------------
        if name == "get_hotels":
            return MockDataServer.get_hotels(
                arguments["location"],
                arguments["check_in"],
                arguments["check_out"],
            )

        if name == "get_flights":
            return MockDataServer.get_flights(
                arguments["departure"],
                arguments["arrival"],
                arguments["date"],
            )

        if name == "get_venues":
            return MockDataServer.get_venues(
                arguments["location"],
                arguments["capacity"],
            )

        if name == "get_catering_options":
            return MockDataServer.get_catering_options(
                arguments["location"],
                arguments["guest_count"],
            )

        if name == "get_entertainment_options":
            return MockDataServer.get_entertainment_options(arguments["location"])

        if name == "get_transportation_options":
            return MockDataServer.get_transportation_options(
                arguments["departure"],
                arguments["arrival"],
                arguments["date"],
                arguments["passengers"],
            )

        if name == "search_services":
            return MockDataServer.search_services(
                arguments["service_type"],
                arguments["location"],
                **{k: v for k, v in arguments.items() if k not in ("service_type", "location")},
            )

        if name == "make_reservation":
            return MockDataServer.make_reservation(
                arguments["service_type"],
                arguments["service_id"],
                arguments["details"],
            )

        if name == "calculate_total_cost":
            return MockDataServer.calculate_total_cost(
                arguments.get("venue_cost", 0),
                arguments.get("catering_cost", 0),
                arguments.get("entertainment_cost", 0),
                arguments.get("transportation_cost", 0),
                arguments.get("accommodation_cost", 0),
                arguments.get("miscellaneous_cost", 0),
            )

        if name == "validate_budget":
            return MockDataServer.validate_budget(
                arguments["allocated_budget"],
                arguments["calculated_cost"],
            )

        if name == "create_event_plan":
            return MockDataServer.create_event_plan(
                arguments["event_type"],
                arguments["location"],
                arguments["date"],
                arguments["guest_count"],
                arguments["budget"],
                arguments.get("weather_data"),
            )

        if name == "get_event_summary":
            return MockDataServer.get_event_summary(arguments["event_plan"])

        return {"error": f"Unknown tool: {name}"}

    async def run(self) -> None:
        logger.info("MCP Server initialized with %d tools", len(self.tools))


# Singleton instance used by main.py
mcp_server = MCPEventPlanningServer()
