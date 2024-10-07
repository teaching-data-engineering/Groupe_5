import requests
from pprint import pprint
import time 


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
url = "https://www.bandsintown.com/choose-dates/fetch-next/upcomingEvents"

fin = []
for i in range(25):
    params = {
        "city_id": 3117735,
        "date": "2024-10-01T00:00:00,2024-10-31T23:00:00",
        "page": i,  # Vous pouvez modifier cette valeur pour naviguer à travers les pages
        "longitude": -3.70256,
        "latitude": 40.4165,
        "genre_query": "all-genres"
    }
    time.sleep(1)
    response = requests.get(url, params=params, headers=headers).json()
    data = response['events']
    if len(data)>0 :
        fin.extend(data)
    else:
        print("plus d'info",i)
        break
pprint(fin)

def save_json(response,idx_page,date):
    folder_path = f"sauvegarde_json_{date}"
    os.makedirs(folder_path, exist_ok=True)
    with open('{folder_path}/response_data_{idx_page}.json', 'w', encoding='utf-8') as json_file:
            json.dump(response, json_file)
        