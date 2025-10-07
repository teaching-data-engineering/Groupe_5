import json
import pandas as pd

# ======================================================
# 1️⃣ Charger les événements depuis le JSON
# ======================================================
def json_to_dataframe(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    events_list = list(data.values())
    df = pd.DataFrame(events_list)
    
    if "startsAt" in df.columns:
        df["date"] = pd.to_datetime(df["startsAt"], errors="coerce").dt.date
    
    return df

df_events = json_to_dataframe("october_events.json")

# ======================================================
# 2️⃣ Ajouter le nombre d'événements le même jour
# ======================================================
df_events["events_same_day"] = df_events.groupby("date")["date"].transform("count")

# ======================================================
# 3️⃣ Sauvegarder dans un nouveau fichier CSV
# ======================================================
df_events.to_csv("october_events_with_counts.csv", index=False, encoding="utf-8")

# Vérification rapide
print(df_events[["artistName", "venueName", "date", "events_same_day"]].head())
