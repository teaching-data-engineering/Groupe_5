from typing import Union, Optional
from fastapi import FastAPI, Request
from pydantic import BaseModel
from google.cloud import bigquery
from google.oauth2 import service_account
import math

credentials = service_account.Credentials.from_service_account_file(
    "key_group_5.json"
)

client = bigquery.Client(
    credentials=credentials,
    project=credentials.project_id
)

app = FastAPI()

# Configuration de la pagination
RESULTS_PER_PAGE = 50  # Nombre de résultats par page

class Objet(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


def exec_query(sql: str):
    """Exécute une requête SQL sur BigQuery"""
    query_job = client.query(sql)
    results = [dict(row) for row in query_job.result()]
    return results


def build_metadata(page: int, total_results: int, results_per_page: int, request: Request, endpoint_path: str):
    """
    Construit les métadonnées pour la pagination
    
    Args:
        page: numéro de la page actuelle
        total_results: nombre total de résultats
        results_per_page: nombre de résultats par page
        request: objet Request de FastAPI pour récupérer l'URL de base
        endpoint_path: chemin de l'endpoint (ex: '/events')
    
    Returns:
        dict: dictionnaire contenant les métadonnées
    """
    total_pages = math.ceil(total_results / results_per_page) if total_results > 0 else 1
    
    # Construire l'URL de la page suivante
    next_page_url = None
    if page < total_pages:
        base_url = str(request.base_url).rstrip('/')
        next_page_url = f"{base_url}{endpoint_path}?page={page + 1}"
    
    return {
        "page": page,
        "total_pages": total_pages,
        "results_per_page": results_per_page,
        "total_results": total_results,
        "next_page_url": next_page_url
    }


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
def get_all_events(request: Request, page: int = 1):
    """
    Endpoint de base pour tous les événements
    
    Args:
        request: objet Request de FastAPI
        page: numéro de la page (par défaut 1)
    
    Returns:
        dict: contenant les métadonnées et les événements
    """
    # Validation du numéro de page
    if page < 1:
        page = 1
    
    # IMPORTANT: Remplacez ces valeurs par votre propre dataset et table
    # Format: `project_id.dataset_id.table_name`
    TABLE_NAME = "dataset_groupe_5.events"
    
    # 1. Compter le nombre total d'événements
    count_query = f"""
        SELECT COUNT(*) as total
        FROM `{TABLE_NAME}`
    """
    
    count_result = exec_query(count_query)
    total_results = count_result[0]['total']
    
    # 2. Calculer l'offset pour la pagination
    offset = (page - 1) * RESULTS_PER_PAGE
    
    # 3. Récupérer les événements pour la page demandée
    events_query = f"""
        SELECT *
        FROM `{TABLE_NAME}`
        ORDER BY date DESC
        LIMIT {RESULTS_PER_PAGE}
        OFFSET {offset}
    """
    
    events = exec_query(events_query)
    
    # 4. Construire les métadonnées
    metadata = build_metadata(
        page=page,
        total_results=total_results,
        results_per_page=RESULTS_PER_PAGE,
        request=request,
        endpoint_path="/events"
    )
    
    # 5. Retourner la réponse complète
    return {
        "metadata": metadata,
        "data": events
    }