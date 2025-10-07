import pandas as pd
import json
import requests
import time

# Charger les events depuis ton fichier JSON
with open("data_json/october_events.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Transformer en liste de dicts
events_list = list(data.values())
df = pd.DataFrame(events_list)

# Extraire les stades uniques
stades_uniques = df['venueName'].unique()
print(f"Nombre de stades différents : {len(stades_uniques)}")

def get_capacity_osm(venue):
    """
    Cherche la capacité d'un lieu via OpenStreetMap / Nominatim.
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": venue,
        "format": "json",
        "limit": 1,
        "extratags": 1
    }

    try:
        response = requests.get(base_url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            results = response.json()
            if results and results[0] is not None:
                extratags = results[0].get("extratags", {})
                capacity = extratags.get("capacity")
                print(f"{venue} → capacity: {capacity}")  # affichage debug
                return capacity
            else:
                print(f"{venue} → Lieu non trouvé")
        else:
            print(f"{venue} → Erreur HTTP {response.status_code}")
    except Exception as e:
        print(f"{venue} → Erreur : {e}")
    return None

# Boucle sur tous les stades pour récupérer la capacité
capacities = []

for venue in stades_uniques:
    cap = get_capacity_osm(venue)
    capacities.append({"venueName": venue, "capacity": cap})
    time.sleep(1)  # respecter la limite de Nominatim

# Créer un DataFrame final
df_capacities = pd.DataFrame(capacities)

# Sauvegarder éventuellement
df_capacities.to_csv("venue_capacities.csv", index=False, encoding="utf-8")
print("Capacités sauvegardées dans venue_capacities.csv")
