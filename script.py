import requests
from pprint import pprint

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
}
for i in range(50):
    params1 = {
        "city_id": 5506956,
        "date": "2024-10-07T00:00:00,2024-10-31T23:00:00",
        "page": i,  # Vous pouvez modifier cette valeur pour naviguer à travers les pages
        "longitude": -115.13722,
        "latitude": 36.17497,
        "genre_query": "all-genres",
    }

    url = "https://www.bandsintown.com/choose-dates/fetch-next/upcomingEvents"

    response1 = requests.get(url, params=params1, headers=headers)

    url = "https://www.bandsintown.com/choose-dates/fetch-next/upcomingEvents"

    # print(response1.json()["events"] == response2.json()["events"])
    # Nous avons bien des pages différentes pour chacune d'entre elles.
    # Nous n'avons pas besoin d'établir de stratégie pour changer de jours en fonction du nombre de pages.
