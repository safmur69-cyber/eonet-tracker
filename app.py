import sqlite3

import requests
from flask import Flask, render_template, request, flash

from models import EventFetcher

app = Flask(__name__)
app.secret_key = "eonet-tracker-secret"

DB_PATH = "events.db"

CATEGORIES = [
    ("drought", "Drought"),
    ("dustHaze", "Dust and Haze"),
    ("earthquakes", "Earthquakes"),
    ("floods", "Floods"),
    ("landslides", "Landslides"),
    ("manmade", "Manmade"),
    ("seaLakeIce", "Sea and Lake Ice"),
    ("severeStorms", "Severe Storms"),
    ("snow", "Snow"),
    ("tempExtremes", "Temperature Extremes"),
    ("volcanoes", "Volcanoes"),
    ("waterColor", "Water Color"),
    ("wildfires", "Wildfires"),
]

fetcher = EventFetcher()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS watched_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eonet_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            category TEXT,
            status TEXT,
            latitude REAL,
            longitude REAL,
            event_date TEXT,
            magnitude REAL,
            mag_unit TEXT,
            source_url TEXT,
            note TEXT DEFAULT '',
            alert_active INTEGER DEFAULT 0,
            saved_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT NOT NULL UNIQUE,
            label TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS search_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_text TEXT,
            searched_at TEXT DEFAULT (datetime('now'))
        )
    """)

    for slug, label in CATEGORIES:
        conn.execute(
            "INSERT OR IGNORE INTO categories (slug, label) VALUES (?, ?)",
            (slug, label),
        )

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/browse")
def browse():
    category = request.args.get("category", "").strip()
    status = request.args.get("status", "open").strip()
    days_raw = request.args.get("days", "30").strip()

    try:
        days = int(days_raw)
    except ValueError:
        days = 30

    events = []
    try:
        events = fetcher.fetch_events(status=status, category=category or None, days=days)
    except requests.RequestException:
        flash("Could not reach the EONET API right now. Please try again in a moment.", "error")

    return render_template(
        "browse.html",
        events=events,
        categories=CATEGORIES,
        category=category,
        status=status,
        days=days,
    )


@app.route("/event/<eonet_id>")
def event_detail(eonet_id):
    event = None
    try:
        event = fetcher.fetch_event(eonet_id)
    except requests.RequestException:
        flash("Could not reach the EONET API right now. Please try again in a moment.", "error")

    return render_template("event_detail.html", event=event)


@app.errorhandler(404)
def page_not_found(_e):
    return render_template("404.html"), 404


init_db()

if __name__ == "__main__":
    app.run(debug=True)
