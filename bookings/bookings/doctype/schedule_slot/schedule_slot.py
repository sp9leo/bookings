# Copyright (c) 2026, osaz and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days


@frappe.whitelist()
def get_schedule_slots(schedule=None, item=None, date=None, start_date=None, end_date=None):
    """Get schedule slots with optional filters."""
    filters = {}
    
    if schedule:
        filters["schedule"] = schedule
    if item:
        filters["reservation_item"] = item
    if date:
        filters["slot_date"] = date
    if start_date and end_date:
        filters["slot_date"] = ["between", [start_date, end_date]]
    
    slots = frappe.get_all(
        "Schedule Slot",
        filters=filters,
        fields=["name", "schedule", "reservation_item", "slot_date", 
                "period_number", "start_time", "end_time", "status", "booking_ref",
                "booked_by", "description"],
        order_by="slot_date, start_time"
    )
    return slots


@frappe.whitelist()
def get_slots_for_room(item, start_date, end_date):
    """Get slots for a room within a date range."""
    return get_schedule_slots(item=item, start_date=start_date, end_date=end_date)


@frappe.whitelist()
def get_or_create_slot(schedule, slot_date, period_number):
    """Get an existing slot or create a new one on-demand."""
    existing = frappe.get_value(
        "Schedule Slot",
        {"schedule": schedule, "slot_date": slot_date, "period_number": period_number},
        "name"
    )
    
    if existing:
        return frappe.get_doc("Schedule Slot", existing)
    
    schedule_doc = frappe.get_doc("Schedule", schedule)
    period = frappe.get_value(
        "Schedule Periods",
        {"parent": schedule, "period_number": period_number},
        "*",
        as_dict=True
    )
    
    if not period:
        frappe.throw(f"Period {period_number} not found in schedule {schedule}")
    
    slot = frappe.get_doc({
        "doctype": "Schedule Slot",
        "schedule": schedule,
        "reservation_item": schedule_doc.reservation_item,
        "slot_date": slot_date,
        "period_number": period_number,
        "start_time": period.start_time,
        "end_time": period.end_time,
        "status": "Free"
    })
    slot.insert(ignore_permissions=True)
    
    return slot


@frappe.whitelist()
def get_week_slots(item, week_start_date):
    """Get all slots for a room for a full week (Mon-Sun)."""
    slots = []
    for i in range(7):
        date = add_days(week_start_date, i)
        date_str = frappe.utils.format_date(date, "yyyy-MM-dd")
        day_slots = get_schedule_slots(item=item, date=date_str)
        slots.extend(day_slots)
    return slots


import frappe
from frappe.model.document import Document


class ScheduleSlot(Document):
	pass
