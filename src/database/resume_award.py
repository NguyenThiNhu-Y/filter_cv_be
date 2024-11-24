from bson import ObjectId  
from datetime import datetime

# Import necessary classes and modules
from .mongodb import MongoDB
from config import cfg
from logger import logger

# Get database configuration
db_cfg = cfg.db

class ResumeAward(MongoDB):
    def __init__(self):
        super().__init__(db_cfg.resume_awards_collection)

    def get_resume_award_by_resume_id(self, resume_id):
        search_filter = {
            "resume_id": ObjectId(resume_id),
            "is_deleted": False
        }

        award_datas = self.find_all(search_filter)
        result = []
        for award_data in award_datas:
            result.append({
                "title": award_data["title"],
                "award_title_embedding": award_data["award_title_embedding"],
            })
        return result

    def get_resume_award(self, resume_award_id):
        try:
            resume_award = self.find_one({"_id": ObjectId(resume_award_id), "is_deleted": False})
            if resume_award:
                logger.info(f"Resume award retrieved successfully: {resume_award}")
            else:
                logger.info(f"No resume award found with ID: {resume_award_id}")
            return resume_award
        except Exception as e:
            logger.error(f"An error occurred while retrieving resume award {resume_award_id}: {e}")
            return None

    def create_resume_award(self, award_data):
        try:
            # Create a new resume award document
            new_resume_award = {
                "title": award_data.title,
                "award_title_embedding": award_data.award_title_embedding,
                "date": award_data.date,
                "resume_id": ObjectId(award_data.resume_id),
                "is_deleted": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insert the new resume award document into the database
            resume_award_id = self.add(new_resume_award)

            # If the resume_award_id is returned, the creation is successful
            if resume_award_id:
                logger.info(f"Resume award created successfully with ID: {resume_award_id}")
                return str(resume_award_id)
            else:
                logger.error("Failed to create resume award.")
                return False
        except Exception as e:
            logger.error(f"An error occurred during create resume award: {e}")
            return False

    def update_resume_award(self, resume_award_id, award_data):
        try:
            update_data = {
                "title": award_data.get("title"),
                "award_title_embedding": award_data.get("award_title_embedding"),
                "date": award_data.get("date"),
                "resume_id": ObjectId(award_data.get("resume_id")),
                "updated_at": datetime.utcnow()
            }

            result = self.update(
                {"_id": ObjectId(resume_award_id)},
                update_data,
            )
            if result.modified_count > 0:
                logger.info(f"Resume award updated with ID: {resume_award_id}")
                return True
            else:
                logger.info(f"No resume award updated with ID: {resume_award_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during update resume award: {e}")
            return False

    def delete_resume_award(self, resume_award_id):
        try:
            result = self.update(
                {"_id": ObjectId(resume_award_id)},
                {"is_deleted": True, "updated_at": datetime.utcnow()},
            )
            if result.modified_count > 0:
                logger.info(f"Resume award deleted with ID: {resume_award_id}")
                return True
            else:
                logger.info(f"No resume award deleted with ID: {resume_award_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during delete resume award: {e}")
            return False
