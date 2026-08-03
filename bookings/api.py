# Bookings Module API
# Public and internal endpoints for the booking system

from datetime import datetime

import frappe


@frappe.whitelist(allow_guest=True)
def get_items(item_type=None):
    """Get all active reservation items."""
    filters = {"is_active": 1}
    if item_type:
        filters["item_type"] = item_type
    
    items = frappe.get_all(
        "Reservation Item",
        filters=filters,
        fields=["name", "item_name", "item_type", "class", "user", "is_active",
                "subtitle", "group", "capacity", "location", "features"],
        order_by="item_name"
    )
    return items


@frappe.whitelist(allow_guest=True)
def get_teachers():
    """Get all active teachers/persons."""
    return get_items("Person")


@frappe.whitelist(allow_guest=True)
def get_rooms():
    """Get all active rooms."""
    return get_items("Room")


@frappe.whitelist(allow_guest=True)
def get_slots(item, date=None):
    """Get slots for an item (including booked/full ones; clients filter by availability)."""
    filters = {
        "reservation_item": item,
    }
    
    if date:
        filters["slot_date"] = date
    
    slots = frappe.get_all(
        "Available Slot",
        filters=filters,
        fields=["name", "slot_date", "reservation_item", 
                "start_time", "end_time", "capacity", "booked"],
        order_by="slot_date, start_time"
    )
    return slots


@frappe.whitelist(allow_guest=True)
def reserve(slot, customer_name, customer_email, notes=None):
    """Create a reservation for a slot."""
    from bookings.bookings.doctype.reservation.reservation import create_reservation
    return create_reservation(slot, customer_name, customer_email, notes)


@frappe.whitelist(allow_guest=True)
def lookup_reservation(email, booking_ref):
    """Lookup a reservation by email and booking reference."""
    from bookings.bookings.doctype.reservation.reservation import get_reservation
    return get_reservation(email, booking_ref)


@frappe.whitelist(allow_guest=True)
def cancel_reservation(access_token):
    """Cancel a reservation using access token."""
    from bookings.bookings.doctype.reservation.reservation import cancel_reservation as cancel_res
    return cancel_res(access_token)


@frappe.whitelist()
def get_schedules(item_type=None):
    """Get all schedules, optionally filtered by item type."""
    from bookings.bookings.doctype.schedule.schedule import get_schedules
    return get_schedules(item_type=item_type)


@frappe.whitelist()
def get_schedule_for_room(item, start_date=None, end_date=None):
    """Get schedule slots for a room within a date range."""
    from bookings.bookings.doctype.schedule_slot.schedule_slot import get_schedule_slots
    return get_schedule_slots(item=item, start_date=start_date, end_date=end_date)


@frappe.whitelist()
def get_or_create_room_schedule(room):
    """Get the schedule for a room, creating a default one if none exists."""
    existing = frappe.db.get_value(
        "Schedule", {"reservation_item": room, "applies_to": "Room"}, "name"
    )
    if not existing:
        existing = frappe.db.get_value("Schedule", {"reservation_item": room}, "name")
    if existing:
        doc = frappe.get_doc("Schedule", existing)
        if len(doc.schedule_periods) == 0:
            for period in _global_periods():
                doc.append("schedule_periods", {**period, "doctype": "Schedule Periods"})
            doc.save(ignore_permissions=True)
        return _schedule_with_periods(doc)

    schedule = frappe.get_doc({
        "doctype": "Schedule",
        "applies_to": "Room",
        "reservation_item": room,
        "schedule_periods": [
            {"doctype": "Schedule Periods", **period}
            for period in _global_periods()
        ],
    })
    schedule.insert(ignore_permissions=True)
    return _schedule_with_periods(schedule)


_DEFAULT_GLOBAL_TIMES = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]


def _add_hour(time_str):
    hour, minute = (time_str or "00:00").split(":")
    return f"{int(hour) + 1:02d}:{minute}"


def _time_of(value):
    if not value:
        return ""
    return str(value).split(" ")[-1][:5]


