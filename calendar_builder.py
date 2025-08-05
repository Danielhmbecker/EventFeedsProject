import os
import csv
from datetime import datetime, timedelta
from ics import Calendar, Event

BASE_URL = "https://eventfeedsproject.netlify.app/output/ics/"
INPUT_FILE = "data/master_events.txt"
OUTPUT_TXT_DIR = "output/txt"
OUTPUT_ICS_DIR = "output/ics"
INDEX_FILE = "output/feeds_index.txt"

os.makedirs(OUTPUT_TXT_DIR, exist_ok=True)
os.makedirs(OUTPUT_ICS_DIR, exist_ok=True)

events_by_area = {}

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="|")
    for row in reader:
        if len(row) != 14:
            print(f"Skipping invalid row: {row}")
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

def format_local_impact(e):
    notes_parts = []

    if e['description'] and e['description'].lower() != "n/a":
        notes_parts.append(e['description'])

    if e['notes'] and e['notes'].lower() != "n/a":
        notes_parts.append(e['notes'])

    local_impact = (
        f"🎪 Venue: {e['venue']} | "
        f"🎟️ Status: {e['status']} | "
        f"👥 Capacity: {e['capacity']} | "
        f"🚪 Doors: {e['doors_open']}–{e['end']} | "
        f"🔥 Busyness: {e['busy_start']}–{e['busy_end']} | "
        f"📝 {'; '.join(notes_parts)}"
    )
    return local_impact

feeds_index = []

for area, events in events_by_area.items():
    cal = Calendar()
    txt_path = os.path.join(OUTPUT_TXT_DIR, f"{area.replace(' ', '_')}_Events.txt")
    ics_path = os.path.join(OUTPUT_ICS_DIR, f"{area.replace(' ', '_')}_Events.ics")

    with open(txt_path, "w", encoding="utf-8") as txt_file:
        for e in events:
            try:
                start_dt = datetime.strptime(f"{e['date']} {e['start']}", "%Y-%m-%d %H:%M")
                end_dt = datetime.strptime(f"{e['date']} {e['end']}", "%Y-%m-%d %H:%M")
            except ValueError:
                print(f"Skipping event due to invalid date/time: {e}")
                continue

            if end_dt <= start_dt:
                print(f"⚠️ Skipping event with invalid timing: {e['artist']} on {e['date']}")
                continue

            event = Event()
            event.name = e["artist"]
            event.begin = start_dt
            event.end = end_dt
            event.url = e["url"]
            event.description = format_local_impact(e)
            cal.events.add(event)

            txt_file.write(f"{e['date']} | {e['artist']} | {e['venue']} | {e['start']}–{e['end']} | {e['status']}\n")

    if cal.events:
        with open(ics_path, "w", encoding="utf-8") as f:
            f.writelines(cal.serialize_iter())
        feeds_index.append(f"{area} | {BASE_URL}{area.replace(' ', '_')}_Events.ics")
    else:
        os.remove(txt_path)
        if os.path.exists(ics_path):
            os.remove(ics_path)

# Write feeds_index.txt
with open(INDEX_FILE, "w", encoding="utf-8") as index_file:
    for line in sorted(feeds_index):
        index_file.write(line + "\n")
