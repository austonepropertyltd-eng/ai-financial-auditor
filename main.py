import os
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend (Netlify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        # Save file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Read Excel
        df = pd.read_excel(file_path)

        # 🔥 IMPORTANT: AUTO DETECT NUMERIC COLUMN
        numeric_cols = df.select_dtypes(include=['number']).columns

        if len(numeric_cols) == 0:
            return {
                "total": 0,
                "average": 0,
                "transactions": 0,
                "vat": 0,
                "wht": 0,
                "cit": 0,
                "ai_insight": "No numeric data found in file"
            }

        main_col = numeric_cols[0]  # take first numeric column

        total = float(df[main_col].sum())
        average = float(df[main_col].mean())
        transactions = int(len(df))

        vat = total * 0.075
        wht = total * 0.05
        cit = total * 0.30

        # AI Insight (simple for now)
        ai_insight = f"Processed {transactions} records. Total revenue is ₦{round(total,2)}."

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