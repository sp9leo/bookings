# Copyright (c) 2026, osaz and contributors
# For license information, please see license.txt

import frappe
import secrets


def generate_booking_ref():
    """Generate a 6-character booking reference."""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(secrets.choice(chars) for _ in range(6))


def _combine_datetime(date_val, time_val):
    from bookings.bookings.doctype.reservation.reservation import _combine_datetime as combine
    return combine(date_val, time_val)


def _time_of(value):
    if not value:
        return ""
    return str(value).split(" ")[-1][:5]


def _add_hour(time_str):
    hour, minute = (time_str or "00:00").split(":")
    return f"{int(hour) + 1:02d}:{minute}"


def _room_capacity(room):
    """Reservation Item capacity, defaulting to 1."""
    capacity = frappe.db.get_value("Reservation Item", room, "capacity") or 0
    return int(capacity) or 1


def _slot_booked_rooms(room, date, start_hm):
    """Confirmed Room Bookings occupying a room/date/start-time slot."""
    rows = frappe.get_all(
        "Room Booking",
        filters={
            "reservation_item": room,
            "booking_date": date,
            "status": "Confirmed",
        },
        fields=["name", "booking_ref", "customer_name", "customer_email",
                "from_time", "notes", "available_slot"],
    )
    return [r for r in rows if _time_of(r.get("from_time")) == start_hm]


def _available_slot_name(room, date, start_hm):
    return frappe.db.get_value(
        "Available Slot",
        {"reservation_item": room, "slot_date": date, "start_time": _combine_datetime(date, start_hm)},
        "name",
    )


def _ensure_available_slot(room, date, start_hm, end_hm=None):
    """Get (creating if needed) the Available Slot for a room/date/start-time.

    Newly created slots reconcile their `booked` count from existing Confirmed
    Room Bookings so legacy bookings are counted and linked correctly.
    """
    name = _available_slot_name(room, date, start_hm)
    if name:
        doc = frappe.get_doc("Available Slot", name)
        capacity = _room_capacity(room)
        if int(doc.capacity or 0) != capacity:
            doc.capacity = capacity
            doc.is_full = 1 if int(doc.booked or 0) >= capacity else 0
            doc.save(ignore_permissions=True)
        return doc

    start_dt = _combine_datetime(date, start_hm)
    end_dt = _combine_datetime(date, end_hm or _add_hour(start_hm))
    existing = _slot_booked_rooms(room, date, start_hm)
    capacity = _room_capacity(room)

    doc = frappe.get_doc({
        "doctype": "Available Slot",
        "reservation_item": room,
        "slot_date": date,
        "start_time": start_dt,
        "end_time": end_dt,
        "capacity": capacity,
        "booked": len(existing),
        "is_full": 1 if len(existing) >= capacity else 0,
    })
    doc.insert(ignore_permissions=True)

    for row in existing:
        if not row.get("available_slot"):
            frappe.db.set_value("Room Booking", row["name"], "available_slot", doc.name)
    return doc


def _increment_available_slot(slot_name, message):
    """Atomically reserve one seat on an Available Slot; throws when full."""
    row = frappe.db.sql(
        "SELECT booked, capacity FROM `tabAvailable Slot` WHERE name = %s FOR UPDATE",
        slot_name, as_dict=True,
    )
    if not row:
        frappe.throw("Slot not found")
    if int(row[0]["booked"]) >= int(row[0]["capacity"]):
        frappe.throw(message)
    frappe.db.sql(
        "UPDATE `tabAvailable Slot` SET booked = booked + 1 WHERE name = %s", slot_name
    )


def _release_available_slot(slot_name):
    """Release one seat on an Available Slot and recompute is_full."""
    if not slot_name:
        return
    row = frappe.db.get_value("Available Slot", slot_name, ["booked", "capacity"], as_dict=True)
    if not row:
        return
    booked = max(0, int(row["booked"]) - 1)
    frappe.db.set_value("Available Slot", slot_name, {
        "booked": booked,
        "is_full": 1 if booked >= int(row["capacity"]) else 0,
    }, update_modified=False)


