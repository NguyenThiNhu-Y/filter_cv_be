from bson import ObjectId  
from datetime import datetime

# Import necessary classes and modules
from .mongodb import MongoDB
from config import cfg
from logger import logger

# Get database configuration
db_cfg = cfg.db

class Resume(MongoDB):
    def __init__(self):
        super().__init__(db_cfg.resumes_collection)

    def find_resume_by_hash(self, hash: str, folder_id: str):
        resume = self.find_one({
            "folder_id": ObjectId(folder_id), 
            "resume_file_hash": hash,
            "is_deleted": False})

        if resume:
            return resume

        return None

    def get_resume(self, resume_id):
        try:
            resume = self.find_one({"_id": ObjectId(resume_id), "is_deleted": False})
            if resume:
                logger.info(f"Resume retrieved successfully: {resume}")
            else:
                logger.info(f"No resume found with ID: {resume_id}")
            return resume
        except Exception as e:
            logger.error(f"An error occurred while retrieving resume {resume_id}: {e}")
            return None
        
    def get_all_resume_by_folder_id(self, folder_id, page, limit):
        try:
            search_filter = {
                "folder_id": ObjectId(folder_id),
                "is_deleted": False
            }

            resumess = self.find_all(search_filter, page, limit, sort={"updated_at": -1})
            result = []
            for resumes in resumess:
                result.append({
                    "resumes_id": resumes["_id"]["$oid"],
                    "folder_id": resumes["folder_id"]["$oid"],
                    "job_title": resumes["job_title"],
                    "full_name": resumes["full_name"],
                    "resume_thumbnail_base64": resumes["resume_thumbnail_base64"],
                    "email": resumes["email"],
                    "phone_number": resumes["phone_number"],
                    "skills": [],
                    "create_at": resumes["create_at"]["$date"],
                    "updated_at": resumes["updated_at"]["$date"],
                })
            return result
        except Exception as e:
            logger.error(f"An error occurred while get all resume by folder_id {folder_id}: {e}")
            return None

    def create_resume(self, resume_data):
        try:
            # Create a new resume document
            new_resume = {
                "resume_thumbnail_base64": resume_data.resume_thumbnail_base64,
                "resume_file_hash": resume_data.resume_file_hash,
                "resume_file_path": resume_data.resume_file_path,
                "job_title": resume_data.job_title,
                "job_title_embedding": resume_data.job_title_embedding,
                "summary_or_objectives": resume_data.summary_or_objectives,
                "full_name": resume_data.full_name,
                "email": resume_data.email,
                "phone_number": resume_data.phone_number,
                "address": resume_data.address,
                "folder_id": ObjectId(resume_data.folder_id), 
                "is_deleted": False,
                "create_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insert the new resume document into the database
            resume_id = self.add(new_resume)

            # If the resume ID is returned, the creation is successful
            if resume_id:
                logger.info(f"Resume created successfully with ID: {resume_id}")
                return str(resume_id)
            else:
                logger.error("Failed to create resume.")
                return False
        except Exception as e:
            logger.error(f"An error occurred during create resume: {e}")
            return False

    def update_resume(self, resume_id, resume_data):
        try:
            update_data = {
                "resume_thumbnail_url": resume_data.get("resume_thumbnail_url"),
                "resume_file_hash": resume_data.get("resume_file_hash"),
                "resume_file_path": resume_data.get("resume_file_path"),
                "job_title": resume_data.get("job_title"),
                "job_title_embedding": resume_data.get("job_title_embedding"),
                "summary_or_objectives": resume_data.get("summary_or_objectives"),
                "full_name": resume_data.get("full_name"),
                "email": resume_data.get("email"),
                "phone_number": resume_data.get("phone_number"),
                "address": resume_data.get("address"),
                "folder_id": ObjectId(resume_data.get("folder_id")),
                "updated_at": datetime.utcnow()
            }

            result = self.update(
                {"_id": ObjectId(resume_id)},
                update_data,
            )
            if result.modified_count > 0:
                logger.info(f"Resume updated with ID: {resume_id}")
                return True
            else:
                logger.info(f"No resume updated with ID: {resume_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during update resume: {e}")
            return False

    def delete_resume(self, resume_id):
        try:
            result = self.update(
                {"_id": ObjectId(resume_id)},
                {"is_deleted": True, "updated_at": datetime.utcnow()},
            )
            if result.modified_count > 0:
                logger.info(f"Resume deleted with ID: {resume_id}")
                return True
            else:
                logger.info(f"No resume deleted with ID: {resume_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during delete resume: {e}")
            return False
