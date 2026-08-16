# NASA Natural Events Tracker

Flask app that pulls live natural event data (wildfires, storms, volcanoes,
floods, etc.) from NASA's EONET v3 API. Browse current/past events, click
into one for details.

## Setup

```
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

Open http://127.0.0.1:5000/

## OOP design

- `NaturalEvent` - one event from EONET: id, title, category, status,
  coords, date, magnitude/unit, source url. `is_active()`, `summary()`.
  `eonet_id` is private (`self.__eonet_id`) with a `get_eonet_id()` getter
  since it shouldn't change after creation.
- `WatchedEvent(NaturalEvent)` — adds `note`, `alert_active`, `toggle_alert()`.
- `EventFetcher` - the only class that touches `requests`. `fetch_events()`
  / `fetch_event()` hit the API and return `NaturalEvent` objects. Handles
  EONET's `[lon, lat]` coordinate order so it doesn't get flipped.

## Data flow

route in `app.py` -> `EventFetcher` hits EONET -> JSON turned into
`NaturalEvent` objects -> passed to a Jinja2 template -> HTML.

## Known limitations

- No watch list / notes / saved-event search / stats page (C, D, E skipped).
- `watched_events` and `search_log` tables get created on startup per the
  schema, just not written to yet.