def _times_to_periods(times):
    """Build Schedule Periods rows from an ordered list of 'HH:MM' start times."""
    periods = []
    for idx, start in enumerate(times):
        start = (start or "").strip()
        if not start:
            continue
        start = _time_of(start) or start
        periods.append({
            "period_number": idx,
            "start_time": f"{start}:00",
            "end_time": f"{_add_hour(start)}:00",
            "label": start,
        })
    return periods


def _default_periods():
    return _times_to_periods(_DEFAULT_GLOBAL_TIMES)


def _global_periods():
    """Return the current global time-slot periods, falling back to defaults."""
    name = frappe.db.get_value(
        "Schedule",
        {"applies_to": "Room", "reservation_item": ("is", "not set")},
        "name",
    )
    if not name:
        return _default_periods()
    doc = frappe.get_doc("Schedule", name)
    return [
        {
            "period_number": p.period_number,
            "start_time": p.start_time,
            "end_time": p.end_time,
            "label": p.label,
        }
        for p in doc.schedule_periods
    ] or _default_periods()


def _schedule_with_periods(schedule):
    if isinstance(schedule, str):
        schedule = frappe.get_doc("Schedule", schedule)
    periods = [
        {
            "period_number": p.period_number,
            "start_time": p.start_time,
            "end_time": p.end_time,
            "label": p.label,
        }
        for p in schedule.schedule_periods
    ]
    return {
        "name": schedule.name,
        "applies_to": schedule.applies_to,
        "reservation_item": schedule.reservation_item,
        "periods": periods,
    }


def _global_schedule_name():
    name = frappe.db.get_value(
        "Schedule",
        {"applies_to": "Room", "reservation_item": ("is", "not set")},
        "name",
    )
    if name:
        return name

    schedule = frappe.get_doc({
        "doctype": "Schedule",
        "applies_to": "Room",
        "reservation_item": None,
        "schedule_periods": [
            {"doctype": "Schedule Periods", **period}
            for period in _default_periods()
        ],
    })
    schedule.insert(ignore_permissions=True)
    return schedule.name


def _periods_match(existing, target):
    if len(existing) != len(target):
        return False
    for existing_period, target_period in zip(existing, target):
        if _time_of(existing_period.start_time) != _time_of(target_period["start_time"]):
            return False
    return True


def _replace_schedule_periods(doc, periods):
    """Replace a Schedule's child periods using Document rows (dicts alone break save)."""
    doc.schedule_periods = []
    for period in periods:
        doc.append("schedule_periods", {**period, "doctype": "Schedule Periods"})


def _sync_room_schedules():
    """Rewrite every room schedule's periods to match the global list."""
    global_name = _global_schedule_name()
    global_doc = frappe.get_doc("Schedule", global_name)
    periods = [
        {"doctype": "Schedule Periods", **{
            "period_number": p.period_number,
            "start_time": p.start_time,
            "end_time": p.end_time,
            "label": p.label,
        }}
        for p in global_doc.schedule_periods
    ]
    room_schedules = frappe.get_all(
        "Schedule",
        filters={"applies_to": "Room", "reservation_item": ("is", "set")},
        fields=["name"],
    )
    for row in room_schedules:
        doc = frappe.get_doc("Schedule", row.name)
        if _periods_match(doc.schedule_periods, periods):
            continue
        _replace_schedule_periods(doc, periods)
        doc.save(ignore_permissions=True)


