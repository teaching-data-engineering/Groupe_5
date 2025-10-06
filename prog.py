import requests

url = "https://www.bandsintown.com/all-dates/fetch-next/upcomingEvents?city_id=5506956&page=2&longitude=-115.13722&latitude=36.17497"

response = requests.get(url)
print(response.text)

