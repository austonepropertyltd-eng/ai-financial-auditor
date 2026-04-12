from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI()

# Allow frontend (Netlify) to talk to backend (Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()

    # Read Excel
    df = pd.read_excel(io.BytesIO(contents))

    # Normalize column names
    df.columns = [col.strip().lower() for col in df.columns]

    # Ensure amount column exists
    if "amount" not in df.columns:
        return {"error": "Amount column not found"}

    # Clean amount values
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(",", "")
        .str.replace("₦", "")
    )

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    # Calculations
    total = df["amount"].sum()
    transactions = len(df)
    average = total / transactions if transactions > 0 else 0

    vat = total * 0.075
    wht = total * 0.05
    cit = total * 0.30

    # SAFE AI INSIGHT (NO BREAK)
    ai_insight = f"""Analysis completed for {transactions} transactions.
Total revenue: ₦{total:,.2f}.
VAT (7.5%): ₦{vat:,.2f}.
WHT (5%): ₦{wht:,.2f}.
CIT (30%): ₦{cit:,.2f}.

Insight: Your business shows strong financial activity. Ensure proper tax remittance and monitor high expense categories."""

    return {
        "total": total,
        "average": average,
        "transactions": transactions,
        "vat": vat,
        "wht": wht,
        "cit": cit,
        "ai_insight": ai_insight
    }