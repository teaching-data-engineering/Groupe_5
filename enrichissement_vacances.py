import requests
from datetime import datetime

url = "https://api.api-ninjas.com/v1/holidays"
headers = {"X-Api-Key": "YaLMZ3CgIRrgKQ12yOJhPA==sZfHzdHBf7gX9Irc"}
params = {"country": "US", "state": "NV"}  # Pas de year

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    # Filtrer uniquement les vacances scolaires et celles de 2025
    school_holidays = [h for h in data if h['type'] == 'school' and h['date'].startswith("2025")]
    school_holidays_sorted = sorted(school_holidays, key=lambda x: x['date'])
    
    print("Vacances scolaires à Las Vegas (Nevada) en 2025 :\n")
    for holiday in school_holidays_sorted:
        print(f"{holiday['date']} - {holiday['name']}")
else:
    print(f"Erreur {response.status_code} : {response.text}")
