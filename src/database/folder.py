from bson import ObjectId  
from datetime import datetime

# Import necessary classes and modules
from .mongodb import MongoDB
from config import cfg
from logger import logger

# Get database configuration
db_cfg = cfg.db

class Folder(MongoDB):
    def __init__(self):
        super().__init__(db_cfg.folders_collection)

    def get_folder(self, folder_id):
        try:
            folder = self.find_one({"folder_id": folder_id, "is_deleted": False})
            if folder:
                logger.info(f"Folder retrieved successfully: {folder}")
            else:
                logger.info(f"No folder found with ID: {folder_id}")
            return folder
        except Exception as e:
            logger.error(f"An error occurred while retrieving folder {folder_id}: {e}")
            return None
        
    def get_all_folder_by_user_id(self, user_id, page, limit, keyword):
        try:
            search_filter = {
                "user_id": ObjectId(user_id),
                "is_deleted": False
            }

            # Add the keyword search to the filter if keyword is provided
            if keyword:
                search_filter["folder_name"] = {"$regex": keyword, "$options": "i"}

            folders = self.find_all(search_filter, page, limit, sort={"updated_at": -1})
            result = []
            for folder in folders:
                result.append({
                    "folder_id": folder["_id"]["$oid"],
                    "folder_name": folder["folder_name"],
                    "user_id": folder["user_id"]["$oid"],
                    "create_at": folder["create_at"]["$date"],
                    "updated_at": folder["updated_at"]["$date"],
                })
            return result
        except Exception as e:
            logger.error(f"An error occurred while get all folder by user_id {user_id}: {e}")
            return None

    def create_folder(self, folder_name, user_id):
        try:
            # Create a new foldera
            new_folder = {
                "folder_name": folder_name,
                "user_id": ObjectId(user_id),
                "is_deleted": False,
                "create_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insert the new folder document into the database
            folder_id = self.add(new_folder)

            # If the user ID is returned, the registration is successful
            if folder_id:
                logger.info(f"Folder {folder_name} created successfully!")
                return str(folder_id)
            else:
                logger.error(f"Failed to create {folder_name}.")
                return False
        except Exception as e:
            logger.error(f"An error occurred during create folder: {e}")
            return False
        
    def update_folder(self, folder_id, folder_name):
        try:
            result = self.update(
                {"_id": ObjectId(folder_id)},
                {"folder_name": folder_name, "updated_at": datetime.utcnow()},
            )
            if result.modified_count > 0:
                logger.info(f"Folder updated with ID: {folder_id}")
                return True
            else:
                logger.info(f"No folder updated with ID: {folder_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during update folder: {e}")
            return False
    
    def delete_folder(self, folder_id):
        try:
            result = self.update(
                {"_id": ObjectId(folder_id)},
                {"is_deleted": True, "updated_at": datetime.utcnow()},
            )
            if result.modified_count > 0:
                logger.info(f"Folder deleted with ID: {folder_id}")
                return True
            else:
                logger.info(f"No folder deleted with ID: {folder_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during delete folder: {e}")
            return False