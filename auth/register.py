from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from storage.user_db import create_user, create_user_table

router = APIRouter()
create_user_table()


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


@router.post("/register")
def register(data: RegisterRequest):
    try:
        create_user(data.name, data.email, data.password)
        return {"message": "User registered successfully"}
    except Exception:
        raise HTTPException(status_code=400, detail="User already exists")