def _cancel_bookings_for_removed_times(times):
    """Cancel active room bookings whose slot time was removed from the list."""
    if not times:
        return
    from bookings.bookings.doctype.room_booking.room_booking import cancel_room_booking

    legacy_slots = frappe.get_all(
        "Schedule Slot",
        filters={"status": "Booked"},
        fields=["name", "start_time", "booking_ref"],
    )
    for slot in legacy_slots:
        if _time_of(slot.get("start_time")) not in times:
            continue
        if not slot.get("booking_ref"):
            continue
        try:
            cancel_room_booking(slot["booking_ref"])
        except Exception:
            frappe.log_error(frappe.get_traceback(), "cancel booking for removed time slot")

    available_bookings = frappe.get_all(
        "Room Booking",
        filters={"status": "Confirmed", "from_time": ("is", "set")},
        fields=["booking_ref", "from_time"],
    )
    for booking in available_bookings:
        if _time_of(booking.get("from_time")) not in times:
            continue
        try:
            cancel_room_booking(booking["booking_ref"])
        except Exception:
            frappe.log_error(frappe.get_traceback(), "cancel available booking for removed time slot")

    empty_slots = frappe.get_all(
        "Available Slot",
        filters={"booked": 0},
        fields=["name", "start_time"],
    )
    for slot in empty_slots:
        if _time_of(slot.get("start_time")) in times:
            try:
                frappe.delete_doc("Available Slot", slot["name"], force=True, ignore_permissions=True)
            except Exception:
                frappe.log_error(frappe.get_traceback(), "clean empty available slot for removed time")


@frappe.whitelist()
def get_global_time_slots():
    """Get the global room time-slot list (single source of truth for room views)."""
    name = _global_schedule_name()
    try:
        _sync_room_schedules()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "sync room schedules from global slots")
    doc = frappe.get_doc("Schedule", name)
    return {
        "schedule": name,
        "slots": [
            {
                "period_number": p.period_number,
                "start_time": p.start_time,
                "end_time": p.end_time,
                "label": p.label,
            }
            for p in doc.schedule_periods
        ],
    }


@frappe.whitelist()
def save_global_time_slots(slots):
    """Replace the global room time-slot list and sync all room schedules."""
    _require_admin()
    periods = _times_to_periods(_coerce_list(slots))
    if not periods:
        frappe.throw("At least one time slot is required")

    name = _global_schedule_name()
    doc = frappe.get_doc("Schedule", name)
    removed_times = {
        _time_of(p.start_time)
        for p in doc.schedule_periods
    } - {p["label"] for p in periods}

    _replace_schedule_periods(doc, periods)
    doc.save(ignore_permissions=True)

    _cancel_bookings_for_removed_times(removed_times)
    _sync_room_schedules()
    frappe.db.commit()

    return {"success": True, "schedule": name, "slots": periods}


@frappe.whitelist()
def get_or_create_slot(schedule, slot_date, period_number):
    """Get or create a schedule slot on-demand."""
    from bookings.bookings.doctype.schedule_slot.schedule_slot import get_or_create_slot as get_create
    return get_create(schedule, slot_date, period_number)


@frappe.whitelist()
def book_room(schedule_slot, notes=None):
    """Book a room from a schedule slot."""
    from bookings.bookings.doctype.room_booking.room_booking import create_room_booking
    return create_room_booking(schedule_slot, notes)


@frappe.whitelist()
def cancel_room_booking(booking_ref):
    """Cancel a room booking."""
    from bookings.bookings.doctype.room_booking.room_booking import cancel_room_booking as cancel_rb
    return cancel_rb(booking_ref)


@frappe.whitelist()
def get_my_room_bookings():
    """Get current user's room bookings."""
    from bookings.bookings.doctype.room_booking.room_booking import get_my_bookings
    return get_my_bookings()


@frappe.whitelist(allow_guest=True)
def lookup_room_booking(email, booking_ref):
    """Lookup a room booking by email and reference."""
    from bookings.bookings.doctype.room_booking.room_booking import lookup_room_booking as lookup
    return lookup(email, booking_ref)


@frappe.whitelist()
def get_my_session_reservations():
    """Get current user's session reservations."""
    email = frappe.session.user
    from bookings.bookings.doctype.reservation.reservation import get_reservations_by_email
    return get_reservations_by_email(email)


@frappe.whitelist()
def get_my_tutor_bookings():
    """Get bookings for items owned by current user as tutor."""
    user = frappe.session.user
    from bookings.bookings.doctype.reservation.reservation import get_tutor_reservations
    return get_tutor_reservations(user)


@frappe.whitelist()
def get_item_reservations(item):
    """Get all reservations for an item (admin or item owner)."""
    _require_can_manage(item)
    return frappe.get_all(
        "Reservation",
        filters={"reservation_item": item},
        fields=["name", "booking_ref", "customer_name", "customer_email",
                "from_time", "to_time", "status", "reservation_item", "slot"],
        order_by="from_time desc"
    )


