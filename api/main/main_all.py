from typing import Union, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
from google.cloud import bigquery
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("sa-key-group-5.json")
client = bigquery.Client(credentials=credentials, project=credentials.project_id)
app = FastAPI()

BASE_URL = "http://127.0.0.1:8000"

class Objet(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

def exec_query(sql: str):
    query_job = client.query(sql)
    return [dict(row) for row in query_job.result()]

def exec_query_paginated(sql: str, page: int, page_size: int, base_url: str):
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    
    count_sql = f"SELECT COUNT(*) as total FROM ({sql})"
    total = exec_query(count_sql)[0]["total"]
    
    offset = (page - 1) * page_size
    total_pages = (total + page_size - 1) // page_size
    
    results = exec_query(f"{sql} LIMIT {page_size} OFFSET {offset}")
    
    next_url = None
    if page < total_pages:
        parsed = urlparse(base_url)
        params = parse_qs(parsed.query)
        params['page'] = [str(page + 1)]
        params['page_size'] = [str(page_size)]
        new_query = urlencode(params, doseq=True)
        next_url = urlunparse((parsed.scheme or 'http', parsed.netloc or '127.0.0.1:8000', 
                               parsed.path, '', new_query, ''))
    
    return {
        "metadata": {
            "page": page,
            "total_pages": total_pages,
            "results_per_page": page_size,
            "total_results": total,
            "next_page_url": next_url
        },
        "results": results
    }

def build_url_with_params(endpoint: str, params: dict) -> str:
    from urllib.parse import urlencode
    query_params = urlencode({k: v for k, v in params.items() if v is not None})
    return f"{BASE_URL}{endpoint}" + (f"?{query_params}" if query_params else "")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/mon_endpoint/{objet_id}")
async def read_objet(objet_id: int, q: Union[str, None] = None):
    return {"objet_id": objet_id, "q": q}

@app.put("/mon_endpoint/{objet_id}")
def update_objet(objet_id: int, objet: Objet):
    return {"objet_name": objet.name, "objet_id": objet_id}

@app.get("/events")
#donne tous les évènements
def get_events(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    sql = "SELECT * FROM `dataset_groupe_5.events` ORDER BY date DESC"
    return exec_query_paginated(sql, page, page_size, f"{BASE_URL}/events")

@app.get("/events/by-day-of-week")
#donne le nombre d'évènements par jour de la semaine, avec filtre optionnel par numéro de semaine
def get_events_by_day_of_week(
    week: Optional[int] = Query(None, description="Numéro de semaine (1-53)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    sql = """
        SELECT 
            EXTRACT(DAYOFWEEK FROM TIMESTAMP_MILLIS(date)) AS day_number,
            FORMAT_TIMESTAMP('%A', TIMESTAMP_MILLIS(date)) AS day_name,
            COUNT(*) AS event_count
        FROM `dataset_groupe_5.events`
        WHERE date > 0
    """
    if week is not None:
        sql += f" AND EXTRACT(WEEK FROM TIMESTAMP_MILLIS(date)) = {week}"
    
    sql += " GROUP BY day_number, day_name ORDER BY day_number"
    
    base_url = build_url_with_params("/events/by-day-of-week", {"week": week})
    return exec_query_paginated(sql, page, page_size, base_url)

@app.get("/events/search")
#recherche d'évènements avec filtres optionnels de base sur nom artiste, nom lieu, date début et date fin
def search_events(
    artistName: Optional[str] = Query(None, description="Nom de l'artiste"),
    venueName: Optional[str] = Query(None, description="Nom du lieu"),
    date_start: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    date_end: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    sql = "SELECT * FROM `dataset_groupe_5.events` WHERE 1=1"
    conditions = []
    
    if artistName and artistName.strip():
        artist_clean = artistName.replace("'", "''")
        conditions.append(f"LOWER(artistName) LIKE LOWER('%{artist_clean}%')")
    
    if venueName and venueName.strip():
        venue_clean = venueName.replace("'", "''")
        conditions.append(f"LOWER(venueName) LIKE LOWER('%{venue_clean}%')")
    
    if date_start:
        conditions.append(f"TIMESTAMP_MILLIS(date) >= TIMESTAMP('{date_start}')")
    
    if date_end:
        conditions.append(f"TIMESTAMP_MILLIS(date) <= TIMESTAMP('{date_end}')")
    
    if conditions:
        sql += " AND " + " AND ".join(conditions)
    
    sql += " ORDER BY date DESC"
    
    params = {
        "artistName": artistName,
        "venueName": venueName,
        "date_start": date_start,
        "date_end": date_end
    }
    base_url = build_url_with_params("/events/search", params)
    
    return exec_query_paginated(sql, page, page_size, base_url)

@app.get("/events/hour")
#donne les évènements par heure, avec filtre optionnel sur une heure spécifique
def get_events_by_hour(
    hour: Optional[str] = Query(None, description="Heure spécifique (ex: 20:00:00)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    params = {}
    
    if hour:
        sql = f"SELECT * FROM `dataset_groupe_5.events` WHERE hour = '{hour}' ORDER BY date DESC"
        params["hour"] = hour
    else:
        sql = """
            SELECT 
                hour,
                COUNT(*) AS event_count,
                ROUND(AVG(risk_score), 3) AS avg_risk_score
            FROM `dataset_groupe_5.events`
            GROUP BY hour
            ORDER BY hour
        """
    
    base_url = build_url_with_params("/events/hour", params)
    return exec_query_paginated(sql, page, page_size, base_url)
  
@app.get("/events/popular-days")
#donne les jours avec le plus d'évènements, avec filtre optionnel sur un nombre minimum d'évènements
def get_popular_days(
    min_events: Optional[int] = Query(None, description="Nombre minimum d'évènements (optionnel)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    sql = """
        SELECT 
            DATE(TIMESTAMP_MILLIS(date)) as event_date,
            COUNT(*) as total_events
        FROM `dataset_groupe_5.events`
        GROUP BY event_date
    """
    
    if min_events is not None:
        sql += f" HAVING total_events > {min_events}"
    
    sql += " ORDER BY total_events DESC"
    
    params = {"min_events": min_events}
    base_url = build_url_with_params("/events/popular-days", params)
    
    return exec_query_paginated(sql, page, page_size, base_url)

@app.get("/events/place-stats")
#donne des statistiques sur les lieux ou détail des évènements dans un lieu spécifique
def get_venues_stats(
    venueName: Optional[str] = Query(None, description="Nom (ou partie du nom) du lieu"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    params = {}

    if venueName:
        v_clean = venueName.replace("'", "''")
        sql = f"""
            SELECT 
                venueName,
                locationText,
                FORMAT_TIMESTAMP('%Y-%m-%d %H:%M', TIMESTAMP_MILLIS(date)) as event_date_formatted,
                artistName,
                risk_score,
                rsvpCountInt
            FROM `dataset_groupe_5.events`
            WHERE LOWER(venueName) LIKE LOWER('%{v_clean}%')
            ORDER BY date DESC
        """
        params["venueName"] = venueName
    else:
        sql = """
            SELECT 
                venueName, 
                MAX(locationText) as city,
                COUNT(*) as total_events,
                ROUND(AVG(risk_score), 2) as average_risk,
                SUM(rsvpCountInt) as total_rsvps
            FROM `dataset_groupe_5.events`
            WHERE venueName IS NOT NULL
            GROUP BY venueName
            ORDER BY total_events DESC
        """

    base_url = build_url_with_params("/events/place-stats", params)
    
    return exec_query_paginated(sql, page, page_size, base_url)

@app.get("/events/genres-trends")
#donne les tendances par genre musical, avec filtre optionnel sur le nombre minimum d'évènements
def get_genre_trends(
    min_events: int = Query(5, description="Ignorer les genres avec moins de X événements"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    sql = f"""
        SELECT 
            TRIM(genre) as genre_name,
            COUNT (*) as total_events,
            ROUND(AVG(rsvpCountInt), 0) as avg_attendance,
            ROUND(AVG(risk_score), 2) as avg_risk
        FROM `dataset_groupe_5.events`,
        UNNEST(SPLIT(genres, ',')) as genre
        WHERE genres IS NOT NULL
        GROUP BY genre_name
        HAVING total_events >= {min_events}
        ORDER BY avg_attendance DESC
    """

    params = {
        "min_events": min_events
    }
    base_url =  build_url_with_params("/events/genres-trends", params)
    return exec_query_paginated(sql, page, page_size, base_url=base_url)


@app.get("/events/competition-impact")
#analyse l'impact de la concurrence en divisant les données en groupes de taille égale (Quantiles)
def get_competition_impact(
    groups: int = Query(5, ge=2, le=20, description="Nombre de groupes"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    sql = f"""
        WITH RankedEvents AS (
            SELECT 
                events_same_day,
                rsvpCountInt,
                risk_score,
                +  NTILE({groups}) OVER (ORDER BY events_same_day) as quantile_rank
            FROM `dataset_groupe_5.events`
        )
        SELECT 
            quantile_rank as sort_order,
            CONCAT(
                'Groupe ', CAST(quantile_rank AS STRING), 
                ' (', CAST(MIN(events_same_day) AS STRING), ' - ', CAST(MAX(events_same_day) AS STRING), ' concurrents)'
            ) as competition_level,
            COUNT(*) as nb_events_analyzed,
            ROUND(AVG(rsvpCountInt), 0) as avg_rsvp_per_event,
            ROUND(AVG(risk_score), 2) as avg_risk
        FROM RankedEvents
        GROUP BY quantile_rank
        ORDER BY quantile_rank
    """

    params = {"groups": groups} 
    base_url = build_url_with_params("/events/competition-impact", params)
    
    return exec_query_paginated(sql, page, page_size, base_url=base_url)


@app.get("/events/by-risk-category")
#donne le nombre d'évènements par catégorie de risque
def get_events_by_risk_category(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    sql = """
        SELECT 
            risk_category,
            COUNT(*) AS event_count
        FROM `dataset_groupe_5.events`
        GROUP BY risk_category
        ORDER BY risk_category
    """
    params = {}
    base_url = build_url_with_params("/events/by-risk-category", params)

    return exec_query_paginated(sql, page, page_size, base_url)

@app.get("/events/by-followers")
#donne les évènements filtrés par nombre de followers
def get_events_by_followers(
    min: int = Query(None, description="Nombre minimum de followers voulu"),
    max: Optional[int] = Query(None, description="Nombre maximum de followers voulu"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):

    sql = "SELECT * FROM `dataset_groupe_5.events` WHERE 1=1"
    
    if min is not None:
        sql += f" AND followers >= {min}"
    
    if max is not None:
        sql += f" AND followers <= {max}"
    
    params = {"min": min, "max": max}
    base_url = build_url_with_params("/events/by-followers", params)
    
    return exec_query_paginated(sql, page, page_size, base_url)


@app.get("/events/risk-by-followers")
#analyse le risque moyen en fonction du nombre de followers, divisé en groupes de taille égale (Quantiles)
def get_risk_by_quantiles(
    groups: int = Query(5, description="Nombre de groupes"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):

    sql = f"""
        SELECT 
            `groups`,
            MIN(followers) as min_followers,
            MAX(followers) as max_followers,
            ROUND(AVG(risk_score), 2) as average_risk,
            COUNT(*) as nb_events
    FROM (
        SELECT 
            risk_score, 
            followers,
            NTILE({groups}) OVER (ORDER BY followers ASC) as `groups`
        FROM `dataset_groupe_5.events`
        WHERE followers IS NOT NULL AND risk_score IS NOT NULL
    )
    GROUP BY `groups`
    ORDER BY `groups` ASC
"""
    
    params = {"groups": groups}
    base_url = build_url_with_params("/events/risk-by-followers", params)

    return exec_query_paginated(sql, page, page_size, base_url)


#----------------#
# Endpoint-Bonus #
#----------------#