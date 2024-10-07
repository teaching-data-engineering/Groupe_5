import requests
import random
from pprint import pprint
import os

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
    "date": f"{date_debut},{date_fin}",
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

def save_json(response, idx_page, date):
    folder_path = f"sauvegarde_json_{date}"
    os.makedirs(folder_path, exist_ok=True)
    with open('{folder_path}/response_data_{idx_page}.json', 'w', encoding='utf-8') as json_file:
            json.dump(response, json_file)

def scrap_multiple_pages(start_date, end_date, max_page):
    l_pages = list()
    response1 = scrap_one_page(1, start_date, end_date)
    for i in range(2, max_page):
        response2 = scrap_one_page(i, start_date, end_date)
        if (
            response1.json()["events"] == response2.json()["events"]
            and len(response1.json()["events"]) > 0
        ):
            break
            # date = response2[-1]["StartsAt"]
            # start_date = date
        save_json(response1, i, response1[-1]["StartsAt"])
        l_pages.extend(response1)
        response1 = response2
    return l_pages