@frappe.whitelist()
def get_all_reservations():
    """Get all person-item reservations (admin)."""
    _require_admin()
    persons = frappe.get_all("Reservation Item", filters={"item_type": "Person"}, pluck="name")
    if not persons:
        return []
    reservations = frappe.get_all(
        "Reservation",
        filters={
            "reservation_item": ["in", persons],
            "status": ["!=", "Cancelled"],
        },
        fields=["name", "booking_ref", "customer_name", "customer_email",
                "from_time", "to_time", "status", "reservation_item", "slot"],
        order_by="from_time desc"
    )
    return reservations


@frappe.whitelist()
def get_all_room_bookings():
    """Get all room bookings (admin)."""
    _require_admin()
    return frappe.get_all(
        "Room Booking",
        filters={"status": ["!=", "Cancelled"]},
        fields=["name", "booking_ref", "schedule_slot", "available_slot", "reservation_item",
                "customer_name", "customer_email", "booking_date", "from_time", "to_time",
                "status", "notes"],
        order_by="booking_date desc",
    )


@frappe.whitelist()
def get_current_user():
    """Get the current logged-in user info (or Guest)."""
    user = frappe.session.user

    if user == "Guest":
        return {"user": "Guest", "full_name": "Guest", "email": "", "roles": []}

    full_name = frappe.get_value("User", user, "full_name") or user

    roles = frappe.get_roles(user)

    return {
        "user": user,
        "full_name": full_name,
        "email": user,
        "roles": roles,
    }


@frappe.whitelist()
def update_booking_time(booking_ref, new_start_time, new_end_time):
    """Move a room booking to a new start/end time on the same date."""
    from bookings.bookings.doctype.room_booking.room_booking import (
        _available_slot_name,
        _increment_available_slot,
        _release_available_slot,
        _combine_datetime,
    )

    booking = frappe.get_doc("Room Booking", {"booking_ref": booking_ref})

    if booking.status == "Cancelled":
        frappe.throw("Cannot move a cancelled booking")

    room = booking.reservation_item
    date = str(booking.booking_date).split(" ")[0]
    start_hm = _time_of(new_start_time)
    if not start_hm:
        frappe.throw("A start time is required")

    target_slot_name = _available_slot_name(room, date, start_hm)

    if target_slot_name and target_slot_name != booking.available_slot:
        _increment_available_slot(
            target_slot_name,
            f"This room is fully booked at {start_hm} on {date}",
        )
        _release_available_slot(booking.available_slot)
        booking.available_slot = target_slot_name
    elif not target_slot_name:
        _release_available_slot(booking.available_slot)
        booking.available_slot = None

    if booking.schedule_slot:
        try:
            legacy = frappe.get_doc("Schedule Slot", booking.schedule_slot)
            legacy.status = "Free"
            legacy.booking_ref = None
            legacy.save(ignore_permissions=True)
        except Exception:
            pass

    booking.from_time = _combine_datetime(booking.booking_date, new_start_time)
    booking.to_time = _combine_datetime(booking.booking_date, new_end_time)
    booking.save(ignore_permissions=True)

    return {
        "success": True,
        "booking_ref": booking_ref,
        "start_time": new_start_time,
        "end_time": new_end_time,
    }


@frappe.whitelist()
def update_booking_details(booking_ref, notes=None, customer_name=None):
    """Update notes and/or booked-by name on a room booking."""
    booking = frappe.get_doc("Room Booking", {"booking_ref": booking_ref})

    if booking.status == "Cancelled":
        frappe.throw("Cannot edit a cancelled booking")

    if notes is not None:
        booking.notes = notes
    if customer_name is not None:
        booking.customer_name = customer_name
    booking.save(ignore_permissions=True)

    return {"success": True, "name": booking.name}


