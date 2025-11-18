import json
import pandas as pd
from datetime import datetime


def json_to_dataframe(json_file):

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    events_list = list(data.values())

    df = pd.DataFrame(events_list)

    if "startsAt" in df.columns:
        df["date"] = pd.to_datetime(df["startsAt"]).dt.date
        df["hour"] = pd.to_datetime(df["startsAt"]).dt.time

    df['date'] = pd.to_datetime(df['date'])

    df["weekday"] = df["date"].dt.day_name()
    
    return df

df_events = json_to_dataframe("data_json/october_events.json")
print(df_events.head())