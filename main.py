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
    return {"message": "API is working"}

@app.post("/login")
def login(data: dict):
    email = data.get("email")
    password = data.get("password")

    if email == "test@test.com" and password == "1234":
        return {"status": "success"}
    
    return {"status": "failed"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        df = pd.read_excel(file.file)

        if "Amount" not in df.columns:
            return {"error": "Missing 'Amount' column"}

        df["Amount"] = df["Amount"].astype(str).str.replace(",", "")
        df["Amount"] = df["Amount"].astype(float)

        total = df["Amount"].sum()
        transactions = len(df)
        average = total / transactions if transactions > 0 else 0

        vat = total * 0.075
        wht = total * 0.05
        cit = total * 0.30

        ai_insight = (
            "Analysis completed for " + str(transactions) + " transactions.\n"
            "Total revenue: ₦" + format(total, ",.2f") + "\n"
            "VAT (7.5%): ₦" + format(vat, ",.2f") + "\n"
            "WHT (5%): ₦" + format(wht, ",.2f") + "\n"
            "CIT (30%): ₦" + format(cit, ",.2f") + "\n\n"
            "Insight: Your business shows strong financial activity."
        )

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