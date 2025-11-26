import pandas as pd
import json
import requests
import time
from datetime import datetime

# Charger les events
with open("data/events_enrichis.json", encoding="utf-8") as f:
    data = json.load(f)

# Transformer en DataFrame
df = pd.DataFrame(data)

# Extraire les stades uniques
stades_uniques = df['venueName'].unique()
print(f"Nombre de stades différents : {len(stades_uniques)}")


if "startsAt" in df.columns:
        df["date"] = pd.to_datetime(df["startsAt"]).dt.date
        df["hour"] = pd.to_datetime(df["startsAt"]).dt.time

df['date'] = pd.to_datetime(df['date'])

df["weekday"] = df["date"].dt.day_name()

def detect_venue_type(venue_name: str) -> str:
    if not isinstance(venue_name, str):
        return "Other / Unknown"
    name = venue_name.lower()

    if any(word in name for word in ["stadium", "arena", "stade", "arène", "palais des sports"]):
        return "Stadium / Arena"
    elif any(word in name for word in ["theatre", "theater", "opera", "auditorium"]):
        return "Theater / Auditorium"
    elif any(word in name for word in ["Comedy","comedy"]):
        return "Comedy"
    elif any(word in name for word in ["casino"]):
        return "Casino"
    elif any(word in name for word in ["bar", "pub", "restaurant", "cafe", "brasserie", "grill"]):
        return "Bar / Restaurant"
    elif any(word in name for word in ["club", "discotheque", "nightclub", "lounge"]):
        return "Club / Nightclub"
    elif any(word in name for word in ["zenith", "hall", "center", "centre", "espace", "salle"]):
        return "Concert Hall"
    else:
        return "Other / Unknown"

# Ajouter la colonne venueType
df["venueType"] = df["venueName"].apply(detect_venue_type)
#print(df[["venueName", "venueType"]].head(15))

# Sauvegarder le DataFrame enrichi en JSON
output_path = "data/events_enrichis.json"
df.to_json(output_path, orient="records", indent=2, force_ascii=False)

print(f"✅ Fichier mis à jour : {output_path}")