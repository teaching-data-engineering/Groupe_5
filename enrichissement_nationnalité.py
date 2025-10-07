import json
import pandas as pd
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time, random

# ==============================
# 1. Lecture sécurisée d’un JSON
# ==============================
def safe_load_json(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        with open(file, "r", encoding="latin-1") as f:
            return json.load(f)

# ==============================
# 2. Fusion de plusieurs fichiers JSON
# ==============================
def load_multiple_json(input_dir="data_json", prefix="october_evt_lv_"):
    files = sorted(Path(input_dir).glob(f"{prefix}*.json"))
    all_events = []

    for file in files:
        try:
            data = safe_load_json(file)
            events_list = list(data.values())
            all_events.extend(events_list)
        except Exception as e:
            print(f"⚠️ Erreur de lecture {file}: {e}")
            continue

    print(f"📂 {len(files)} fichiers chargés, {len(all_events)} événements au total")
    return pd.DataFrame(all_events)

# ==============================
# 3. Transformation du DataFrame
# ==============================
def transform_dataframe(df):
    if "startsAt" in df.columns:
        df["startsAt"] = pd.to_datetime(df["startsAt"], errors="coerce")
        df["date"] = df["startsAt"].dt.date
        df["hour"] = df["startsAt"].dt.time

    if "event_id" in df.columns:
        df = df.drop_duplicates(subset=["event_id"])
    else:
        df = df.drop_duplicates()

    # Extraire artist_id depuis artistUrl
    def extract_artist_id(url):
        if isinstance(url, str) and "/a/" in url:
            return url.split("/a/")[1].split("?")[0]
        return None

    if "artistUrl" in df.columns:
        df["artist_id"] = df["artistUrl"].apply(extract_artist_id)

    return df

# ==============================
# 4. Scraping du hometown
# ==============================
def get_hometown(artist_id):
    url = f"https://www.bandsintown.com/a/{artist_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/118.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        
        soup = BeautifulSoup(r.text, "html.parser")
        hometown_div = soup.find("div", string="Hometown:")
        if hometown_div:
            next_div = hometown_div.find_next("div")
            if next_div:
                return next_div.text.strip()
    except Exception as e:
        print(f"Erreur pour {artist_id}: {e}")
    return None

def enrich_with_hometowns(df):
    if "artist_id" not in df.columns:
        print("❌ Pas de colonne artist_id dans le DataFrame")
        return df

    artist_ids = df["artist_id"].dropna().unique()
    artist_hometowns = {}

    for artist_id in artist_ids:
        if artist_id not in artist_hometowns:
            hometown = get_hometown(artist_id)
            artist_hometowns[artist_id] = hometown
            print(f"{artist_id} -> {hometown}")
            time.sleep(random.uniform(1, 3))  # pause aléatoire

    df["hometown"] = df["artist_id"].map(artist_hometowns)

    # Sauvegarde dictionnaire pour réutilisation
    with open("artist_hometowns.json", "w", encoding="utf-8") as f:
        json.dump(artist_hometowns, f, ensure_ascii=False, indent=2)

    return df

# ==============================
# 5. Main
# ==============================
if __name__ == "__main__":
    df = load_multiple_json(input_dir="data_json", prefix="october_evt_lv_")
    df = transform_dataframe(df)

    print("🔎 Vérification des colonnes disponibles :", df.columns.tolist())
    print(df[["artistName", "artistUrl", "artist_id"]].head())

    df = enrich_with_hometowns(df)

    # Sauvegarde finale
    df.to_csv("events_with_hometown.csv", index=False, encoding="utf-8")
    print("✅ Fichier enrichi sauvegardé : events_with_hometown.csv")
