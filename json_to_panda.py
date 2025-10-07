import json
import pandas as pd
from pathlib import Path


def load_all_events(data_dir="data_json"):
    path = Path(data_dir)
    all_events = []
    
    for json_file in sorted(path.glob("*.json")):
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
            all_events.extend(data.values())
    
    return pd.DataFrame(all_events)


if __name__ == "__main__":
    df = load_all_events()
    print(f"Loaded {len(df)} events")
    print(df.iloc[0])

