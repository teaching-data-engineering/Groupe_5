import json
import pandas as pd
from pathlib import Path

# ==============================
# 1. Lecture sécurisée d’un JSON
# ==============================
def safe_load_json(file):
    """
    Charge un fichier JSON en essayant UTF-8 puis latin-1.
    Remplace les caractères invalides si besoin.
    """
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

    # Suppression des doublons
    if "event_id" in df.columns:
        df = df.drop_duplicates(subset=["event_id"])
    else:
        df = df.drop_duplica_
