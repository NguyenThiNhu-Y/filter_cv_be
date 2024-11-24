from bson import ObjectId  
from datetime import datetime

# Import necessary classes and modules
from .mongodb import MongoDB
from config import cfg
from logger import logger

# Get database configuration
db_cfg = cfg.db

class ResumeSkill(MongoDB):
    def __init__(self):
        super().__init__(db_cfg.resume_skill_collection)

    def get_resume_skill_by_resume_id(self, resume_id):
        search_filter = {
            "resume_id": ObjectId(resume_id),
            "is_deleted": False
        }

        skill_datas = self.find_all(search_filter)
        result = []
        for skill_data in skill_datas:
            result.append({
                "skill_name": skill_data["skill_name"],
                "skill_name_embedding": skill_data["skill_name_embedding"],
            })
        return result

    def get_resume_skill(self, resume_skill_id):
        try:
            resume_skill = self.find_one({"_id": ObjectId(resume_skill_id), "is_deleted": False})
            if resume_skill:
                logger.info(f"Resume skill retrieved successfully: {resume_skill}")
            else:
                logger.info(f"No resume skill found with ID: {resume_skill_id}")
            return resume_skill
        except Exception as e:
            logger.error(f"An error occurred while retrieving resume skill {resume_skill_id}: {e}")
            return None

    def create_resume_skill(self, skill_data):
        try:
            # Create a new resume skill document
            new_resume_skill = {
                "skill_name": skill_data.skill_name,
                "skill_name_embedding": skill_data.skill_name_embedding,
                "resume_id": ObjectId(skill_data.resume_id),
                "is_deleted": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insert the new resume skill document into the database
            resume_skill_id = self.add(new_resume_skill)

            # If the resume_skill_id is returned, the creation is successful
            if resume_skill_id:
                logger.info(f"Resume skill created successfully with ID: {resume_skill_id}")
                return str(resume_skill_id)
            else:
                logger.error("Failed to create resume skill.")
                return False
        except Exception as e:
            logger.error(f"An error occurred during create resume skill: {e}")
            return False

    def update_resume_skill(self, resume_skill_id, skill_data):
        try:
            update_data = {
                "skill_name": skill_data.skill_name,
                "skill_name_embedding": skill_data.skill_name_embedding,
                "resume_id": ObjectId(skill_data.get("resume_id")),
                "updated_at": datetime.utcnow()
            }

            result = self.update(
                {"_id": ObjectId(resume_skill_id)},
                update_data,
            )
            if result.modified_count > 0:
                logger.info(f"Resume skill updated with ID: {resume_skill_id}")
                return True
            else:
                logger.info(f"No resume skill updated with ID: {resume_skill_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during update resume skill: {e}")
            return False

    def delete_resume_skill(self, resume_skill_id):
        try:
            result = self.update(
                {"_id": ObjectId(resume_skill_id)},
                {"is_deleted": True, "updated_at": datetime.utcnow()},
            )
            if result.modified_count > 0:
                logger.info(f"Resume skill deleted with ID: {resume_skill_id}")
                return True
            else:
                logger.info(f"No resume skill deleted with ID: {resume_skill_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during delete resume skill: {e}")
            return False
