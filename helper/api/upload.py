from fastapi import APIRouter, UploadFile, File
import pandas as pd
import io

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        # Normalize column names
        df.columns = [col.strip().lower() for col in df.columns]

        if "amount" not in df.columns:
            return {"error": "Excel must contain 'Amount' column"}

        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df = df.dropna(subset=["amount"])

        total = df["amount"].sum()
        average = df["amount"].mean()
        count = len(df)

        # Taxes
        vat = total * 0.075
        wht = total * 0.05
        cit = total * 0.30

        # AI Anomaly Detection
        mean = df["amount"].mean()
        std = df["amount"].std()

        anomalies = df[df["amount"] > (mean + 2 * std)]

        insight = f"""
        Total transactions: {count}.
        Average value: {average:.2f}.
        Detected {len(anomalies)} unusually high transactions.
        """

        return {
            "total": float(total),
            "average": float(average),
            "vat": float(vat),
            "wht": float(wht),
            "cit": float(cit),
            "count": count,
            "anomalies": len(anomalies),
            "insight": insight.strip()
        }

    except Exception as e:
        return {"error": str(e)}