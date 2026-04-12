from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "API is running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        df = pd.read_excel(file.file)

        # Ensure Amount column exists
        if "Amount" not in df.columns:
            return {"error": "Excel must contain 'Amount' column"}

        # Clean amounts (remove commas)
        df["Amount"] = df["Amount"].astype(str).str.replace(",", "")
        df["Amount"] = df["Amount"].astype(float)

        total = df["Amount"].sum()
        transactions = len(df)
        average = total / transactions if transactions > 0 else 0

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

    except Exception as e:
        return {"error": str(e)}