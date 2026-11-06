import frappe

ROLE_BOOKINGS_MANAGER = "Bookings Manager"
ROLE_BOOKINGS_USER = "Bookings User"


def ensure_user_color_field():
    if frappe.db.exists("Custom Field", {"dt": "User", "fieldname": "bookings_color"}):
        return
    frappe.get_doc(
        {
            "doctype": "Custom Field",
            "dt": "User",
            "fieldname": "bookings_color",
            "label": "Bookings Color",
            "fieldtype": "Color",
        }
    ).insert(ignore_permissions=True, ignore_if_duplicate=True)


def ensure_role(role_name, desk_access=0):
    if not frappe.db.exists("Role", role_name):
        frappe.get_doc(
            {
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": desk_access,
                "disabled": 0,
            }
        ).insert(ignore_permissions=True, ignore_if_duplicate=True)


def ensure_bookings_manager_role():
    ensure_role(ROLE_BOOKINGS_MANAGER)


def ensure_bookings_user_role():
    ensure_role(ROLE_BOOKINGS_USER)


def backfill_reservation_item_name():
    """Fill the read-only Item Name field for reservations created before it existed."""
    frappe.db.sql(
        """
        update `tabReservation` r
        join `tabReservation Item` i on i.name = r.reservation_item
        set r.item_name = i.item_name
        where ifnull(r.item_name, '') = ''
          and ifnull(r.reservation_item, '') != ''
        """
    )


def after_migrate():
    ensure_bookings_manager_role()
    ensure_bookings_user_role()
    ensure_user_color_field()
    backfill_reservation_item_name()
