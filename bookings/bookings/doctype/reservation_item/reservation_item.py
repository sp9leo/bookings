# Copyright (c) 2026, osaz and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def get_active_items(item_type=None):
    """Get all active reservation items, optionally filtered by type."""
    filters = {"is_active": 1}
    if item_type:
        filters["item_type"] = item_type
    
    items = frappe.get_all(
        "Reservation Item",
        filters=filters,
        fields=["name", "item_name", "item_type", "class", "user"],
        order_by="item_name"
    )
    return items


@frappe.whitelist()
def get_item(name):
    """Get a single reservation item with full details."""
    return frappe.get_doc("Reservation Item", name)


import frappe
from frappe.model.document import Document


class ReservationItem(Document):
	pass
