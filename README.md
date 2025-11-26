# Projet de groupe d’étudiants en Master 2 MAS, réalisé en octobre/novembre 2025. 

<p align="center">
  <img src="./images/vegas.png" alt="Las Vegas" width="300">
</p>

**Travail effectué par Juliette Brault, Florent Cheyron, Mathis Cotonnec, Damien Peres, Solo Peyret**

Étape à suivre pour obtenir notre travail :  

  1. **Exécuter le script de scraping (APIscraping.py)**  
    Celui-ci récupère les informations nécessaires et génère la base de données initiale.

  2. Après avoir réalisé le scraping, nous créons notre DataFrame à partir de **json_to_pandas.py**

  3. **Lancer tous les scripts d'enrichissement (enrichissement_ferie_vacances.py, enrichissement_infos.py, enrichissement_type_salle_&_jour_semaine.py)**  
     Ils permettent d'ajouter des données complémentaires, notamment :
       - Hometown, followers, genres
       - Jours fériés, vacances, jours avant les vacances
       - Les nombre d'évènements le même jour  
     En plus de cela, nous avons développé un modèle de prévision de type K-plus-proche-voisins, qui calcule un score       de risque à partir de différentes métriques, telles que le nombres de followers,   l'emplacement ou encore le style      musical. Le score obtenu varie entre 0 et 1, puis il est transformé en catégories de risque (faible, modéré,           élevé, très élevé) en fonction de sa valeur.

  4. **Exécuter create_df_security.py**    
     Ce script calcule le score de risque, l'ajoute au DataFrame et prépare les données pour les étapes suivantes.

  5. **Lancer upload_to_bigquery.py**    
     Il importe le DataFrame dans BigQuery afin de pouvoir travailler dessus ensuite.

  6. **Excéuter API_security.py**    
     Ce fichier contient toutes les dernières modifications ainsi que la création de l'API (avec sécurisation).Comme        l’API est sécurisée, nous fournissons le fichier api_key.json, sans lequel les tests de l’API ne seraient pas          possibles. En temps normal, ce fichier devrait être ajouté au .gitignore et ne jamais être partagé.
     Ce fichier crée aussi plusieurs endpoints, qui donnent des fonctionnalités à notre API :
     - GET/ : Endpoint racine : renvoie un message d'accueil
     - GET/events : Retourne tous les évènements, triés par date. Paramètres : page, page_size
     - GET/events/by-day-of-week : Retourne le nombre d’évènements par jour de la semaine, avec option pour filtrer par numéro de semaine. Paramètre : week
     - GET/events/search : Recherche avancée avec filtres combinables. Paramètres : artistName, venueName, date_start, date_end
     - GET/events/hour : Analyse des évènements par heure. Paramètre : hour
     - GET/events/popular-days : Retourne les jours ayant le plus d’évènements, avec possibilité de filtrer par seuil minimum. Paramètre : min_events
     - GET/events/place-stats : Statistiques sur les lieux. Paramètre : venueName
     - GET/events/genres-trends : Analyse des tendances par genre musical. Paramètre : min_events
     - GET/events/competition-impact : Analyse l’impact de la concurrence en divisant les évènements en quantiles selon le nombre d’évènements le même jour. Paramètre : groups
    

Présentation sur Canva : https://www.canva.com/design/DAG5IVkkUWs/HoRNEHwTVdfqDgfZR8v3xA/edit?utm_content=DAG5IVkkUWs&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton
