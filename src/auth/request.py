# Mô hình user
from pydantic import BaseModel


class User(BaseModel):
    email: str
    full_name: str | None = None
    hashed_password: str

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str