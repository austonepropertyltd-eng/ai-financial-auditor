from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TaxData(BaseModel):
    total: float

database = []

@app.post("/api/tax/save")
def save_tax(data: TaxData):
    tax = data.total * 0.15
    database.append({"total": data.total, "tax": tax})
    return {"tax": tax}

@app.get("/api/tax/all")
def get_all():
    return database