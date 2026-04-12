from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import openai
import os
from reportlab.pdfgen import canvas

app = FastAPI()

# ✅ CORS (allow Netlify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ OpenAI Key (from Render ENV)
import os
openai.api_key = os.getenv("proj-1agjAqvEGzXTxrVyekCSbNfruBuLEpSWKelOfUhyCBr1quVdWc94pDM31zbP-65vqtJWwiNtfFT3BlbkFJ78BzhBGF7FeJSkBgW7nQO5fY17v-DkJkBS2qtGCUZ2q5mwoz4K7Gh8tbzIo3HRlECnlpXmwQoA")

# ✅ Dummy users (for now)
users = {
    "admin@vfg.com": "123456"
}

# ✅ Store reports (temporary)
reports = []
usage_count = 0


@app.get("/")
def home():
    return {"message": "VFG TaxRecon API Running"}


# 🔐 LOGIN
@app.post("/api/login")
def login(data: dict):
    email = data.get("email")
    password = data.get("password")

    if users.get(email) == password:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=401, detail="Invalid login")


# 📊 UPLOAD + AI ANALYSIS
@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    global usage_count

    if usage_count > 5:
        return {"error": "Free limit reached. Upgrade required."}

    try:
        df = pd.read_excel(file.file)

        if "amount" not in df.columns:
            return {"error": "Excel must contain 'amount' column"}

        total = df["amount"].sum()
        avg = df["amount"].mean()
        count = len(df)

        vat = total * 0.075
        wht = total * 0.05
        cit = total * 0.30

        # 🤖 AI Insight (SAFE)
        prompt = f"""
        Analyze this financial data:
        Total: {total}
        Average: {avg}
        Transactions: {count}
        VAT: {vat}
        WHT: {wht}
        CIT: {cit}

        Give a short professional financial insight.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            insight = response.choices[0].message.content
        except:
            insight = "AI insight unavailable (check API key)."

        result = {
            "total": float(total),
            "average": float(avg),
            "transactions": count,
            "vat": float(vat),
            "wht": float(wht),
            "cit": float(cit),
            "insight": insight
        }

        reports.append(result)
        usage_count += 1

        return result

    except Exception as e:
        return {"error": str(e)}


# 📄 PDF REPORT
@app.get("/api/report")
def generate_pdf():
    file_name = "report.pdf"
    c = canvas.Canvas(file_name)

    c.drawString(100, 750, "VFG TaxRecon Report")
    c.drawString(100, 720, "AI Financial Analysis Report")

    c.save()

    return {"message": "PDF generated"}


# 📊 HISTORY
@app.get("/api/history")
def history():
    return reports