@frappe.whitelist()
def get_room_available_slots(room, start_date, end_date):
    """Get available slots for a room across a date range using the global time list.

    Slots that already exist (or have bookings) are returned as-is; the rest are
    returned as lightweight placeholders so the frontend can render the full grid
    without creating rows until a booking actually happens.
    """
    from frappe.utils import add_days
    from bookings.bookings.doctype.room_booking.room_booking import (
        _slot_booked_rooms,
        _room_capacity,
        _combine_datetime,
    )

    periods = _global_periods()
    user = frappe.session.user

    dates = []
    current = frappe.utils.getdate(start_date)
    end = frappe.utils.getdate(end_date)
    while current <= end:
        dates.append(current)
        current = add_days(current, 1)

    result = []
    for date in dates:
        date_str = frappe.utils.format_date(date, "yyyy-MM-dd")
        for period in periods:
            start_hm = _time_of(period.get("start_time"))
            end_hm = _time_of(period.get("end_time"))
            if not start_hm:
                continue

            booked_rows = _slot_booked_rooms(room, date_str, start_hm)
            booked = len(booked_rows)

            slot = _available_slot_doc(room, date_str, start_hm, end_hm)
            capacity = slot.capacity if slot else _room_capacity(room)

            slot_datetime = datetime.strptime(_combine_datetime(date_str, start_hm), "%Y-%m-%d %H:%M:%S")
            is_past = slot_datetime < datetime.now()
            is_full = booked >= capacity
            status = "past" if is_past else ("booked" if is_full else "free")

            my_ref = next(
                (r["booking_ref"] for r in booked_rows if r.get("customer_email") == user),
                None,
            )
            primary = (
                next((r for r in booked_rows if r.get("customer_email") == user), None)
                or (booked_rows[0] if booked_rows else None)
            )

            result.append({
                "name": slot.name if slot else "",
                "reservation_item": room,
                "slot_date": date_str,
                "start_time": slot.start_time if slot else _combine_datetime(date_str, start_hm),
                "end_time": slot.end_time if slot else _combine_datetime(date_str, end_hm),
                "capacity": capacity,
                "booked": booked,
                "is_full": 1 if is_full else 0,
                "status": status,
                "bookers": [
                    {
                        "booking_ref": r["booking_ref"],
                        "customer_name": r["customer_name"],
                        "notes": r.get("notes"),
                    }
                    for r in booked_rows
                ],
                "my_booking_ref": my_ref,
                "booking_ref": my_ref or (primary["booking_ref"] if primary else None),
                "booked_by": primary["customer_name"] if primary else "",
                "description": primary.get("notes") if primary else "",
            })
    return result


def _available_slot_doc(room, date_str, start_hm, end_hm):
    """Return the persisted Available Slot for a room/date/start, or None."""
    from bookings.bookings.doctype.room_booking.room_booking import _available_slot_name
    name = _available_slot_name(room, date_str, start_hm)
    if name:
        return frappe.get_doc("Available Slot", name)
    return None


@frappe.whitelist()
def book_room_slot(room, date, start_time, end_time, notes=None,
                   customer_name=None, customer_email=None):
    """Book one seat on a room's Available Slot (capacity-aware, atomic)."""
    from bookings.bookings.doctype.room_booking.room_booking import (
        _ensure_available_slot,
        _increment_available_slot,
        _combine_datetime,
        generate_booking_ref,
    )

    user = frappe.session.user
    if not customer_name:
        customer_name = frappe.get_value("User", user, "full_name") or user
    if not customer_email:
        customer_email = user

    start_hm = _time_of(start_time)
    end_hm = _time_of(end_time)
    if not start_hm:
        frappe.throw("A start time is required")

    slot_doc = _ensure_available_slot(room, date, start_hm, end_hm)
    _increment_available_slot(
        slot_doc.name,
        f"This room is fully booked at {start_hm} on {date}",
    )

    booking = frappe.get_doc({
        "doctype": "Room Booking",
        "available_slot": slot_doc.name,
        "reservation_item": room,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "booking_date": date,
        "from_time": _combine_datetime(date, start_hm),
        "to_time": _combine_datetime(date, end_hm),
        "notes": notes,
        "status": "Confirmed",
        "booking_ref": generate_booking_ref(),
    })
    booking.insert(ignore_permissions=True)

    return {
        "name": booking.name,
        "booking_ref": booking.booking_ref,
        "available_slot": slot_doc.name,
    }


