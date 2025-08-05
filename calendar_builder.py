import os
import csv
from datetime import datetime
from ics import Calendar, Event

INPUT_FILE = "data/master_events.txt"
OUTPUT_ICS_DIR = "output/ics"
BASE_URL = "https://eventfeedsproject.netlify.app/output/ics/"

os.makedirs(OUTPUT_ICS_DIR, exist_ok=True)

def format_local_impact(e, is_error=False):
    desc_parts = []
    if e['description'].lower() != "n/a":
        desc_parts.append(e['description'])
    if e['notes'].lower() != "n/a":
        desc_parts.append(e['notes'])

    local_impact = (
        f"🎪 Venue: {e['venue']} | 🎟️ Status: {e['status']} | "
        f"👥 Capacity: {e['capacity']} | 🚪 Doors: {e['doors_open']}–{e['end']} | "
        f"🔥 Busyness: {e['busy_start']}–{e['busy_end']} | "
        f"📝 {'; '.join(desc_parts)}"
    )
    if is_error:
        local_impact = "⚠️ This is an error event. Please review manually.\n" + local_impact
    return local_impact

events_by_area = {}

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="|")
    for row in reader:
        if len(row) != 14:
            continue

        (date_str, artist, url, area, venue, capacity, doors_open, start, end,
         status, notes, busy_start, busy_end, description) = [x.strip() for x in row]

        key = area.replace("’", "'").strip()
        events_by_area.setdefault(key, []).append({
            "date": date_str,
            "artist": artist,
            "url": url,
            "area": key,
            "venue": venue,
            "capacity": capacity,
            "doors_open": doors_open,
            "start": start,
            "end": end,
            "status": status,
            "notes": notes,
            "busy_start": busy_start,
            "busy_end": busy_end,
            "description": description
        })

# Generate ICS per area
all_london = Calendar()

for area, events in events_by_area.items():
    cal = Calendar()
    for e in events:
        event = Event()
        event.name = e['artist']
        event.url = e['url']
        is_error = False

        try:
            start_dt = datetime.strptime(f"{e['date']} {e['start']}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{e['date']} {e['end']}", "%Y-%m-%d %H:%M")
            if end_dt <= start_dt:
                raise ValueError
        except:
            start_dt = datetime.strptime(f"{e['date']} 18:00", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{e['date']} 18:30", "%Y-%m-%d %H:%M")
            is_error = True

        event.begin = start_dt
        event.end = end_dt
        event.description = format_local_impact(e, is_error)
        cal.events.add(event)
        all_london.events.add(event)

    # Save area ICS
    area_slug = area.replace(" ", "_")
    ics_path = os.path.join(OUTPUT_ICS_DIR, f"{area_slug}_Events.ics")
    with open(ics_path, "w", encoding="utf-8") as f:
        f.writelines(cal.serialize_iter())

# Save All London ICS
with open(os.path.join(OUTPUT_ICS_DIR, "All_London_Events.ics"), "w", encoding="utf-8") as f:
    f.writelines(all_london.serialize_iter())
