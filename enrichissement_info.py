from json_to_pandas import load_all_events
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from tqdm import tqdm
import re

df = load_all_events()
df = df.head()

headers = {
    "User-Agent": "Mozilla/5.0" 
}

def extract_hometown(soup):
    for div in soup.find_all("div"):
        if div.text.strip() == "Hometown:":
            next_div = div.find_next_sibling("div")
            if next_div:
                return next_div.text.strip()
    return None

def extract_genres(soup):
    for div in soup.find_all("div"):
        if div.text.strip() == "Genres:":
            next_div = div.find_next_sibling("div")
            if next_div:
                return next_div.text.strip()
    return None



def get_artist_info(artist_url):
    response = requests.get(artist_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    # Hometown
    hometown = extract_hometown(soup)

    # Followers
    followers = None
    for div in soup.find_all("div"):
        text = div.text.strip()
        if text.lower().endswith("followers"):
            num = re.sub(r"[^\d]", "", text)  # garde que les chiffres
            followers = int(num) if num else None
            break

    # Genres 
    genres = extract_genres(soup)

    return {
        "hometown": hometown,
        "followers": followers,
        "genres": genres
    }

result = []
for url in tqdm(df['artistUrl']):
    info = get_artist_info(url)
    result.append(info)
    time.sleep(random.uniform(1, 1))

info_df = pd.DataFrame(result)

df_new = pd.concat([df.reset_index(drop = True), info_df], axis = 1)

json_output = df_new.to_json(orient="records", indent=4)
print(json_output.replace("\\/", "/"))

# Optionnel : sauvegarde dans un fichier
with open("events_enriched.json", "w", encoding="utf-8") as f:
    f.write(json_output.replace("\\/", "/"))