@frappe.whitelist()
def book_room_recurring(room, dates, start_time, end_time, notes=None,
                        customer_name=None, customer_email=None):
    """Create room bookings across multiple dates for the same time."""
    import json

    if isinstance(dates, str):
        try:
            dates = json.loads(dates)
        except Exception:
            dates = [d.strip() for d in dates.split(",") if d.strip()]

    if not _time_of(start_time):
        frappe.throw("A start time is required")

    created = []
    for slot_date in dates:
        try:
            res = book_room_slot(
                room, slot_date, start_time, end_time, notes, customer_name, customer_email
            )
        except Exception:
            continue
        created.append({"date": slot_date, "booking_ref": res["booking_ref"]})

    return {"success": True, "created": created}


@frappe.whitelist()
def update_slot_details(slot, description=None, booked_by=None):
    """Update description and booked-by info on a schedule slot."""
    slot_doc = frappe.get_doc("Schedule Slot", slot)

    if description is not None:
        slot_doc.description = description
    if booked_by is not None:
        slot_doc.booked_by = booked_by
    slot_doc.save(ignore_permissions=True)

    return {
        "success": True,
        "name": slot_doc.name,
        "description": slot_doc.description,
        "booked_by": slot_doc.booked_by,
    }


@frappe.whitelist()
def create_recurring_room_bookings(schedule, dates, period_number, notes=None):
    """Create room bookings across multiple dates for the same period."""
    import json

    if isinstance(dates, str):
        try:
            dates = json.loads(dates)
        except Exception:
            dates = [d.strip() for d in dates.split(",") if d.strip()]

    from bookings.bookings.doctype.schedule_slot.schedule_slot import get_or_create_slot
    from bookings.bookings.doctype.room_booking.room_booking import create_room_booking

    created = []
    last_booking = None
    for slot_date in dates:
        slot = get_or_create_slot(schedule, slot_date, period_number)
        if slot.status == "Booked":
            continue
        last_booking = create_room_booking(slot.name, notes)
        created.append({
            "date": slot_date,
            "slot": slot.name,
            "name": last_booking.get("name"),
            "booking_ref": last_booking.get("booking_ref"),
        })

    return {"success": True, "created": created}


# ---------------------------------------------------------------------------
# Admin endpoints (require System Manager / Bookings Manager role)
# ---------------------------------------------------------------------------

def _is_admin():
    return "System Manager" in frappe.get_roles() or "Bookings Manager" in frappe.get_roles()


def _require_admin():
    if not _is_admin():
        frappe.throw("Not permitted", frappe.PermissionError)


def _require_can_manage(item):
    """Admins may manage any item; other users only items assigned to them."""
    if _is_admin():
        return
    owner = frappe.db.get_value("Reservation Item", item, "user")
    if owner != frappe.session.user:
        frappe.throw("Not permitted", frappe.PermissionError)


