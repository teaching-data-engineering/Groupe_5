import json
import pandas as pd
import requests
import base64
import time

# ==============================
# 1. Charger le JSON en DataFrame
# ==============================
def json_to_dataframe(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    events_list = list(data.values())
    df = pd.DataFrame(events_list)
    return df

# ==============================
# 2. Authentification Spotify
# ==============================
CLIENT_ID = "5a1a2622eb4946dd9a47317e7485ab48"          # <-- Mets ton Client ID Spotify
CLIENT_SECRET = "abda33b3373642e6a082f60469e38572"  # <-- Mets ton Client Secret Spotify

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {"Authorization": f"Basic {b64_auth_str}"}
    data = {"grant_type": "client_credentials"}

    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code == 200:
        return resp.json()["access_token"]
    else:
        raise Exception("⚠️ Erreur Spotify Auth:", resp.text)

# ==============================
# 3. Recherche d’artiste
# ==============================
def search_artist(artist_name, token):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": artist_name, "type": "artist", "limit": 1}

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        results = resp.json()["artists"]["items"]
        if results:
            return results[0]
    return None

# ==============================
# 4. Enrichissement du DataFrame
# ==============================
def enrich_with_spotify(df, token, limit=5):
    df = df.head(limit).copy()  # garder seulement les 5 premiers événements
    df["spotify_popularity"] = None
    df["spotify_followers"] = None
    df["spotify_genres"] = None
    df["spotify_url"] = None

    for i, row in df.iterrows():
        artist = row["artistName"]
        if not artist:
            continue

        artist_data = search_artist(artist, token)

        if artist_data:
            df.at[i, "spotify_popularity"] = artist_data["popularity"]
            df.at[i, "spotify_followers"] = artist_data["followers"]["total"]
            df.at[i, "spotify_genres"] = ", ".join(artist_data["genres"])
            df.at[i, "spotify_url"] = artist_data["external_urls"]["spotify"]
            print(f"✅ {artist} enrichi avec Spotify")
        else:
            print(f"❌ Pas trouvé sur Spotify : {artist}")

        time.sleep(0.2)  # éviter de spammer l’API

    return df

# ==============================
# 5. Exécution du script
# ==============================
if __name__ == "__main__":
    input_file = "data_json/october_events.json"
    output_file = "data_json/october_events_spotify.json"

    df_events = json_to_dataframe(input_file)
    token = get_spotify_token()
    df_events = enrich_with_spotify(df_events, token, limit=5)

    # Sauvegarde en JSON
    df_events.to_json(output_file, orient="records", force_ascii=False, indent=2)
    print(f"\n🎉 Enrichissement terminé. Résultat sauvegardé dans {output_file}")
