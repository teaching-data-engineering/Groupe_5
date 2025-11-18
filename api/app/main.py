from typing import Union, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
from google.cloud import bigquery
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("key_group_5.json")
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
def get_events(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    sql = "SELECT * FROM `dataset_groupe_5.events` ORDER BY date DESC"
    return exec_query_paginated(sql, page, page_size, f"{BASE_URL}/events")

@app.get("/events/by-day-of-week")
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
def get_events_by_hour(
    hour: Optional[str] = Query(None, description="Heure spÃ©cifique (ex: 20:00:00)"),
    risk: Optional[bool] = Query(None, description="Afficher le score moyen de risque"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    if hour:
        sql = f"SELECT * FROM `dataset_groupe_5.events` WHERE hour = '{hour}' ORDER BY date DESC"
        base_url = build_url_with_params("/events/hour", {"hour": hour, "risk": risk})
    else:
        if risk:
            sql = """
                SELECT 
                    hour,
                    COUNT(*) AS event_count,
                    ROUND(AVG(risk_score), 3) AS avg_risk_score
                FROM `dataset_groupe_5.events`
                GROUP BY hour
                ORDER BY hour
            """
        else:
            sql = """
                SELECT 
                    hour,
                    COUNT(*) AS event_count
                FROM `dataset_groupe_5.events`
                GROUP BY hour
                ORDER BY hour
            """
        base_url = build_url_with_params("/events/hour", {"risk": risk})
    
    return exec_query_paginated(sql, page, page_size, base_url)