from json_to_pandas import load_all_events
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm
import re
import json

df = load_all_events()
df = df.head()

headers = {
    "User-Agent": "Mozilla/5.0" 
}


def extract_label(soup, label):
    for div in soup.find_all("div"):
        if div.text.strip() == label:
            next_div = div.find_next_sibling("div")
            if next_div:
                return next_div.text.strip()


def extract_followers(soup):
    for div in soup.find_all("div"):
        text = div.text.strip()
        if text.lower().endswith("followers"):
            num = re.sub(r"[^\d]", "", text) 
            if num:
                return int(num)



def get_artist_info(artist_url):
    response = requests.get(artist_url, headers= headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    return {
        "hometown": extract_label(soup, "Hometown:"),
        "genres": extract_label(soup, "Genres:"),
        "followers": extract_followers(soup)  
    }



result = []
for url in tqdm(df['artistUrl']):
    info = get_artist_info(url)
    result.append(info)
    time.sleep(1)

info_df = pd.DataFrame(result)
df_new = pd.concat([df.reset_index(drop = True), info_df], axis = 1)

json_output = df_new.to_json(orient="records", indent=4).replace("\\/", "/")
with open("data_info/events_test.json", "w", encoding="utf-8") as f:
    f.write(json_output)
