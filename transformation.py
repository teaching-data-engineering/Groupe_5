import json
import pandas as pd

def json_to_dataframe(json_file):
    # Charger le JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Chaque valeur du dictionnaire correspond à un événement
    events_list = list(data.values())
    
    # Créer le DataFrame
    df = pd.DataFrame(events_list)
    
    # Séparer la date et l'heure si nécessaire
    if "startsAt" in df.columns:
        df["date"] = pd.to_datetime(df["startsAt"]).dt.date
        df["hour"] = pd.to_datetime(df["startsAt"]).dt.time
    
    return df

df_events = json_to_dataframe("october_events.json")
print(df_events.head())