@frappe.whitelist()
def create_room_booking(schedule_slot, notes=None):
    """Create a new room booking from a schedule slot."""
    slot_doc = frappe.get_doc("Schedule Slot", schedule_slot)
    
    if slot_doc.status == "Booked":
        frappe.throw("This slot is already booked")
    
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)
    
    booking = frappe.get_doc({
        "doctype": "Room Booking",
        "schedule_slot": schedule_slot,
        "reservation_item": slot_doc.reservation_item,
        "customer_name": user_doc.full_name,
        "customer_email": user,
        "booking_date": slot_doc.slot_date,
        "from_time": slot_doc.start_time,
        "to_time": slot_doc.end_time,
        "notes": notes,
        "status": "Confirmed",
        "booking_ref": generate_booking_ref()
    })
    booking.insert(ignore_permissions=True)
    
    slot_doc.status = "Booked"
    slot_doc.booking_ref = booking.booking_ref
    slot_doc.booked_by = user_doc.full_name or user
    slot_doc.save(ignore_permissions=True)
    
    return {
        "name": booking.name,
        "booking_ref": booking.booking_ref
    }


@frappe.whitelist()
def cancel_room_booking(booking_ref):
    """Cancel a room booking."""
    booking = frappe.get_doc("Room Booking", {"booking_ref": booking_ref})
    
    if booking.status == "Cancelled":
        return {"success": False, "message": "Already cancelled"}
    
    if booking.schedule_slot:
        try:
            slot_doc = frappe.get_doc("Schedule Slot", booking.schedule_slot)
            slot_doc.status = "Free"
            slot_doc.booking_ref = None
            slot_doc.save(ignore_permissions=True)
        except Exception:
            pass
    
    _release_available_slot(booking.available_slot)
    
    booking.status = "Cancelled"
    booking.save(ignore_permissions=True)
    
    return {"success": True, "message": "Booking cancelled"}


@frappe.whitelist()
def get_my_bookings(user=None):
    """Get all bookings for the current user or specified user."""
    if not user:
        user = frappe.session.user

    user_email = frappe.db.get_value("User", user, "email") or user

    bookings = frappe.get_all(
        "Room Booking",
        filters={"customer_email": ["in", [user, user_email]]},
        fields=["name", "booking_ref", "schedule_slot", "available_slot", "reservation_item",
                "customer_name", "customer_email", "booking_date", "from_time", "to_time",
                "status", "notes"],
        order_by="booking_date desc"
    )
    return bookings


@frappe.whitelist()
def lookup_room_booking(email, booking_ref):
    """Lookup a room booking by email and booking reference."""
    return frappe.get_all(
        "Room Booking",
        filters={"customer_email": email, "booking_ref": booking_ref},
        fields=["name", "booking_ref", "schedule_slot", "available_slot", "reservation_item",
                "customer_name", "customer_email", "booking_date", "from_time", "to_time",
                "status", "notes"],
    )


@frappe.whitelist()
def get_room_schedule(item, start_date, end_date):
    """Get schedule slots for a room within a date range."""
    slots = frappe.get_all(
        "Schedule Slot",
        filters={
            "reservation_item": item,
            "slot_date": ["between", [start_date, end_date]]
        },
        fields=["name", "slot_date", "period_number", "start_time", 
                "end_time", "status", "booking_ref"],
        order_by="slot_date, start_time"
    )
    return slots


@frappe.whitelist()
def get_upcoming_bookings(user=None):
    """Get upcoming bookings for a user."""
    if not user:
        user = frappe.session.user
    
    today = frappe.utils.today()
    
    bookings = frappe.get_all(
        "Room Booking",
        filters={
            "customer_email": user,
            "booking_date": [">=", today],
            "status": "Confirmed"
        },
        fields=["name", "booking_ref", "reservation_item", "booking_date",
                "from_time", "to_time", "notes"],
        order_by="booking_date, from_time"
    )
    return bookings


import frappe
from frappe.model.document import Document


class RoomBooking(Document):
	pass
