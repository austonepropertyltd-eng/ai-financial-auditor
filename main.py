from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import os
from openai import OpenAI

app = FastAPI()

# Allow frontend (Vercel) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def home():
    return {"message": "VFG TaxRecon API Running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))

    # Clean Amount column
    df["Amount"] = (
        df["Amount"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    total = df["Amount"].sum()
    transactions = len(df)
    average = total / transactions if transactions > 0 else 0

    vat = total * 0.075
    wht = total * 0.05
    cit = total * 0.30

    # =========================
    # REAL AI INSIGHT
    # =========================
    prompt = f"""
    You are a financial analyst.

    Analyze this business data:
    Total Revenue: {total}
    VAT: {vat}
    WHT: {wht}
    CIT: {cit}
    Transactions: {transactions}

    Give a short professional insight.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        ai_insight = response.choices[0].message.content
    except:
        ai_insight = "AI insight unavailable"

    return {
        "total": total,
        "average": average,
        "transactions": transactions,
        "vat": vat,
        "wht": wht,
        "cit": cit,
        "ai_insight": ai_insight
    }