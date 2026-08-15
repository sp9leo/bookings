# Copyright (c) 2026, osaz and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def get_available_slots(item=None, date=None):
    """Get available slots for an item on a specific date."""
    filters = {"is_full": 0}
    
    if item:
        filters["reservation_item"] = item
    
    if date:
        filters["slot_date"] = date
    
    slots = frappe.get_all(
        "Available Slot",
        filters=filters,
        fields=["name", "slot_date", "reservation_item", "start_time", "end_time", "capacity", "booked"],
        order_by="slot_date, start_time"
    )
    
    return slots


@frappe.whitelist()
def get_slots_for_item(item):
    """Get all future available slots for an item."""
    slots = frappe.get_all(
        "Available Slot",
        filters={
            "reservation_item": item,
            "slot_date": [">=", frappe.utils.today()]
        },
        fields=["name", "slot_date", "reservation_item", "start_time", "end_time", "capacity", "booked"],
        order_by="slot_date, start_time"
    )
    return slots


def update_is_full(doc, method):
    """Update is_full based on booked count."""
    doc.is_full = 1 if doc.booked >= doc.capacity else 0


import frappe
from frappe.model.document import Document


class AvailableSlot(Document):
	pass