def _coerce_list(value):
    import json
    if isinstance(value, (list, tuple)):
        return list(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return [v.strip() for v in value.split(",") if v.strip()]
    return []


def _item_booking_count(item):
    """Count active bookings referencing a Reservation Item."""
    confirmed_available = frappe.db.count("Available Slot", filters={"reservation_item": item, "booked": [">", 0]})
    booked_slots = frappe.db.count("Schedule Slot", filters={"reservation_item": item, "status": "Booked"})
    room_bookings = frappe.db.count("Room Booking", filters={"reservation_item": item, "status": "Confirmed"})
    return int(confirmed_available) + int(booked_slots) + int(room_bookings)


@frappe.whitelist()
def get_all_items():
    """Get all reservation items (admin: includes inactive, full fields)."""
    _require_admin()
    return frappe.get_all(
        "Reservation Item",
        fields=["name", "item_name", "item_type", "class", "user", "is_active",
                "subtitle", "group", "capacity", "location", "features"],
        order_by="item_name"
    )


@frappe.whitelist()
def create_item(data):
    """Create a Reservation Item (Person / Asset / Room)."""
    _require_admin()
    d = data or {}
    doc = frappe.get_doc({
        "doctype": "Reservation Item",
        "item_name": d.get("item_name") or d.get("name"),
        "subtitle": d.get("subtitle") or "",
        "item_type": d.get("item_type") or "Person",
        "class": d.get("class") or "",
        "user": d.get("user") or None,
        "group": d.get("group") or None,
        "capacity": d.get("capacity") or 0,
        "location": d.get("location") or "",
        "features": d.get("features") or "",
        "is_active": 1 if d.get("is_active", 1) else 0,
    })
    doc.insert(ignore_permissions=True)
    return {"name": doc.name}


@frappe.whitelist()
def update_item(name, data):
    """Update a Reservation Item."""
    _require_admin()
    doc = frappe.get_doc("Reservation Item", name)
    d = data or {}
    for key, field in {
        "item_name": "item_name",
        "subtitle": "subtitle",
        "item_type": "item_type",
        "class": "class",
        "user": "user",
        "group": "group",
        "capacity": "capacity",
        "location": "location",
        "features": "features",
        "is_active": "is_active",
    }.items():
        if key in d:
            doc.set(field, d[key])
    doc.save(ignore_permissions=True)
    return {"success": True, "name": doc.name}


@frappe.whitelist()
def delete_item(name, force=0):
    """Delete a Reservation Item. Returns has_bookings if bookings exist and not forced."""
    _require_admin()
    force = 1 if force in (1, "1", "true", True) else 0
    count = _item_booking_count(name)
    if count > 0 and not force:
        return {"has_bookings": count}

    frappe.db.delete("Available Slot", {"reservation_item": name})
    frappe.db.delete("Room Booking", {"reservation_item": name})
    frappe.db.delete("Schedule Slot", {"reservation_item": name})
    frappe.delete_doc("Reservation Item", name, force=True, ignore_permissions=True)
    return {"success": True}


@frappe.whitelist()
def get_groups():
    """List all item groups."""
    _require_admin()
    return frappe.get_all("Item Group", fields=["name", "group_name", "description"], order_by="group_name")


@frappe.whitelist()
def create_group(group_name, description=None):
    """Create an item group."""
    _require_admin()
    doc = frappe.get_doc({
        "doctype": "Item Group",
        "group_name": group_name,
        "description": description,
    })
    doc.insert(ignore_permissions=True)
    return {"name": doc.name, "group_name": doc.group_name}


@frappe.whitelist()
def update_group(name, group_name=None, description=None):
    """Rename or update an item group."""
    _require_admin()
    doc = frappe.get_doc("Item Group", name)
    if group_name is not None:
        doc.group_name = group_name
    if description is not None:
        doc.description = description
    doc.save(ignore_permissions=True)
    return {"success": True, "name": doc.name, "group_name": doc.group_name}


@frappe.whitelist()
def delete_group(name):
    """Delete an item group. Returns has_items if items reference it."""
    _require_admin()
    has_items = frappe.db.count("Reservation Item", filters={"group": name})
    if has_items:
        return {"has_items": has_items}
    frappe.delete_doc("Item Group", name, force=True, ignore_permissions=True)
    return {"success": True}


@frappe.whitelist()
def get_users():
    """List enabled users holding the Bookings Manager or Bookings User role."""
    _require_admin()
    users = frappe.get_all(
        "User",
        filters={"enabled": 1, "name": ["not in", ["Guest"]]},
        fields=["name", "full_name", "email"],
        order_by="full_name asc"
    )
    result = []
    for u in users:
        roles = frappe.get_roles(u.name)
        is_manager = "Bookings Manager" in roles
        if not is_manager and "Bookings User" not in roles:
            continue
        result.append({
            "name": u.name,
            "email": u.email or u.name,
            "full_name": u.full_name or u.name,
            "roles": roles,
            "is_admin": is_manager,
        })
    return result


@frappe.whitelist()
def create_user(email, full_name=None, password=None, role="user"):
    """Create a Frappe user. role = 'admin' assigns System Manager."""
    _require_admin()
    email = (email or "").strip()
    if not email:
        frappe.throw("Email is required")
    if frappe.db.exists("User", email):
        frappe.throw("User already exists")

    doc = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": (full_name or email).strip(),
        "send_welcome_email": 0,
    })
    if password:
        doc.new_password = password
    if role == "admin":
        doc.append("roles", {"role": "System Manager"})
    doc.insert(ignore_permissions=True)
    return {"success": True, "name": email}


