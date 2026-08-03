# Copyright (c) 2026, osaz and contributors
# For license information, please see license.txt

import frappe
import secrets


def generate_booking_ref():
    """Generate a 6-character booking reference."""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(secrets.choice(chars) for _ in range(6))


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
    slot_doc.booked_by = user
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
    
    slot_doc = frappe.get_doc("Schedule Slot", booking.schedule_slot)
    slot_doc.status = "Free"
    slot_doc.booking_ref = None
    slot_doc.save(ignore_permissions=True)
    
    booking.status = "Cancelled"
    booking.save(ignore_permissions=True)
    
    return {"success": True, "message": "Booking cancelled"}


@frappe.whitelist()
def get_my_bookings(user=None):
    """Get all bookings for the current user or specified user."""
    if not user:
        user = frappe.session.user
    
    bookings = frappe.get_all(
        "Room Booking",
        filters={"customer_email": user},
        fields=["name", "booking_ref", "schedule_slot", "reservation_item",
                "customer_name", "customer_email", "booking_date", "from_time", "to_time", 
                "status", "notes"],
        order_by="booking_date desc"
    )
    return bookings


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
