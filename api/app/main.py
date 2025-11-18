from typing import Union, Optional
from fastapi import FastAPI, Query, Request
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

class Objet(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

def exec_query(sql: str):
    query_job = client.query(sql)
    results = [dict(row) for row in query_job.result()]
    return {"rows": results}

def exec_query_paginated(sql: str, page: int = 1, page_size: int = 20, base_url: str = ""):
    count_sql = f"SELECT COUNT(*) as total FROM ({sql})"
    total_results_list = exec_query(count_sql)
    total_results = total_results_list["rows"][0]["total"]

    offset = (page - 1) * page_size
    total_pages = (total_results + page_size - 1) // page_size

    # RequÃªte paginÃ©e
    paginated_sql = f"{sql} LIMIT {page_size} OFFSET {offset}"
    results = exec_query(paginated_sql)["rows"]

    next_page_url = None
    if page < total_pages:
        next_page_url = f"{base_url}?page={page+1}&page_size={page_size}" 

    return {
        "metadata": {
            "page": page,
            "total_pages": total_pages,
            "results_per_page": page_size,
            "total_results": total_results,
            "next_page_url": next_page_url
        },
        "results": results
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
def get_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    sql = "SELECT * FROM `dataset_groupe_5.events`"
    return exec_query_paginated(sql, page=page, page_size=page_size, base_url="http://127.0.0.1:8000/events")