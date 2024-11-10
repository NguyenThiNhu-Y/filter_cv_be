import os
import sys
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status

sys.path.append(".")
from auth.request import LoginRequest, RegisterRequest
from database.user import Users

# Tạo một router cho các route liên quan đến authentication
load_dotenv()
router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
user_db = Users()

@router.post("/register")
def register(user_data: RegisterRequest):
    # Kiểm tra xem email đã tồn tại hay chưa
    existing_user = user_db.get_user(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng.",
        )
    
    # Đăng ký người dùng mới
    result = user_db.register(user_data.email, user_data.password)
    
    return result

@router.post("/login")
def login(user_data: LoginRequest):
    result = user_db.login(user_data.email, user_data.password)
    return result
