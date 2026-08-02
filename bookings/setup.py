import frappe

ROLE_BOOKINGS_MANAGER = "Bookings Manager"


def ensure_bookings_manager_role():
    if not frappe.db.exists("Role", ROLE_BOOKINGS_MANAGER):
        frappe.get_doc(
            {
                "doctype": "Role",
                "name": ROLE_BOOKINGS_MANAGER,
                "desk_access": 0,
                "disabled": 0,
            }
        ).insert(ignore_permissions=True, ignore_if_duplicate=True)


def after_migrate():
    ensure_bookings_manager_role()
