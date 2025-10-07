import json
import pandas as pd
import requests
from datetime import datetime
import matplotlib.pyplot as plt

# ======================================================
# 1️⃣ Charger les événements Bandsintown
# ======================================================
def json_to_dataframe(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    events_list = list(data.values())
    df = pd.DataFrame(events_list)
    
    if "startsAt" in df.columns:
        df["date"] = pd.to_datetime(df["startsAt"], errors="coerce").dt.date
        df["hour"] = pd.to_datetime(df["startsAt"], errors="coerce").dt.time
    
    return df

df_events = json_to_dataframe("october_events.json")

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
# 5️⃣ Graphique combiné
# ======================================================
# Compter le nombre d'événements par date
df_count = df_events.groupby("date").size().reset_index(name="num_events")

# Définir une couleur selon le type de jour
def get_color(row):
    if row["date"] in df_holidays["date"].values:
        return "red"           # jour férié
    elif is_in_school_holiday(row["date"]):
        return "orange"        # vacances scolaires
    else:
        return "blue"          # jour normal

df_count["color"] = df_count.apply(get_color, axis=1)

plt.figure(figsize=(12,6))
plt.bar(df_count["date"], df_count["num_events"], color=df_count["color"])
plt.xlabel("Date")
plt.ylabel("Nombre d'événements")
plt.title("Événements par date (rouge = jour férié, orange = vacances scolaires)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ======================================================
# 6️⃣ Ajouter la colonne 'day_before_holiday' si besoin
# ======================================================
holiday_dates = set(df_holidays["date"])
df_events["day_before_holiday"] = df_events["date"].apply(lambda d: (d + pd.Timedelta(days=1)) in holiday_dates)

# ======================================================
# 7️⃣ Vérification finale
# ======================================================
print(df_events[["artistName", "venueName", "date", "is_holiday", "is_school_holiday", "day_before_holiday"]])
