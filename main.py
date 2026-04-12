import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        # Save file
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Read Excel
        df = pd.read_excel(file_path)

        # 🔥 FORCE CLEAN "Amount" COLUMN
        if "Amount" not in df.columns:
            return {"error": "Amount column not found"}

        df["Amount"] = (
            df["Amount"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₦", "", regex=False)
        )

        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

        # CALCULATIONS
        total = float(df["Amount"].sum())
        average = float(df["Amount"].mean())
        transactions = int(len(df))

        vat = total * 0.075
        wht = total * 0.05
        cit = total * 0.30

        # SIMPLE AI INSIGHT
        ai_insight = (
            f"You processed {transactions} transactions. "
            f"Total revenue is ₦{round(total,2)}. "
            f"VAT is ₦{round(vat,2)}."
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