from bson import ObjectId  
from datetime import datetime

# Import necessary classes and modules
from .mongodb import MongoDB
from config import cfg
from logger import logger

# Get database configuration
db_cfg = cfg.db

class ResumeProjectExperience(MongoDB):
    def __init__(self):
        super().__init__(db_cfg.resume_project_experiences_collection)

    def get_resume_project_experience(self, resume_project_experience_id):
        try:
            project_experience = self.find_one({"_id": ObjectId(resume_project_experience_id), "is_deleted": False})
            if project_experience:
                logger.info(f"Project experience retrieved successfully: {project_experience}")
            else:
                logger.info(f"No project experience found with ID: {resume_project_experience_id}")
            return project_experience
        except Exception as e:
            logger.error(f"An error occurred while retrieving project experience {resume_project_experience_id}: {e}")
            return None

    def create_resume_project_experience(self, project_data):
        try:
            # Create a new project experience document
            new_project_experience = {
                "project_name": project_data.project_name,
                "project_description": project_data.project_description,
                "project_technologies": project_data.project_technologies,
                "responsibilities": project_data.responsibilities,
                "repository_url": project_data.repository_url,
                "demo_or_live_url": project_data.demo_or_live_url,
                "start_date": project_data.start_date,
                "end_date": project_data.end_date,
                "resume_id": ObjectId(project_data.resume_id),
                "is_deleted": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insert the new project experience document into the database
            project_experience_id = self.add(new_project_experience)

            # If the project_experience_id is returned, the creation is successful
            if project_experience_id:
                logger.info(f"Project experience created successfully with ID: {project_experience_id}")
                return str(project_experience_id)
            else:
                logger.error("Failed to create project experience.")
                return False
        except Exception as e:
            logger.error(f"An error occurred during create project experience: {e}")
            return False

    def update_resume_project_experience(self, resume_project_experience_id, project_data):
        try:
            update_data = {
                "project_name": project_data.project_name,
                "project_description": project_data.project_description,
                "project_technologies": project_data.project_technologies,
                "responsibilities": project_data.responsibilities,
                "repository_url": project_data.repository_url,
                "demo_or_live_url": project_data.demo_or_live_url,
                "start_date": project_data.start_date,
                "end_date": project_data.end_date,
                "resume_id": ObjectId(project_data.resume_id),
                "updated_at": datetime.utcnow()
            }

            result = self.update(
                {"_id": ObjectId(resume_project_experience_id)},
                update_data,
            )
            if result.modified_count > 0:
                logger.info(f"Project experience updated with ID: {resume_project_experience_id}")
                return True
            else:
                logger.info(f"No project experience updated with ID: {resume_project_experience_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during update project experience: {e}")
            return False

    def delete_resume_project_experience(self, resume_project_experience_id):
        try:
            result = self.update(
                {"_id": ObjectId(resume_project_experience_id)},
                {"is_deleted": True, "updated_at": datetime.utcnow()},
            )
            if result.modified_count > 0:
                logger.info(f"Project experience deleted with ID: {resume_project_experience_id}")
                return True
            else:
                logger.info(f"No project experience deleted with ID: {resume_project_experience_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during delete project experience: {e}")
            return False
