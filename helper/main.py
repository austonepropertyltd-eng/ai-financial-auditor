from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# Allow frontend (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test route
@app.get("/")
def home():
    return {"message": "API running"}


# LOGIN ROUTE (simple demo)
@app.post("/login")
def login(data: dict):
    email = data.get("email")
    password = data.get("password")

    # Simple test login
    if email == "test@test.com" and password == "1234":
        return {"status": "success"}
    
    return {"status": "error", "message": "Invalid login"}


# ANALYZE ROUTE
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)

    total = df.sum().sum()
    transactions = len(df)
    average = total / transactions if transactions else 0

    vat = total * 0.075
    wht = total * 0.05
    cit = total * 0.30

    insight = f"""
Analysis completed for {transactions} transactions.
Total revenue: ₦{total:,.2f}
VAT (7.5%): ₦{vat:,.2f}
WHT (5%): ₦{wht:,.2f}
CIT (30%): ₦{cit:,.2f}

Insight: Your business shows strong financial activity. Ensure proper tax remittance and monitor high expense categories.
"""

    return {
        "total": total,
        "average": average,
        "transactions": transactions,
        "vat": vat,
        "wht": wht,
        "cit": cit,
        "ai_insight": insight
    }