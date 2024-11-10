import os
import sys
from dotenv import load_dotenv
from fastapi import APIRouter

sys.path.append(".")
from folder.request import CreateFolderRequest, UpdateFolderRequest
from database.folder import Folder

# Tạo một router cho các route liên quan đến authentication
load_dotenv()
router = APIRouter()
folder_db = Folder()

@router.post("/create")
def create(folder_data: CreateFolderRequest):
    folder_id = folder_db.create_folder(folder_data.folder_name, folder_data.user_id)
    return folder_id

@router.put("/update")
def update(folder_data: UpdateFolderRequest):
    result = folder_db.update_folder(folder_data.folder_id, folder_data.folder_name)
    return result

@router.delete("/delete/{folder_id}")
def delete(folder_id: str):
    result = folder_db.delete_folder(folder_id)
    return result

@router.get("/get_all")
def get_all(user_id: str, page: int = 1, limit: int = 10, keyword = ""):
    folders = folder_db.get_all_folder_by_user_id(user_id, page, limit, keyword)
    return folders

@router.get("/get")
def get(folder_id: str):
    folder = folder_db.get_folder(folder_id)
    return folder

