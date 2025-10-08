import json


fichiers_json = [f"data_info/events_enriched{i}.json" for i in range(1, 24)]

# Initialise la liste combinée
evenements_combines = []

# Parcourt chaque fichier dans l'ordre et ajoute son contenu
for fichier in fichiers_json:
    with open(fichier, 'r', encoding='utf-8') as f:
        donnees = json.load(f)
        evenements_combines.extend(donnees)

# Sauvegarde dans un nouveau fichier
with open('enrichissement_info_artiste.json', 'w', encoding='utf-8') as f_out:
    json.dump(evenements_combines, f_out, indent=2, ensure_ascii=False)




