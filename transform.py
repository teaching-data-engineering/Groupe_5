from geopy.geocoders import Nominatim
import random
import requests
import random
from pprint import pprint
import os
import json
import time
import pandas as pd

df = pd.read_csv('df_event.csv')

##### ajout des coord

def adress_to_coords(adresse, geolocator):
    try:
        location = geolocator.geocode(adresse)
        if location:
            return location.latitude, location.longitude
        else:
            print(f"Aucune localisation trouvée pour l'adresse: {adresse}")  # Message pour adresse non trouvée
            return None, None
    except Exception as e:
        print(f"Erreur lors de la géocodification de l'adresse '{adresse}': {e}. Ignorer cette adresse.")
        return None, None

for adresse in df.lieu:
    geolocator = Nominatim(user_agent=f"mon_geocode{random.randint(200000, 300000)}") #changer la grille à chaque lancement
    latitude, longitude = adress_to_coords(adresse,geolocator)
    df.loc[df['lieu'] == adresse, ['latitude', 'longitude']] = [latitude, longitude]

##### ajout du weekend

df["horaire_debut"] = pd.to_datetime(df["horaire_debut"])
df["weekend_vdd_soir"] = (
    (df["horaire_debut"].dt.dayofweek == 4) & (df["horaire_debut"].dt.hour >= 19)
    | (df["horaire_debut"].dt.dayofweek.isin([5, 6]))
).astype(int)

#### ajout de la nationalité

artistes = df['artiste'].unique()  

def get_artist_area(artist_name):
    url = f'https://musicbrainz.org/ws/2/artist?query=artist:{artist_name}&fmt=json'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'artists' in data and len(data['artists']) > 0:
            first_artist = data['artists'][0]
            if 'area' in first_artist:
                print(first_artist)
                return first_artist['area']['name'] 
            else:
                return None
        else:
            return None
    else:
        return f"Erreur {response.status_code}"

def get_provenance(artiste):
    area = get_artist_area(artiste)
    time.sleep(1)  
    return area

df['artiste_provenance'] = df['artiste'].apply(get_provenance)

df.to_csv('df_event.csv',type='w',index='False')