import requests
import random
from pprint import pprint

# # Liste de User-Agents de différents navigateurs
# user_agents = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/78.0',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
#     'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.109 Mobile Safari/537.36',
#     'Mozilla/5.0 (Linux; Android 11; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
# ]

# data = []
# for i in range(1, 15):
#     # url = f"https://www.bandsintown.com/choose-dates/fetch-next/upcomingEvents?city_id=3117735&date=2024-10-01T00%3A00%3A00%2C2024-10-31T23%3A00%3A00&page={i}&longitude=-3.70256&latitude=40.4165&genre_query=all-genres"
#     url = "https://www.bandsintown.com/choose-dates/fetch-next/upcomingEvents"
#     headers = {'User-Agent': random.choice(user_agents)}
#     params = {
#     "city_id": 3117735,
#     "date": "2024-10-01T00:00:00,2024-10-31T23:00:00",
#     "page": i,  # Vous pouvez modifier cette valeur pour naviguer à travers les pages
#     "longitude": -3.70256,
#     "latitude": 40.4165,
#     "genre_query": "all-genres"}
    
#     try:
#         response = requests.get(url, params=params, headers=headers).json()
#         # response.raise_for_status()  # Vérifie les erreurs HTTP
#         event = response['events']
#         if len(event)>0 :
#             data.extend(event)
#         else:
#             print("plus d'info",i)
#         break
#         # data.append(response.json())
#     except requests.exceptions.RequestException as e:
#         print("Une erreur s'est produite:", e)

# pprint(data)
# print(data[11])

def scrap_one_page(page_idx, date_debut, date_fin):
    user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
    'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.109 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36']

    url = "https://www.bandsintown.com/choose-dates/fetch-next/upcomingEvents"
    headers = {'User-Agent': random.choice(user_agents)}
    params = {
    "city_id": 3117735,
    "date": f"{date_debut}T00:00:00,{date_fin}T23:59:59",
    "page": page_idx,  # Vous pouvez modifier cette valeur pour naviguer à travers les pages
    "longitude": -3.70256,
    "latitude": 40.4165,
    "genre_query": "all-genres"}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        event = response.json()['events']
        # data.append(response.json())
    except requests.exceptions.RequestException as e:
        print("Une erreur s'est produite:", e)
    return list(event)

pprint(scrap_one_page(1, "2024-10-01", "2024-10-31"))