import requests
import json
from datetime import datetime

# Constants
LATITUDE = 36.17497
LONGITUDE = -115.13722
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}
BASE_URL = "https://www.bandsintown.com/all-dates/fetch-next/upcomingEvents"


def scrap_one_page(page_idx, latitude, longitude):
    params = {
        "came_from": 257,
        "page": page_idx,
        "latitude": latitude,
        "longitude": longitude
    }

    response = requests.get(BASE_URL, params=params, headers=HEADERS)

    if response.status_code != 200:
        print(f"Error fetching page {page_idx}: {response.status_code}")
        return []

    data = response.json()
    return data.get("events", [])


def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def scrap_multiple_pages(latitude, longitude, start_month, end_month):
    seen_artists = set()
    events_dict = {}
    event_counter = 1
    page = 1

    while True:
        events = scrap_one_page(page, latitude, longitude)

        if not events:
            break

        current_artists = set(event.get("artistName") for event in events)
        if current_artists.issubset(seen_artists):
            break  # All events already seen

        for event in events:
            artist = event.get("artistName")
            date_str = event.get("startsAt")

            try:
                date_obj = datetime.fromisoformat(date_str)
            except Exception:
                continue

            if start_month <= date_obj.month <= end_month:
                events_dict[event_counter] = {
                    "artistName": event.get("artistName"),
                    "venueName": event.get("venueName"),
                    "streamingEvent": event.get("streamingEvent"),
                    "locationText": event.get("locationText"),
                    "watchLiveText": event.get("watchLiveText"),
                    "callToActionText": event.get("callToActionText"),
                    "rsvpCount": event.get("rsvpCount"),
                    "rsvpCountInt": event.get("rsvpCountInt"),
                    "startsAt": event.get("startsAt"),
                    "timezone": event.get("timezone"),
                    "displayRule": event.get("displayRule"),
                    "locale": event.get("locale")
                }
                event_counter += 1

            seen_artists.add(artist)

        page += 1

    return events_dict


def main():
    start_month = 10  # October
    end_month = 10    # Only October
    output_file = "data_json/october_events.json"

    events = scrap_multiple_pages(LATITUDE, LONGITUDE, start_month, end_month)
    save_json(events, output_file)

    print(f"{len(events)} events saved to '{output_file}'.")

main()