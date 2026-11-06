# Copyright (c) 2026, osaz and contributors
# For license information, please see license.txt

import frappe
import secrets
import string
from frappe.utils import now_datetime

from bookings.formatting import format_slovenian_date


def generate_booking_ref():
    """Generate a 6-character booking reference."""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(secrets.choice(chars) for _ in range(6))


def generate_access_token():
    """Generate a secure access token."""
    return secrets.token_urlsafe(32)


def _combine_datetime(date_val, time_val):
    """Combine a date with a time/datetime value into a 'YYYY-MM-DD HH:MM:SS' string.

    frappe.utils.combine_datetime was removed from the framework, so this
    replaces it for Available Slot values (datetime strings/objects).
    """
    date_str = str(date_val).split(" ")[0].strip()
    time_str = str(time_val).split(" ")[-1].strip()
    if time_str.count(":") == 1:
        time_str = f"{time_str}:00"
    return f"{date_str} {time_str}"


@frappe.whitelist()
def create_reservation(slot, customer_name, customer_email, notes=None, child_name=None, phone=None):
    """Create a new reservation from an available slot."""
    slot_doc = frappe.get_doc("Available Slot", slot)
    
    if slot_doc.is_full:
        frappe.throw("This slot is already fully booked")
    
    reservation = frappe.get_doc({
        "doctype": "Reservation",
        "reservation_item": slot_doc.reservation_item,
        "slot": slot,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "child_name": child_name,
        "phone": phone,
        "from_time": _combine_datetime(slot_doc.slot_date, slot_doc.start_time),
        "to_time": _combine_datetime(slot_doc.slot_date, slot_doc.end_time),
        "notes": notes,
        "status": "Confirmed",
        "booking_ref": generate_booking_ref(),
        "access_token": generate_access_token()
    })
    reservation.insert(ignore_permissions=True)
    
    slot_doc.booked = slot_doc.booked + 1
    slot_doc.is_full = 1 if slot_doc.booked >= slot_doc.capacity else 0
    slot_doc.save(ignore_permissions=True)
    
    return {
        "name": reservation.name,
        "booking_ref": reservation.booking_ref,
        "access_token": reservation.access_token
    }


@frappe.whitelist(allow_guest=True)
def get_reservation(email, booking_ref):
    """Get a reservation by email and booking reference."""
    reservation = frappe.get_value(
        "Reservation",
        {"customer_email": email, "booking_ref": booking_ref},
        "*",
        as_dict=True
    )
    if not reservation:
        return None
    return reservation


@frappe.whitelist(allow_guest=True)
def cancel_reservation(access_token):
    """Cancel a reservation using access token."""
    reservation = frappe.get_doc("Reservation", {"access_token": access_token})
    
    if reservation.status == "Cancelled":
        return {"success": False, "message": "Already cancelled"}
    
    slot_doc = frappe.get_doc("Available Slot", reservation.slot)
    slot_doc.booked = max(0, slot_doc.booked - 1)
    slot_doc.is_full = 1 if slot_doc.booked >= slot_doc.capacity else 0
    slot_doc.save(ignore_permissions=True)
    
    reservation.status = "Cancelled"
    reservation.cancellation_reason = "Cancelled by customer"
    reservation.save(ignore_permissions=True)
    
    return {"success": True, "message": "Reservation cancelled"}


@frappe.whitelist()
def get_reservations_by_email(email):
    """Get all reservations for an email."""
    reservations = frappe.get_all(
        "Reservation",
        filters={"customer_email": email},
        fields=["name", "booking_ref", "customer_name", "customer_email", 
                "child_name", "phone",
                "from_time", "to_time", "status", "reservation_item", "slot"],
        order_by="from_time desc"
    )
    return reservations


@frappe.whitelist()
def get_tutor_reservations(user):
    """Get all reservations for items owned by a tutor (via user link)."""
    items = frappe.get_all(
        "Reservation Item",
        filters={"user": user, "item_type": "Person"},
        pluck="name"
    )
    
    if not items:
        return []
    
    reservations = frappe.get_all(
        "Reservation",
        filters={
            "reservation_item": ["in", items],
            "status": ["!=", "Cancelled"]
        },
        fields=["name", "booking_ref", "customer_name", "customer_email",
                "child_name", "phone",
                "from_time", "to_time", "status", "reservation_item", "slot"],
        order_by="from_time asc"
    )
    return reservations


import frappe
from frappe.model.document import Document


class Reservation(Document):
    def validate(self):
        self.set_display_fields()

    def set_display_fields(self):
        """Keep email display values on the document.

        Frappe's Email Template preview renders against the document rather
        than the API context, so variables such as {{ date_str }} need real
        fields to work there as well.
        """
        from_time = frappe.utils.get_datetime(self.from_time) if self.from_time else None
        to_time = frappe.utils.get_datetime(self.to_time) if self.to_time else None

        self.date_str = format_slovenian_date(from_time) if from_time else ""
        self.time_from = from_time.strftime("%H:%M") if from_time else ""
        self.time_to = to_time.strftime("%H:%M") if to_time else ""

        item = (
            frappe.db.get_value(
                "Reservation Item",
                self.reservation_item,
                ["item_name", "item_type"],
                as_dict=True,
            )
            if self.reservation_item
            else None
        )
        self.item_name = (item.item_name if item else "") or ""
        item_type = (item.item_type if item else "") or ""
        manage_path = "/rooms/my" if item_type == "Room" else "/book/my"
        self.manage_url = frappe.utils.get_url() + manage_path
