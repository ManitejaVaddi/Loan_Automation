from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from storage.user_db import create_session, delete_session, get_user

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
        "name": user[1],
        "role": user[2],
        "session_token": create_session(user[0])
    }


@router.post("/logout")
def logout(x_session_token: str | None = Header(default=None)):
    if not x_session_token:
        raise HTTPException(status_code=400, detail="Session token missing")

    if not delete_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    return {"message": "Logout successful"}
