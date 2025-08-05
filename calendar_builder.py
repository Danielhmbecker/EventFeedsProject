import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from ics import Calendar, Event

# Paths
DATA_FILE = "data/master_events.txt"
TXT_DIR = "output/txt"
ICS_DIR = "output/ics"
FEEDS_INDEX = "output/feeds_index.txt"
NETLIFY_BASE_URL = "https://eventfeedslondon.netlify.app/output/ics"

# Ensure output directories exist
os.makedirs(TXT_DIR, exist_ok=True)
os.makedirs(ICS_DIR, exist_ok=True)

def format_local_impact(venue, capacity, doors_open, doors_close, ticket_url, tube, bus, notes, busy_start, busy_end):
    output = [
        f"📍 Venue: {venue} (Capacity: {capacity})",
        f"🚉 Access: {tube} (Tube) / {bus} (Bus)",
        f"🚪 Doors: {doors_open}–{doors_close}",
        f"🎟️ Tickets: {ticket_url}",
        f"🔥 Busyness: {busy_start} – {busy_end}",
    ]

    notes = notes.strip()
    if notes and notes.lower() != "n/a":
        if ";" in notes:
            note_lines = [f"• {n.strip()}" for n in notes.split(";") if n.strip()]
        else:
            note_lines = [f"• {notes}"]
        output.append("🗒️ Notes:\n" + "\n".join(note_lines))

    return "📊 Local Impact:\n" + "\n".join(output)

# Load and group events by area
area_events = defaultdict(list)

with open(DATA_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip() or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.strip().split("|")]
        if len(parts) < 15:
            print(f"⚠️ Skipping malformed line: {line}")
            continue

        (
            date_str, artist, url, area, venue, capacity, doors_open, start, end,
            description, status, notes, busy_start, busy_end, extra
        ) = parts

        event_data = {
            "date": date_str,
            "artist": artist,
            "url": url,
            "area": area,
            "venue": venue,
            "capacity": capacity,
            "doors_open": doors_open,
            "doors_close": "19:45",  # Static for now
            "start": start,
            "end": end,
            "description": description,
            "status": status,
            "notes": notes,
            "busy_start": busy_start,
            "busy_end": busy_end,
            "tube": extra,
            "bus": area  # Placeholder: use area name as dummy for bus
        }

        area_key = area.replace(" ", "_")
        area_events[area_key].append(event_data)

# Write feeds
active_feeds = []

for area_key, events in area_events.items():
    if not events:
        continue

    txt_path = os.path.join(TXT_DIR, f"{area_key}_Events.txt")
    txt_lines = [
        " | ".join([
            e["date"], e["artist"], e["url"], e["area"], e["venue"], e["capacity"],
            e["doors_open"], e["start"], e["end"], e["description"], e["status"],
            e["notes"], e["busy_start"], e["busy_end"], e["tube"]
        ]) for e in events
    ]
    txt_content = "\n".join(txt_lines) + "\n"
    if not os.path.exists(txt_path) or open(txt_path).read() != txt_content:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(txt_content)

    cal = Calendar()
    for e in events:
        try:
            start_dt = datetime.strptime(f'{e["date"]} {e["start"]}', "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f'{e["date"]} {e["end"]}', "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"⚠️ Invalid datetime for event: {e}")
            continue

        event = Event()
        event.name = f"{e['artist']} @ {e['venue']}"
        event.begin = start_dt
        event.end = end_dt
        event.location = e["venue"]
        event.description = (
            f"{e['description']}\n\n" +
            format_local_impact(e['venue'], e['capacity'], e['doors_open'], e['doors_close'],
                                e['url'], e['tube'], e['bus'], e['notes'], e['busy_start'], e['busy_end'])
        )
        cal.events.add(event)

    ics_path = os.path.join(ICS_DIR, f"{area_key}_Events.ics")
    new_ics = cal.serialize()
    if not os.path.exists(ics_path) or open(ics_path).read() != new_ics:
        with open(ics_path, "w", encoding="utf-8") as f:
            f.write(new_ics)

    active_feeds.append(f"{NETLIFY_BASE_URL}/{area_key}_Events.ics")

# Cleanup
existing_txt = {p.name for p in Path(TXT_DIR).glob("*_Events.txt")}
existing_ics = {p.name for p in Path(ICS_DIR).glob("*_Events.ics")}
valid_files = {f"{k}_Events.txt" for k in area_events} | {f"{k}_Events.ics" for k in area_events}

for f in existing_txt - valid_files:
    os.remove(os.path.join(TXT_DIR, f))
for f in existing_ics - valid_files:
    os.remove(os.path.join(ICS_DIR, f))

with open(FEEDS_INDEX, "w", encoding="utf-8") as f:
    for url in sorted(active_feeds):
        f.write(url + "\n")

print(f"✅ Done. Generated {len(active_feeds)} area feeds.")
