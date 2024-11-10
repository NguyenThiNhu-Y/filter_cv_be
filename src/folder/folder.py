import sys

sys.path.append(".")
from folder.request import CreateFolderRequest
from database.folder import Folder as FolderMongoDB

folder_mongodb = FolderMongoDB()
def create_folder(request: CreateFolderRequest):
    folder_id = folder_mongodb.create_folder(request.folder_name, request.user_id)
    return folder_id
    