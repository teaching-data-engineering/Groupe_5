import json
import os
import pandas as pd
import requests
from datetime import datetime
import matplotlib.pyplot as plt

# ======================================================
# 1️⃣ Charger les événements depuis le fichier enrichi
# ======================================================
def json_to_dataframe(json_file):
    """Charge un fichier JSON (liste d'événements) en DataFrame pandas."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    
    # Extraire la date et l'heure à partir de la colonne startsAt
    if "startsAt" in df.columns:
        df["date"] = pd.to_datetime(df["startsAt"], errors="coerce").dt.date
        df["hour"] = pd.to_datetime(df["startsAt"], errors="coerce").dt.time
    
    return df


# Déterminer le chemin absolu du fichier JSON (même dossier que le script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "enrichissement_info_artiste.json")

df_events = json_to_dataframe(file_path)


# ======================================================
# 2️⃣ Récupérer les jours fériés US via Calendarific
# ======================================================
API_KEY = "tODcUQCbwj11dE8rmXOK0ih5kVaGf5jB"  # ← remplace par ta vraie clé
COUNTRY = "US"
YEAR = datetime.now().year

url = f"https://calendarific.com/api/v2/holidays?api_key={API_KEY}&country={COUNTRY}&year={YEAR}"
response = requests.get(url)

if response.status_code != 200:
    raise Exception(f"Erreur API Calendarific : {response.status_code}")

data = response.json()
holidays_iterable = data.get("response", {}).get("holidays", [])

holidays = []
for h in holidays_iterable:
    try:
        holidays.append({
            "date": h["date"]["iso"],
            "name": h["name"],
            "type": ", ".join(h.get("type", [])),
            "locations": h.get("locations", "")
        })
    except Exception as e:
        print("⚠️ Erreur dans un élément :", e, h)

df_holidays = pd.DataFrame(holidays)
if not df_holidays.empty:
    df_holidays["date"] = pd.to_datetime(df_holidays["date"], errors="coerce", utc=True).dt.date
    df_holidays = df_holidays.dropna(subset=["date"])
    df_holidays = df_holidays[
        df_holidays["locations"].str.contains("Nevada|All", case=False, na=False) &
        df_holidays["type"].str.contains("National holiday", case=False, na=False)
    ]
else:
    print("⚠️ Aucun jour férié trouvé.")


# ======================================================
# 3️⃣ Définir les vacances scolaires (Las Vegas, CCSD)
# ======================================================
school_holidays = [
    ("2024-12-23", "2025-01-03"),  # Vacances d'hiver
    ("2025-03-17", "2025-03-21"),  # Vacances de printemps
]
school_holidays = [(pd.to_datetime(start).date(), pd.to_datetime(end).date()) for start, end in school_holidays]


def is_in_school_holiday(date):
    """Renvoie True si la date est dans une période de vacances scolaires."""
    for start, end in school_holidays:
        if start <= date <= end:
            return True
    return False


# ======================================================
# 4️⃣ Ajouter les colonnes pour jours fériés et vacances scolaires
# ======================================================
df_events["date"] = pd.to_datetime(df_events["date"], errors="coerce").dt.date
df_events["is_holiday"] = df_events["date"].isin(df_holidays["date"]) if not df_holidays.empty else False
df_events["is_school_holiday"] = df_events["date"].apply(is_in_school_holiday)


# ======================================================
# 5️⃣ Ajouter la colonne "day_before_holiday"
# ======================================================
holiday_dates = set(df_holidays["date"])
df_events["day_before_holiday"] = df_events["date"].apply(lambda d: (d + pd.Timedelta(days=1)) in holiday_dates)


#Ajoute colonne "events_same_day"


# Compter le nombre d'événements par date
events_per_day = df_events["date"].value_counts()
# Ajouter cette information dans le DataFrame
df_events["events_same_day"] = df_events["date"].map(events_per_day)


output_file = os.path.join(BASE_DIR, "events_enrichis.json")
df_events.to_json(output_file, orient="records", indent=2, force_ascii=False)
print(f"✅ Fichier enrichi sauvegardé : {output_file}")
