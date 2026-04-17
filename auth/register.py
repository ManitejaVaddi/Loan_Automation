from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from storage.user_db import get_user

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(data: LoginRequest):
    user = get_user(data.email, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user_id": user[0],
        "name": user[1]
    }