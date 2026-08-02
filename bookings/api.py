# Bookings Module API
# Public and internal endpoints for the booking system

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
    """Get available slots for an item."""
    filters = {
        "reservation_item": item,
        "is_full": 0
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
def get_schedule_for_room(item, start_date, end_date):
    """Get schedule slots for a room within a date range."""
    from bookings.bookings.doctype.schedule_slot.schedule_slot import get_schedule_slots
    return get_schedule_slots(item=item, start_date=start_date, end_date=end_date)


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
    booking = frappe.get_doc("Room Booking", {"booking_ref": booking_ref})

    if booking.status == "Cancelled":
        frappe.throw("Cannot move a cancelled booking")

    slot_doc = frappe.get_doc("Schedule Slot", booking.schedule_slot)
    slot_doc.start_time = new_start_time
    slot_doc.end_time = new_end_time
    slot_doc.save(ignore_permissions=True)

    booking.from_time = frappe.utils.combine_datetime(booking.booking_date, new_start_time)
    booking.to_time = frappe.utils.combine_datetime(booking.booking_date, new_end_time)
    booking.save(ignore_permissions=True)

    return {
        "success": True,
        "booking_ref": booking_ref,
        "start_time": new_start_time,
        "end_time": new_end_time,
    }


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
def add_available_slots(item, date, start_time, end_time, duration=30):
    """Create Available Slot records for an item between start and end at intervals."""
    _require_can_manage(item)
    return _create_slots(item, [date], start_time, end_time, duration)


@frappe.whitelist()
def bulk_add_available_slots(items, dates, start_time, end_time, duration=30):
    """Create Available Slot records across multiple items and dates."""
    _require_admin()
    item_list = _coerce_list(items)
    date_list = _coerce_list(dates)
    return _create_slots(item_list, date_list, start_time, end_time, duration)


def _create_slots(items, dates, start_time, end_time, duration):
    from datetime import datetime, timedelta
    from frappe.utils import now_datetime

    item_list = [items] if isinstance(items, str) else items
    duration = int(duration or 30)
    if duration <= 0:
        frappe.throw("Duration must be positive")

    created = 0
    for item in item_list:
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
                        "capacity": 1,
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
