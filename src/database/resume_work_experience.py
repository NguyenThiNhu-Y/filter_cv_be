from bson import ObjectId  
from datetime import datetime

# Import necessary classes and modules
from .mongodb import MongoDB
from config import cfg
from logger import logger

# Get database configuration
db_cfg = cfg.db

class ResumeWorkExperience(MongoDB):
    def __init__(self):
        super().__init__(db_cfg.resume_work_experiences_collection)

    def get_resume_work_experience(self, resume_work_experience_id):
        try:
            work_experience = self.find_one({"_id": ObjectId(resume_work_experience_id), "is_deleted": False})
            if work_experience:
                logger.info(f"Work experience retrieved successfully: {work_experience}")
            else:
                logger.info(f"No work experience found with ID: {resume_work_experience_id}")
            return work_experience
        except Exception as e:
            logger.error(f"An error occurred while retrieving work experience {resume_work_experience_id}: {e}")
            return None

    def create_resume_work_experience(self, experience_data):
        try:
            # Create a new work experience document
            new_work_experience = {
                "job_title": experience_data.job_title,
                "job_summary": experience_data.job_summary,
                "company_name": experience_data.company_name,
                "start_date": experience_data.start_date,
                "end_date": experience_data.end_date,
                "resume_id": ObjectId(experience_data.resume_id),
                "is_deleted": False,
                "create_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insert the new work experience document into the database
            work_experience_id = self.add(new_work_experience)

            # If the work_experience_id is returned, the creation is successful
            if work_experience_id:
                logger.info(f"Work experience created successfully with ID: {work_experience_id}")
                return str(work_experience_id)
            else:
                logger.error("Failed to create work experience.")
                return False
        except Exception as e:
            logger.error(f"An error occurred during create work experience: {e}")
            return False

    def update_resume_work_experience(self, resume_work_experience_id, experience_data):
        try:
            update_data = {
                "job_title": experience_data.job_title,
                "job_summary": experience_data.job_summary,
                "company_name": experience_data.company_name,
                "start_date": experience_data.start_date,
                "end_date": experience_data.end_date,
                "resume_id": ObjectId(experience_data.resume_id),
                "updated_at": datetime.utcnow()
            }

            result = self.update(
                {"_id": ObjectId(resume_work_experience_id)},
                update_data,
            )
            if result.modified_count > 0:
                logger.info(f"Work experience updated with ID: {resume_work_experience_id}")
                return True
            else:
                logger.info(f"No work experience updated with ID: {resume_work_experience_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during update work experience: {e}")
            return False

    def delete_resume_work_experience(self, resume_work_experience_id):
        try:
            result = self.update(
                {"_id": ObjectId(resume_work_experience_id)},
                {"is_deleted": True, "updated_at": datetime.utcnow()},
            )
            if result.modified_count > 0:
                logger.info(f"Work experience deleted with ID: {resume_work_experience_id}")
                return True
            else:
                logger.info(f"No work experience deleted with ID: {resume_work_experience_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during delete work experience: {e}")
            return False
