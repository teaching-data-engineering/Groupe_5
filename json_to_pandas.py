import json
import pandas as pd
from pathlib import Path

def load_all_events(data_dir="data_json"):
    path = Path(data_dir)
    all_events = []

    for json_file in sorted(path.glob("*.json")):
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
        except UnicodeDecodeError:
            # Try fallback encodings
            try:
                with open(json_file, encoding="utf-8-sig") as f:
                    data = json.load(f)
            except UnicodeDecodeError:
                with open(json_file, encoding="latin-1") as f:
                    data = json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Erreur JSON dans {json_file.name} — fichier ignoré.")
            continue
        
        all_events.extend(data.values())

    return pd.DataFrame(all_events)

""" To import df in an other file : 
from json_to_pandas import load_all_events df = load_all_events() 
"""