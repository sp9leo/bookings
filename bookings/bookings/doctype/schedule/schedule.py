# Copyright (c) 2026, osaz and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def get_schedules(item_type=None):
    """Get all schedules, optionally filtered by type."""
    filters = {}
    if item_type:
        filters["applies_to"] = item_type
    
    schedules = frappe.get_all(
        "Schedule",
        filters=filters,
        fields=["name", "applies_to", "reservation_item"],
        order_by="name"
    )
    
    for schedule in schedules:
        periods = frappe.get_all(
            "Schedule Periods",
            filters={"parent": schedule.name},
            fields=["period_number", "start_time", "end_time", "label"],
            order_by="period_number"
        )
        schedule.periods = periods
    
    return schedules


@frappe.whitelist()
def get_schedule(name):
    """Get a single schedule with its periods."""
    doc = frappe.get_doc("Schedule", name)
    periods = frappe.get_all(
        "Schedule Periods",
        filters={"parent": name},
        fields=["period_number", "start_time", "end_time", "label"],
        order_by="period_number"
    )
    return {
        "name": doc.name,
        "applies_to": doc.applies_to,
        "reservation_item": doc.reservation_item,
        "periods": periods
    }


import frappe
from frappe.model.document import Document


class Schedule(Document):
	pass
