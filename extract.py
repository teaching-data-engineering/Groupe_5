import requests
import random
from pprint import pprint
import os
import json
import time
import pandas as pd

def scrap_one_page(page_idx, date_debut, date_fin):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/78.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.109 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36",
    ]

    url = "https://www.bandsintown.com/choose-dates/fetch-next/upcomingEvents"
    headers = {"User-Agent": random.choice(user_agents)}
    params = {
        "city_id": 5506956,
        "date": f"{date_debut},{date_fin}",
        "page": page_idx,  
        "longitude": -115.13722,
        "latitude": 36.17497,
        "genre_query": "all-genres",
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status() 
        event = response.json()["events"]
        # data.append(response.json())
    except requests.exceptions.RequestException as e:
        print("Une erreur s'est produite:", e)
    return list(event)


def save_json(response, idx_page, date):
    folder_path = f"sauvegarde_json_{date.split('T')[0]}"
    if not os.path.exists(f"{folder_path}/response_data_{idx_page}.json"):
        os.makedirs(folder_path, exist_ok=True)
        with open(
            f"{folder_path}/response_data_{idx_page}.json", "w", encoding="utf-8"
        ) as json_file:
            json.dump(response, json_file)


def scrap_multiple_pages(start_date, end_date, max_page, nb_pages=1):
    fin = False
    l_pages = list()
    response1 = scrap_one_page(1, start_date, end_date)

    if response1:  
        save_json(
            response1, nb_pages, response1[-1]["startsAt"]
        ) 
        l_pages.extend(response1)  

    for i in range(2, max_page + 1):
        if len(response1) != 0:
            k=random.uniform(1,3)
            time.sleep(k)
            response2 = scrap_one_page(i, start_date, end_date)
            print(response1 == response2)
            if not response2:
                print(f"Arrêté à la page {nb_pages} car la page est vide.")
                fin = True
                break
            if (
                set(event["startsAt"] for event in response1)
                == set(event["startsAt"] for event in response2)
                and set(event["artistName"] for event in response1)
                == set(event["artistName"] for event in response2)
                and set(event["venueName"] for event in response1)
                == set(event["venueName"] for event in response2)
            ):
                print(f"Arrêté à la page {nb_pages} car les pages sont identiques.")
                break
            save_json(response2, nb_pages + 1, response2[-1]["startsAt"])
            l_pages.extend(response2)
            response1 = response2
            nb_pages += 1
    return l_pages, fin, nb_pages


def extraction(start_date, end_date, max_page):
    l_pages, fin, nb_pages = scrap_multiple_pages(start_date, end_date, max_page)
    while fin == False:
        start_date = l_pages[-1]["startsAt"]
        l_int, fin, nb_pages = scrap_multiple_pages(
                start_date,
                end_date,
                (max_page - nb_pages),
                nb_pages=nb_pages + 1,
            )
        l_pages.extend(l_int)
    return l_pages


def json_to_df(lst_dico):
    df= pd.DataFrame(lst_dico)
    df.columns=['img_artiste','url_img_taille_adaptee','url_redir','url_img_secours','artiste','lieu','even_streaming','titre','loc','icone_epingle','url_even','url_artiste','txt_watch_live','est_plus','txt_redir','RSVP','RSVP_int','horaire_debut','horaire_fin','fuseau','regle_affichage','locale']
    return df

lst_dico = extraction("2024-10-07T00:00:00", "2024-10-31T00:00:00", 50)
df = json_to_df(lst_dico)
df.to_csv('df_event.csv',index='False')

