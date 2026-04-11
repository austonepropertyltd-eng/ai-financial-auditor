from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from helper.api.upload import router as upload_router

app = FastAPI()

# ✅ Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ API route
app.include_router(upload_router, prefix="/api")

@app.get("/")
def home():
    return {"message": "VFG TaxRecon Backend Running 🚀"}