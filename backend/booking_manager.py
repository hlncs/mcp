"""
Human-in-the-loop booking manager.

Flow (manual approval):
  1. Agent calls `offer_flight` / `offer_hotel` → stored as "pending_approval".
  2. Frontend shows Approve / Reject buttons.
  3. User clicks → PUT /bookings/{id}/decision → transitions to confirmed/rejected.
  4. Confirmed bookings trigger mock payment automatically.

Flow (auto-approve):
  1. Agent calls `offer_flight` / `offer_hotel` with auto_approve=True.
  2. Record is created and immediately auto-confirmed + payment processed.
  3. Frontend shows confirmed state with payment receipt.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class BookingStatus(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class BookingType(str, Enum):
    FLIGHT = "flight"
    HOTEL = "hotel"


# Preference strategies surfaced to the UI and agent
FLIGHT_PREFERENCES = ["cheapest", "earliest", "most_luxury", "shortest"]
HOTEL_PREFERENCES  = ["cheapest", "earliest", "most_luxury"]

# In-memory store  {booking_id: dict}
_bookings: dict[str, dict[str, Any]] = {}


def _run_payment(booking_id: str, booking_type: str, amount: float) -> dict[str, Any]:
    """Execute mock payment and return receipt."""
    from mcp_servers.mock_data import MockDataServer
    return MockDataServer.process_payment(
        amount=amount,
        currency="USD",
        booking_id=booking_id,
        booking_type=booking_type,
    )


def create_booking(
    booking_type: BookingType,
    offer: dict[str, Any],
    plan_id: str | None = None,
    preference: str = "cheapest",
    auto_approve: bool = False,
) -> dict[str, Any]:
    """
    Persist an offer. If auto_approve=True the booking is immediately
    confirmed and payment is processed — no human decision needed.
    """
    booking_id = str(uuid.uuid4())
    record: dict[str, Any] = {
        "booking_id": booking_id,
        "booking_type": booking_type.value,
        "status": BookingStatus.PENDING_APPROVAL.value,
        "offer": offer,
        "plan_id": plan_id,
        "preference": preference,
        "auto_approve": auto_approve,
        "created_at": datetime.utcnow().isoformat(),
        "decided_at": None,
        "decision_note": None,
        "confirmation_code": None,
        "payment": None,
    }
    _bookings[booking_id] = record

    if auto_approve:
        _confirm(record)
        record["decision_note"] = "Auto-approved by user preference"
        logger.info("booking_auto_approved", extra={"booking_id": booking_id})
    else:
        logger.info("booking_created_pending", extra={"booking_id": booking_id})

    return record


def _confirm(record: dict[str, Any]) -> None:
    """Transition record to confirmed + process mock payment (in-place)."""
    booking_id = record["booking_id"]
    record["status"] = BookingStatus.CONFIRMED.value
    record["decided_at"] = datetime.utcnow().isoformat()
    record["confirmation_code"] = f"CONF-{booking_id[:8].upper()}"

    # Determine amount from offer
    offer = record.get("offer", {})
    amount = float(offer.get("total_price") or offer.get("price_per_night") or 0)
    record["payment"] = _run_payment(booking_id, record["booking_type"], amount)


def get_booking(booking_id: str) -> dict[str, Any] | None:
    return _bookings.get(booking_id)


def list_bookings(plan_id: str | None = None) -> list[dict[str, Any]]:
    bookings = list(_bookings.values())
    if plan_id:
        bookings = [b for b in bookings if b.get("plan_id") == plan_id]
    return sorted(bookings, key=lambda b: b["created_at"], reverse=True)


def record_decision(
    booking_id: str,
    approved: bool,
    note: str | None = None,
) -> dict[str, Any]:
    """
    Record the human's approve/reject decision.
    Raises KeyError  — booking not found.
    Raises ValueError — booking not in pending_approval state.
    """
    record = _bookings.get(booking_id)
    if record is None:
        raise KeyError(f"Booking {booking_id!r} not found")
    if record["status"] != BookingStatus.PENDING_APPROVAL.value:
        raise ValueError(
            f"Booking {booking_id!r} is already '{record['status']}'; "
            "only pending_approval bookings can be decided."
        )

    record["decision_note"] = note

    if approved:
        _confirm(record)
    else:
        record["status"] = BookingStatus.REJECTED.value
        record["decided_at"] = datetime.utcnow().isoformat()

    logger.info(
        "booking_decision",
        extra={"booking_id": booking_id, "approved": approved, "status": record["status"]},
    )
    return record
