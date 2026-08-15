# Bookings

Frappe app for a booking system for persons, assets and rooms.

## Installation

```bash
bench get-app https://github.com/sp9leo/bookings
bench install-app bookings
bench migrate
```

## Development

This app uses the default Frappe app layout. The Python API is exposed via
`api.py`; frontend lives in the separate repository
[`sp9leo/bookings-frontend`](https://github.com/sp9leo/bookings-frontend).
