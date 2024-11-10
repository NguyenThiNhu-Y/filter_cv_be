from bson import ObjectId  
from datetime import datetime

# Import necessary classes and modules
from .mongodb import MongoDB
from config import cfg
from logger import logger

# Get database configuration
db_cfg = cfg.db

class ResumeLanguage(MongoDB):
    def __init__(self):
        super().__init__(db_cfg.resume_languages_collection)

    def get_resume_language(self, resume_language_id):
        try:
            resume_language = self.find_one({"_id": ObjectId(resume_language_id), "is_deleted": False})
            if resume_language:
                logger.info(f"Resume language retrieved successfully: {resume_language}")
            else:
                logger.info(f"No resume language found with ID: {resume_language_id}")
            return resume_language
        except Exception as e:
            logger.error(f"An error occurred while retrieving resume language {resume_language_id}: {e}")
            return None

    def create_resume_language(self, language_data):
        try:
            # Create a new resume language document
            new_resume_language = {
                "language_name": language_data.language_name,
                "language_name_embedding": language_data.language_name_embedding,
                "resume_id": ObjectId(language_data.resume_id),
                "is_deleted": False,
                "create_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insert the new resume language document into the database
            resume_language_id = self.add(new_resume_language)

            # If the resume_language_id is returned, the creation is successful
            if resume_language_id:
                logger.info(f"Resume language created successfully with ID: {resume_language_id}")
                return str(resume_language_id)
            else:
                logger.error("Failed to create resume language.")
                return False
        except Exception as e:
            logger.error(f"An error occurred during create resume language: {e}")
            return False

    def update_resume_language(self, resume_language_id, language_data):
        try:
            update_data = {
                "language_name": language_data.language_name,
                "language_name_embedding": language_data.language_name_embedding,
                "resume_id": ObjectId(language_data.resume_id),
                "updated_at": datetime.utcnow()
            }

            result = self.update(
                {"_id": ObjectId(resume_language_id)},
                update_data,
            )
            if result.modified_count > 0:
                logger.info(f"Resume language updated with ID: {resume_language_id}")
                return True
            else:
                logger.info(f"No resume language updated with ID: {resume_language_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during update resume language: {e}")
            return False

    def delete_resume_language(self, resume_language_id):
        try:
            result = self.update(
                {"_id": ObjectId(resume_language_id)},
                {"is_deleted": True, "updated_at": datetime.utcnow()},
            )
            if result.modified_count > 0:
                logger.info(f"Resume language deleted with ID: {resume_language_id}")
                return True
            else:
                logger.info(f"No resume language deleted with ID: {resume_language_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during delete resume language: {e}")
            return False
