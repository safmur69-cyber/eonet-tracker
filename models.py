import requests

BASE_URL = "https://eonet.gsfc.nasa.gov/api/v3"


class NaturalEvent:
    def __init__(self, eonet_id, title, category, status, latitude, longitude,
                 event_date, magnitude, mag_unit, source_url):
        self.__eonet_id = eonet_id
        self.title = title
        self.category = category
        self.status = status
        self.latitude = latitude
        self.longitude = longitude
        self.event_date = event_date
        self.magnitude = magnitude
        self.mag_unit = mag_unit
        self.source_url = source_url

    def get_eonet_id(self):
        return self.__eonet_id

    def is_active(self):
        return self.status == "open"

    def summary(self):
        return f"[{self.category}] {self.title} - {self.status}"

    def __str__(self):
        return self.summary()


class WatchedEvent(NaturalEvent):
    def __init__(self, eonet_id, title, category, status, latitude, longitude,
                 event_date, magnitude, mag_unit, source_url, note="", alert_active=False):
        super().__init__(eonet_id, title, category, status, latitude, longitude,
                          event_date, magnitude, mag_unit, source_url)
        self.note = note
        self.alert_active = alert_active

    def toggle_alert(self):
        self.alert_active = not self.alert_active
        return self.alert_active

    def summary(self):
        base = super().summary()
        if self.note:
            base += f" | note: {self.note}"
        if self.alert_active:
            base += " | alert ON"
        return base


class EventFetcher:

    def fetch_events(self, status="open", category=None, days=30, limit=50):
        params = {"status": status, "limit": limit, "days": days}
        if category:
            params["category"] = category

        response = requests.get(f"{BASE_URL}/events", params=params, timeout=10)
        response.raise_for_status()
        raw_events = response.json()["events"]
        return [self.__build_event(item) for item in raw_events]

    def fetch_event(self, eonet_id):
        response = requests.get(f"{BASE_URL}/events/{eonet_id}", timeout=10)
        response.raise_for_status()
        return self.__build_event(response.json())

    def __build_event(self, item):
        category = item["categories"][0]["title"] if item.get("categories") else "Unknown"
        status = "closed" if item.get("closed") else "open"

        latitude = None
        longitude = None
        event_date = None
        geometry = item.get("geometry")
        if geometry:
            first_point = geometry[0]
            event_date = first_point.get("date", "")[:10]
            coords = first_point.get("coordinates")
            if first_point.get("type") == "Point" and coords:
                longitude, latitude = coords[0], coords[1]

        source_url = ""
        if item.get("sources"):
            source_url = item["sources"][0].get("url", "")

        return NaturalEvent(
            eonet_id=item["id"],
            title=item["title"],
            category=category,
            status=status,
            latitude=latitude,
            longitude=longitude,
            event_date=event_date,
            magnitude=item.get("magnitudeValue"),
            mag_unit=item.get("magnitudeUnit"),
            source_url=source_url,
        )
