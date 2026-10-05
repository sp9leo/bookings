"""Audit: every @frappe.whitelist() endpoint in api.py must call a guard.

Run from the repo root:
    py -3 scripts/check_endpoint_guards.py [path/to/api.py]
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

GUARDS = {
    "_require_bookings_user",
    "_require_admin",
    "_require_can_manage",
    "_require_booking_access",
    "_require_self_or_admin",
    "_validate_booking_horizon",
}

# Endpoints that are deliberately reachable without a Bookings role.
ALLOWLIST = {
    "get_current_user",  # returns identity + roles so the UI can explain a denial
}


def audit(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    endpoints: list[tuple[str, bool, list[str]]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            f = dec.func
            if not (isinstance(f, ast.Attribute) and f.attr == "whitelist"):
                continue
            allow_guest = any(
                kw.arg == "allow_guest" and isinstance(kw.value, ast.Constant) and kw.value.value
                for kw in dec.keywords
            )
            calls = {
                n.func.id
                for n in ast.walk(node)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            }
            endpoints.append((node.name, allow_guest, sorted(calls & GUARDS)))

    unguarded, guest, ok = [], 0, 0
    for name, allow_guest, guards in sorted(endpoints):
        if allow_guest:
            guest += 1
        elif guards or name in ALLOWLIST:
            ok += 1
        else:
            unguarded.append(name)

    print(f"{path}")
    print(f"  whitelisted endpoints : {len(endpoints)}")
    print(f"  guest-accessible      : {guest}")
    print(f"  guarded               : {ok}")
    print(f"  UNGUARDED             : {len(unguarded)}")

    for name in unguarded:
        print(f"    !! {name}  (@frappe.whitelist() with no permission guard)")

    if unguarded:
        print("\nFAIL: an authenticated non-member could reach the endpoints above.")
        return 1
    print("\nOK: every non-guest endpoint enforces access control.")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("bookings/api.py")
    raise SystemExit(audit(target))