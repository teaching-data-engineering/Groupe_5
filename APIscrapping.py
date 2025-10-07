import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
import requests

# Configuration
CITY_ID = 5506956
LAT, LON = 36.17497, -115.13722
BASE_URL = "https://www.bandsintown.com/choose-dates/fetch-next/upcomingEvents"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

FIELDS = [
    "artistName", "venueName", "streamingEvent", "locationText",
    "watchLiveText", "callToActionText", "rsvpCount", "rsvpCountInt",
    "startsAt", "timezone", "displayRule", "locale"
]


def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }


def create_event_id(artist, date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        safe = artist.replace(" ", "_").replace("/", "_")
        return f"{safe}_{dt:%Y%m%d_%H%M}"
    except:
        return f"{artist.replace(' ', '_')}_{date_str}"


def fetch_page(page, date):
    params = {
        "city_id": CITY_ID,
        "date": f"{date}T00:00:00,{date}T23:00:00",
        "page": page,
        "longitude": LON,
        "latitude": LAT,
        "genre_query": "all-genres"
    }
    
    try:
        r = requests.get(BASE_URL, params=params, headers=get_headers(), timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("events", []), data.get("totalCount", 0)
    except Exception as e:
        print(f"Error page {page}: {e}")
        return [], 0


def extract_event_data(event):
    artist = event.get("artistName", "Unknown")
    event_id = create_event_id(artist, event.get("startsAt", ""))
    
    data = {"event_id": event_id}
    data.update({k: event.get(k) for k in FIELDS})
    
    # Ajout des URLs
    data["eventUrl"] = event.get("eventUrl") or event.get("url")
    data["artistUrl"] = event.get("artistUrl") or f"https://www.bandsintown.com/a/{artist.lower().replace(' ', '-')}"
    
    return event_id, data


def scrap_day(date, max_page=50):
    print(f"\nScraping {date}...")
    seen, results = set(), {}
    failures = 0

    for page in range(1, max_page + 1):
        events, total = fetch_page(page, date)
        
        if not events:
            failures += 1
            if failures >= 3:
                print("Too many failures, skipping day")
                break
            time.sleep(random.uniform(2, 4))
            continue

        failures = 0
        for e in events:
            eid, data = extract_event_data(e)
            if eid not in seen:
                seen.add(eid)
                results[eid] = data

        print(f"Page {page}: {len(results)} total ({total} available)")

        if total and len(seen) >= total:
            break

        time.sleep(random.uniform(1, 3))

    return results


def save_json(data, date_key, output_dir="data_json"):
    path = Path(output_dir)
    path.mkdir(exist_ok=True)
    file = path / f"october_evt_lv_{date_key}.json"
    file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"Saved {len(data)} events → {file}")


def scrap_range(start, end, max_page=50):
    start_dt, end_dt = datetime.fromisoformat(start), datetime.fromisoformat(end)
    current, total = start_dt, 0

    while current <= end_dt:
        date_str = current.strftime("%Y-%m-%d")
        events = scrap_day(date_str, max_page)
        
        if events:
            save_json(events, current.strftime("%Y%m%d"))
            total += len(events)
        
        current += timedelta(days=1)
        time.sleep(random.uniform(2, 4))

    print(f"\n{'='*50}\nTotal: {total} events\n{'='*50}")


if __name__ == "__main__":
    print("Starting scrape for Las Vegas (America/Los_Angeles)")
    scrap_range("2025-10-01", "2025-10-31", 50)