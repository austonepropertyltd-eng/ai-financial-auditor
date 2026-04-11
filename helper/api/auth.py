from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# 🔥 TEMP DATABASE (upgrade later)
users = []

class User(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(user: User):
    for u in users:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="User already exists")

    users.append(user.dict())
    return {"message": "User registered successfully"}

@router.post("/login")
def login(user: User):
    for u in users:
        if u["email"] == user.email and u["password"] == user.password:
            return {"message": "Login successful"}

    raise HTTPException(status_code=401, detail="Invalid credentials")