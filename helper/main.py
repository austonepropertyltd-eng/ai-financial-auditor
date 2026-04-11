from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from helper.database import Base, engine
from helper.api.auth import router as auth_router
from helper.api.upload import router as upload_router

app = FastAPI(title="TaxRecon AI")

# Create tables
Base.metadata.create_all(bind=engine)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(upload_router, prefix="/api", tags=["Upload"])