from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI()

# ✅ Enable CORS (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "VFG TaxRecon Backend Running 🚀"}


# ✅ FULL UPLOAD ENDPOINT
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        # ✅ Basic calculations
        total = df.select_dtypes(include='number').sum().sum()
        transactions = len(df)
        average = total / transactions if transactions else 0

        # Example tax calculations
        vat = total * 0.075
        wht = total * 0.05
        cit = total * 0.30

        return {
            "total": float(total),
             "average": float(average),
                "transactions": len(df),  
             "vat": float(vat),
             "wht": float(wht),
             "cit": float(cit)
        }

    except Exception as e:
        return {"error": str(e)}