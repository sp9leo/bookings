import frappe


def execute():
    if not frappe.db.exists("Role", "Bookings Manager"):
        frappe.get_doc(
            {
                "doctype": "Role",
                "name": "Bookings Manager",
                "desk_access": 0,
                "disabled": 0,
            }
        ).insert(ignore_permissions=True, ignore_if_duplicate=True)