@frappe.whitelist()
def update_user(name, full_name=None, role=None):
    """Update a Frappe user's full name and admin role."""
    _require_admin()
    doc = frappe.get_doc("User", name)
    if full_name is not None:
        doc.first_name = (full_name or name).strip()
    if role is not None:
        has_sm = any((r.role == "System Manager") for r in doc.roles)
        want_sm = role == "admin"
        if want_sm and not has_sm:
            doc.append("roles", {"role": "System Manager"})
        elif not want_sm and has_sm:
            doc.roles = [r for r in doc.roles if r.role != "System Manager"]
    doc.save(ignore_permissions=True)
    return {"success": True}


@frappe.whitelist()
def delete_user(name):
    """Delete a Frappe user (cannot delete self or Administrator)."""
    _require_admin()
    if name == frappe.session.user:
        frappe.throw("You cannot delete your own account")
    if name == "Administrator":
        frappe.throw("You cannot delete the Administrator user")
    frappe.delete_doc("User", name, force=True, ignore_permissions=True)
    return {"success": True}


@frappe.whitelist()
def add_available_slots(item, date, start_time, end_time, duration=30, capacity=None):
    """Create Available Slot records for an item between start and end at intervals."""
    _require_can_manage(item)
    return _create_slots(item, [date], start_time, end_time, duration, capacity)


@frappe.whitelist()
def bulk_add_available_slots(items, dates, start_time, end_time, duration=30, capacity=None):
    """Create Available Slot records across multiple items and dates."""
    _require_admin()
    item_list = _coerce_list(items)
    date_list = _coerce_list(dates)
    return _create_slots(item_list, date_list, start_time, end_time, duration, capacity)


def _create_slots(items, dates, start_time, end_time, duration, capacity=None):
    from datetime import datetime, timedelta
    from frappe.utils import now_datetime

    from bookings.bookings.doctype.room_booking.room_booking import _room_capacity

    item_list = [items] if isinstance(items, str) else items
    duration = int(duration or 30)
    if duration <= 0:
        frappe.throw("Duration must be positive")

    created = 0
    for item in item_list:
        item_type = frappe.db.get_value("Reservation Item", item, "item_type") or "Person"
        slot_capacity = int(capacity or 0) or (_room_capacity(item) if item_type == "Room" else 1)
        for date in dates:
            start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
            current = start
            while current + timedelta(minutes=duration) <= end:
                existing = frappe.db.exists("Available Slot", {
                    "reservation_item": item,
                    "start_time": current.strftime("%Y-%m-%d %H:%M:%S"),
                })
                if not existing:
                    doc = frappe.get_doc({
                        "doctype": "Available Slot",
                        "reservation_item": item,
                        "slot_date": date,
                        "start_time": current.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": (current + timedelta(minutes=duration)).strftime("%Y-%m-%d %H:%M:%S"),
                        "capacity": slot_capacity,
                        "booked": 0,
                        "is_full": 0,
                    })
                    doc.insert(ignore_permissions=True)
                    created += 1
                current = current + timedelta(minutes=duration)
    frappe.db.commit()
    return {"success": True, "created": created}


@frappe.whitelist()
def delete_available_slot(name):
    """Delete an Available Slot. Returns has_bookings if it has bookings."""
    item = frappe.db.get_value("Available Slot", name, "reservation_item")
    _require_can_manage(item)
    booked = frappe.db.get_value("Available Slot", name, "booked") or 0
    if int(booked) > 0:
        return {"has_bookings": int(booked)}
    frappe.delete_doc("Available Slot", name, force=True, ignore_permissions=True)
    return {"success": True}
