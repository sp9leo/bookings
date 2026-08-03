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
        fields=["name"],
        order_by="name"
    )
    
    result = []
    for schedule in schedules:
        doc = frappe.get_doc("Schedule", schedule.name)
        result.append({
            "name": doc.name,
            "applies_to": doc.applies_to,
            "reservation_item": doc.reservation_item,
            "periods": [
                {
                    "period_number": p.period_number,
                    "start_time": p.start_time,
                    "end_time": p.end_time,
                    "label": p.label,
                }
                for p in doc.schedule_periods
            ],
        })
    
    return result


@frappe.whitelist()
def get_schedule(name):
    """Get a single schedule with its periods."""
    doc = frappe.get_doc("Schedule", name)
    return {
        "name": doc.name,
        "applies_to": doc.applies_to,
        "reservation_item": doc.reservation_item,
        "periods": [
            {
                "period_number": p.period_number,
                "start_time": p.start_time,
                "end_time": p.end_time,
                "label": p.label,
            }
            for p in doc.schedule_periods
        ],
    }


import frappe
from frappe.model.document import Document


class Schedule(Document):
	pass
