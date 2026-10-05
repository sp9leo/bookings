"""Diagnostic: explain which Schedule the room time-slot endpoints resolve to.

The app treats exactly one Schedule as the global room time-slot list. It is
discovered implicitly by api.py::_global_schedule_name():

    frappe.db.get_value(
        "Schedule",
        {"applies_to": "Room", "reservation_item": ("is", "not set")},
        "name",
    )

Anything that does not match that filter is invisible to the UI -- and
_sync_room_schedules() overwrites every Schedule that *does* have a
reservation_item, so hand-made room schedules silently revert. Run this before
changing anything to see which case you are in.

Run from the bench apps directory:

    bench --site <site> console
    >>> exec(open("apps/bookings/scripts/diagnose_global_schedule.py").read())

Or non-interactively:

    bench --site <site> execute bookings.scripts.diagnose_global_schedule

Exit code is 1 when the global schedule is ambiguous, missing, or empty.
"""

from __future__ import annotations

import frappe

GLOBAL_FILTER = {"applies_to": "Room", "reservation_item": ("is", "not set")}
ROOM_FILTER = {"applies_to": "Room", "reservation_item": ("is", "set")}

# Mirrors the frontend default in src/stores/booking.ts.
DEFAULT_TIMES = [
    "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00",
]


def _periods(name):
    doc = frappe.get_doc("Schedule", name)
    return [
        {
            "period_number": p.period_number,
            "start_time": p.start_time,
            "end_time": p.end_time,
            "label": p.label,
        }
        for p in doc.schedule_periods
    ]


def _describe(name, periods):
    starts = [str(p.get("start_time") or "")[:5] for p in periods]
    print(f"    {name}: {len(periods)} period(s)")
    if not periods:
        print("      -> EMPTY. get_global_time_slots() has no fallback here (unlike")
        print("         _global_periods()), so the UI renders an empty table.")
    else:
        print(f"      start_times: {', '.join(starts)}")
        missing_label = [p for p in periods if not p.get("label")]
        if missing_label:
            print("      -> some periods have no label; the UI falls back to the time.")


def main() -> int:
    print("=" * 72)
    print("ALL Schedule rows")
    print("=" * 72)
    rows = frappe.get_all(
        "Schedule",
        fields=["name", "applies_to", "reservation_item", "creation", "modified"],
        order_by="creation asc",
    )
    if not rows:
        print("  none. The next call to get_global_time_slots() will auto-create a")
        print("  default Room schedule.")
        return 1

    for row in rows:
        marker = " "
        if row["applies_to"] == "Room":
            marker = "*" if not row["reservation_item"] else "+"
        item = row["reservation_item"] or "-"
        print(f" {marker} {row['name']:<12} applies_to={row['applies_to']:<8} "
              f"reservation_item={item:<20} created={row['creation']}")

    print()
    print("=" * 72)
    print("GLOBAL candidates (applies_to=Room AND reservation_item is empty)")
    print("=" * 72)
    globals_ = frappe.get_all(
        "Schedule", filters=GLOBAL_FILTER, fields=["name"], order_by="creation desc"
    )
    if not globals_:
        print("  NONE -- api.py::_global_schedule_name() will SILENTLY auto-create a")
        print("  default 08:00-16:00 schedule. That is why your edits appear to be")
        print("  ignored: the app is reading a schedule you did not create.")
        print()
        print(f"  Defaults that would be written: {', '.join(DEFAULT_TIMES)}")
        print()
        print("  Check the '*'-marked rows above. A filled-in reservation_item or a")
        print("  different applies_to value will exclude them.")
        return 1

    for name in globals_:
        print(f"  {name}")
        _describe(name, _periods(name))

    print()
    print("=" * 72)
    print("PER-ROOM schedules (_sync_room_schedules overwrites these)")
    print("=" * 72)
    rooms = frappe.get_all("Schedule", filters=ROOM_FILTER, fields=["name", "reservation_item"],
                           order_by="reservation_item asc")
    if not rooms:
        print("  none yet; they are created lazily per room.")
    for row in rooms:
        print(f"  {row['name']:<12} room={row['reservation_item']}")
        _describe(row["name"], _periods(row["name"]))

    print()
    print("=" * 72)
    print("VERDICT")
    print("=" * 72)
    problems = []
    if len(globals_) > 1:
        names = ", ".join(globals_)
        problems.append(
            f"{len(globals_)} global candidates ({names}). Resolution is ambiguous;"
            " api.py now prefers the newest by creation desc, but you should delete"
            " the ones you do not want."
        )
    resolved = globals_[0]
    if not _periods(resolved):
        problems.append(
            f"{resolved} has no Schedule Periods rows. Add them, or use the admin"
            " Time Slots page, which creates them via save_global_time_slots."
        )
    for row in rows:
        if row["applies_to"] != "Room":
            continue
        if row["reservation_item"] and row["name"] == resolved:
            problems.append(f"{resolved} has both reservation_item set and no periods.")

    for problem in problems:
        print(f"  !! {problem}")
    if not problems:
        print(f"  OK: {resolved} is the only global schedule and it has periods.")
        print("  If the UI still shows stale times, it is a browser HTTP cache issue --")
        print("  the frontend now sends cache:'no-store' for this endpoint.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())