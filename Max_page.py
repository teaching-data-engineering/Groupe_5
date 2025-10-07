import requests

url = "https://www.bandsintown.com/all-dates/fetch-next/upcomingEvents?came_from=257&longitude=-115.13722&latitude=36.17497&page=1"
response = requests.get(url)
print(response.status_code)
print(response.text[:500])  # Affiche les 500 premiers caractères
