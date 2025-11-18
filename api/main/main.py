from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import bigquery
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    "sa-key-group-5.json"
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


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/mon_endpoint/{objet_id}")
async def read_objet(objet_id: int, q: Union[str, None] = None):
    return {"objet_id": objet_id, "q": q}


@app.put("/mon_endpoint/{objet_id}")
def update_objet(objet_id: int, objet: Objet):
    return {"objet_name": objet.name, "objet_id": objet_id}


@app.get("/query")
def exec_query(sql: str):
    query_job = client.query(sql)
    results = [dict(row) for row in query_job.result()]
    return {"rows": results}
