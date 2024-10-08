import pandas as pd
import requests

df = pd.read_csv("df_event.csv")
print(df.columns)
df["horaire_debut"] = pd.to_datetime(df["horaire_debut"])
df["weekend_vdd_soir"] = (
    (df["horaire_debut"].dt.dayofweek == 4) & (df["horaire_debut"].dt.hour >= 19)
    | (df["horaire_debut"].dt.dayofweek.isin([5, 6]))
).astype(int)
