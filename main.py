import os
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fake user DB (for now)
users = {}

PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")


# =========================
# AUTH
# =========================

@app.post("/register")
def register(email: str = Form(...), password: str = Form(...)):
    users[email] = password
    return {"message": "User registered"}


@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    if users.get(email) == password:
        return {"message": "Login successful"}
    return {"error": "Invalid credentials"}


# =========================
# ANALYZE
# =========================

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)

    # Clean amount column
    df["Amount"] = df["Amount"].astype(str).str.replace(",", "")
    df["Amount"] = df["Amount"].astype(float)

    total = df["Amount"].sum()
    transactions = len(df)
    average = total / transactions if transactions else 0

    vat = total * 0.075
    wht = total * 0.05
    cit = total * 0.30

    ai_insight = f"""
Analysis completed for {transactions} transactions.
Total revenue: ₦{total:,.2f}
VAT (7.5%): ₦{vat:,.2f}
WHT (5%): ₦{wht:,.2f}
CIT (30%): ₦{cit:,.2f}

Insight: Your business shows strong financial activity. Ensure proper tax remittance.
"""

    return {
        "total": total,
        "average": average,
        "transactions": transactions,
        "vat": vat,
        "wht": wht,
        "cit": cit,
        "ai_insight": ai_insight
    }


# =========================
# PAYSTACK
# =========================

@app.post("/pay")
def initialize_payment(email: str = Form(...), amount: int = Form(...)):
    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET}",
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "amount": amount * 100  # kobo
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()