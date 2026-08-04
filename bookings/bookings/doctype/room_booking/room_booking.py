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
    time_str = str(value).split(" ")[-1].strip()
    parts = time_str.split(":")
    return f"{int(parts[0]):02d}:{parts[1]}"


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
                "from_time", "notes", "available_slot", "recurring_group_id"],
    )
    return [r for r in rows if _time_of(r.get("from_time")) == start_hm]


def _available_slot_name(room, date, start_hm):
    return frappe.db.get_value(
        "Available Slot",
        {"reservation_item": room, "slot_date": date, "start_time": _combine_datetime(date, start_hm)},
        "name",
    )


def _available_slot_doc(room, date_str, start_hm, end_hm=None):
    """Return the persisted Available Slot for a room/date/start, or None."""
    name = _available_slot_name(room, date_str, start_hm)
    if name:
        return frappe.get_doc("Available Slot", name)
    return None


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


def _insert_room_booking(room, date, start_hm, end_hm, notes, customer_name, customer_email,
                         recurring_group_id=None, recurring_frequency=None,
                         recurring_interval=None, recurring_until_date=None):
    """Create a Confirmed Room Booking, reconciling Available Slot counts.

    Mirrors the create path used by book_room_slot so recurring regeneration
    and ad-hoc bookings behave identically.
    """
    slot_doc = _available_slot_doc(room, date, start_hm, end_hm)
    if slot_doc:
        _increment_available_slot(
            slot_doc.name,
            f"This room is fully booked at {start_hm} on {date}",
        )
    else:
        booked = len(_slot_booked_rooms(room, date, start_hm))
        capacity = _room_capacity(room)
        if booked >= capacity:
            frappe.throw(f"This room is fully booked at {start_hm} on {date}")

    booking = frappe.get_doc({
        "doctype": "Room Booking",
        "available_slot": slot_doc.name if slot_doc else "",
        "reservation_item": room,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "booking_date": date,
        "from_time": _combine_datetime(date, start_hm),
        "to_time": _combine_datetime(date, end_hm),
        "notes": notes,
        "status": "Confirmed",
        "booking_ref": generate_booking_ref(),
        "recurring_group_id": recurring_group_id or "",
        "recurring_frequency": recurring_frequency or "",
        "recurring_interval": recurring_interval,
        "recurring_until_date": recurring_until_date or "",
    })
    booking.insert(ignore_permissions=True)
    return booking


def _scope_targets(booking, scope):
    """Resolve the Room Bookings affected by an edit, based on scope.

    scope 'this' -> only the booking itself.
    scope 'future' -> the booking and later members of its recurring group.
    scope 'all' -> every active member of its recurring group.
    """
    group = (booking.get("recurring_group_id") or "").strip()
    if scope == "this" or not group:
        return [booking.name]
    filters = {"recurring_group_id": group, "status": "Confirmed"}
    if scope == "future":
        filters["booking_date"] = [">=", str(booking.booking_date)]
    return frappe.get_all("Room Booking", filters=filters, pluck="name")


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
def cancel_room_booking(booking_ref, scope="this"):
    """Cancel a room booking (optionally its whole recurring series)."""
    booking = frappe.get_doc("Room Booking", {"booking_ref": booking_ref})
    targets = _scope_targets(booking, scope)

    cancelled = 0
    for name in targets:
        doc = booking if name == booking.name else frappe.get_doc("Room Booking", name)

        if doc.status == "Cancelled":
            continue

        if doc.schedule_slot:
            try:
                slot_doc = frappe.get_doc("Schedule Slot", doc.schedule_slot)
                slot_doc.status = "Free"
                slot_doc.booking_ref = None
                slot_doc.save(ignore_permissions=True)
            except Exception:
                pass

        _release_available_slot(doc.available_slot)

        doc.status = "Cancelled"
        doc.save(ignore_permissions=True)
        cancelled += 1

    return {"success": True, "message": "Booking cancelled", "cancelled": cancelled}


def update_recurring_group(booking_ref, frequency, interval, until_date, scope="future"):
    """Regenerate the set of dates in a recurring group, or unlink the series.

    scope 'future' regenerates from the edited booking's date onward.
    scope 'all' regenerates the entire series.
    An empty frequency/until_date unlinks (detaches) the group members instead.
    """
    from frappe.utils import add_days, add_months, getdate

    booking = frappe.get_doc("Room Booking", {"booking_ref": booking_ref})
    group = (booking.get("recurring_group_id") or "").strip()

    if not group:
        frappe.throw("This booking is not part of a recurring series")

    members = frappe.get_all(
        "Room Booking",
        filters={"recurring_group_id": group, "status": "Confirmed"},
        fields=["name", "booking_date"],
        order_by="booking_date asc",
    )
    if not members:
        frappe.throw("No active occurrences in this recurring series")

    if not frequency or not until_date:
        for name in _scope_targets(booking, scope):
            doc = frappe.get_doc("Room Booking", name)
            doc.recurring_group_id = ""
            doc.recurring_frequency = ""
            doc.recurring_interval = None
            doc.recurring_until_date = ""
            doc.save(ignore_permissions=True)
        return {"success": True, "unlinked": True}

    anchor = getdate(members[0]["booking_date"]) if scope == "all" else getdate(booking.booking_date)
    until = getdate(until_date)
    interval = max(1, int(interval or 1))

    desired = []
    current = anchor
    count = 0
    while current <= until and count < 500:
        desired.append(current)
        if frequency == "daily":
            current = add_days(current, interval)
        elif frequency == "weekly":
            current = add_days(current, 7 * interval)
        else:
            current = add_months(current, interval)
        count += 1

    if not desired:
        frappe.throw("The recurrence end date is before the series start")

    existing = {getdate(m["booking_date"]): m["name"] for m in members}
    desired_set = set(desired)

    removed = [name for mdate, name in existing.items() if mdate >= anchor and mdate not in desired_set]
    for name in removed:
        doc = frappe.get_doc("Room Booking", name)
        _release_available_slot(doc.available_slot)
        doc.status = "Cancelled"
        doc.save(ignore_permissions=True)

    start_hm = _time_of(booking.from_time)
    end_hm = _time_of(booking.to_time)
    for mdate in desired:
        if mdate in existing:
            continue
        _insert_room_booking(
            booking.reservation_item, str(mdate), start_hm, end_hm,
            booking.notes, booking.customer_name, booking.customer_email,
            group, frequency, interval, str(until),
        )

    for name in members:
        doc = frappe.get_doc("Room Booking", name["name"])
        if doc.status == "Cancelled":
            continue
        doc.recurring_frequency = frequency
        doc.recurring_interval = interval
        doc.recurring_until_date = str(until)
        doc.save(ignore_permissions=True)

    return {"success": True, "occurrences": len(desired)}


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
                "status", "notes", "recurring_group_id", "recurring_frequency",
                "recurring_interval", "recurring_until_date"],
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
                "status", "notes", "recurring_group_id", "recurring_frequency",
                "recurring_interval", "recurring_until_date"],
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
