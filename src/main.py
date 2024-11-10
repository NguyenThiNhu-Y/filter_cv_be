import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from auth import route as auth_route
from folder import route as folder_route
from resume import route as resume_route

load_dotenv()
# Tạo ứng dụng FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, or specify a list of domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Gọi các route từ file auth.py
app.include_router(auth_route.router, prefix="/api", tags=["Auth"])
app.include_router(folder_route.router, prefix="/api/folder", tags=["Folder"])
app.include_router(resume_route.router, prefix="/api/resume", tags=["Resume"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)