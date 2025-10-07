import pandas as pd
import json
import requests
import time

# Charger les events
from json_to_pandas import load_all_events 
df = load_all_events() 

# Extraire les stades uniques
stades_uniques = df['venueName'].unique()
print(f"Nombre de stades différents : {len(stades_uniques)}")

def detect_venue_type(venue_name: str) -> str:
    name = venue_name.lower()

    if any(word in name for word in ["stadium", "arena", "stade", "arène", "palais des sports"]):
        return "Stadium / Arena"
    elif any(word in name for word in ["theatre", "theater", "opera", "auditorium"]):
        return "Theater / Auditorium"
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
    
    
df["venueType"] = df["venueName"].apply(detect_venue_type)
print(df[["venueName", "venueType"]].head(15))

print(df.head())