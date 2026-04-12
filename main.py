from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import openai
from reportlab.pdfgen import canvas

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 SET YOUR OPENAI KEY
openai.api_key = "YOUR_OPENAI_KEY"


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)

    total = df["amount"].sum()
    avg = df["amount"].mean()
    count = len(df)

    vat = total * 0.075
    wht = total * 0.05
    cit = total * 0.30

    # 🤖 AI Insight
    prompt = f"""
    Analyze this financial data:
    Total: {total}
    Average: {avg}
    Transactions: {count}
    VAT: {vat}
    WHT: {wht}
    CIT: {cit}

    Give professional financial insight.
    """

    ai = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    insight = ai.choices[0].message.content

    return {
        "total": float(total),
        "average": float(avg),
        "transactions": count,
        "vat": float(vat),
        "wht": float(wht),
        "cit": float(cit),
        "insight": insight
    }


# 📄 PDF DOWNLOAD
@app.get("/api/report")
def generate_pdf():
    file = "report.pdf"
    c = canvas.Canvas(file)

    c.drawString(100, 750, "VFG TaxRecon Report")
    c.drawString(100, 720, "Generated AI Financial Report")

    c.save()

    return {"message": "PDF Generated"}