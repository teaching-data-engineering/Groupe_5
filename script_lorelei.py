import requests
from pprint import pprint
import time 
import pandas as pd

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
        
def json_to_df(lst_dico):
    df= pd.DataFrame(lst_dico)
    df= df.rename({"artistImageSrc": 'img_artiste',
    'properlySizedImageURL': 'url_img_taille_adaptee',
    'callToActionRedirectUrl': 'url_redir',
    'fallbackImageUrl' : 'url_img_secours',
    "artistName" : "artiste" ,
    "venueName" : "lieu",
    "streamingEvent" : "even_streaming",
    "title" : 'titre',
    "locationText" : 'loc',
    "pinIconSrc" : 'icone_epingle',
    "eventUrl" : 'url_even',
    "artistUrl" : 'url_artiste',
    "watchLiveText" : 'txt_watch_live',
    "isPlus" : 'est_plus',
    "callToActionText" : 'txt_redir',
    'rsvpCount' : 'RSVP',
    "rsvpCountInt" : 'RSVP_int',
    "startsAt" : 'horaire',
    "timezone" : 'fuseau',
    "displayRule" : 'regle_affichage' })
    return df