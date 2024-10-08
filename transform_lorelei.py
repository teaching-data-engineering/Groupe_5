import requests
import random
from pprint import pprint
import os
import json
import time
import pandas as pd


df = pd.read_csv('df_event.csv')

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
                return "Aire non trouvée"
        else:
            return "Artiste non trouvé"
    else:
        return f"Erreur {response.status_code}"


resultats = []

for artiste in artistes:
    area = get_artist_area(artiste)
    resultats.append({'artiste': artiste, 'area': area})
    
    time.sleep(1)  
pprint(resultats)
'''
# Créer un nouveau dataframe à partir des résultats
df_result = pd.DataFrame(resultats)

# Afficher le nouveau dataframe
print(df_result)

# Optionnel : Sauvegarder dans un fichier CSV
df_result.to_csv('artistes_areas.csv', index=False)
'''