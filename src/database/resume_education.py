from bson import ObjectId  
from datetime import datetime

# Import necessary classes and modules
from .mongodb import MongoDB
from config import cfg
from logger import logger

# Get database configuration
db_cfg = cfg.db

class ResumeEducation(MongoDB):
    def __init__(self):
        super().__init__(db_cfg.resume_educations_collection)

    def get_resume_education(self, resume_education_id):
        try:
            education = self.find_one({"_id": ObjectId(resume_education_id), "is_deleted": False})
            if education:
                logger.info(f"Education record retrieved successfully: {education}")
            else:
                logger.info(f"No education record found with ID: {resume_education_id}")
            return education
        except Exception as e:
            logger.error(f"An error occurred while retrieving education record {resume_education_id}: {e}")
            return None

    def create_resume_education(self, education_data):
        try:
            # Create a new education document
            new_education = {
                "name": education_data.name,
                "education_name_embedding": education_data.education_name_embedding,
                "start_date": education_data.start_date,
                "end_date": education_data.end_date,
                "major": education_data.major,
                "gpa": education_data.gpa,
                "resume_id": ObjectId(education_data.resume_id),
                "is_deleted": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insert the new education document into the database
            education_id = self.add(new_education)

            # If the education_id is returned, the creation is successful
            if education_id:
                logger.info(f"Education record created successfully with ID: {education_id}")
                return str(education_id)
            else:
                logger.error("Failed to create education record.")
                return False
        except Exception as e:
            logger.error(f"An error occurred during create education record: {e}")
            return False

    def update_resume_education(self, resume_education_id, education_data):
        try:
            update_data = {
                "name": education_data.name,
                "education_name_embedding": education_data.education_name_embedding,
                "start_date": education_data.start_date,
                "end_date": education_data.end_date,
                "major": education_data.major,
                "gpa": education_data.gpa,
                "resume_id": ObjectId(education_data.resume_id),
                "updated_at": datetime.utcnow()
            }

            result = self.update(
                {"_id": ObjectId(resume_education_id)},
                update_data,
            )
            if result.modified_count > 0:
                logger.info(f"Education record updated with ID: {resume_education_id}")
                return True
            else:
                logger.info(f"No education record updated with ID: {resume_education_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during update education record: {e}")
            return False

    def delete_resume_education(self, resume_education_id):
        try:
            result = self.update(
                {"_id": ObjectId(resume_education_id)},
                {"is_deleted": True, "updated_at": datetime.utcnow()},
            )
            if result.modified_count > 0:
                logger.info(f"Education record deleted with ID: {resume_education_id}")
                return True
            else:
                logger.info(f"No education record deleted with ID: {resume_education_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during delete education record: {e}")
            return False
