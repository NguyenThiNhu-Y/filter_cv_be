from bson import ObjectId  
from datetime import datetime

# Import necessary classes and modules
from .mongodb import MongoDB
from config import cfg
from logger import logger

# Get database configuration
db_cfg = cfg.db

class ResumeCertificate(MongoDB):
    def __init__(self):
        super().__init__(db_cfg.resume_certificates_collection)

    def get_resume_certificate(self, resume_certificate_id):
        try:
            resume_certificate = self.find_one({"_id": ObjectId(resume_certificate_id), "is_deleted": False})
            if resume_certificate:
                logger.info(f"Resume certificate retrieved successfully: {resume_certificate}")
            else:
                logger.info(f"No resume certificate found with ID: {resume_certificate_id}")
            return resume_certificate
        except Exception as e:
            logger.error(f"An error occurred while retrieving resume certificate {resume_certificate_id}: {e}")
            return None

    def create_resume_certificate(self, certificate_data):
        try:
            # Create a new resume certificate document
            new_resume_certificate = {
                "title": certificate_data.title,
                "certification_embedding": certificate_data.certification_embedding,
                "date": certificate_data.date,
                "resume_id": ObjectId(certificate_data.resume_id),
                "is_deleted": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insert the new resume certificate document into the database
            resume_certificate_id = self.add(new_resume_certificate)

            # If the resume_certificate_id is returned, the creation is successful
            if resume_certificate_id:
                logger.info(f"Resume certificate created successfully with ID: {resume_certificate_id}")
                return str(resume_certificate_id)
            else:
                logger.error("Failed to create resume certificate.")
                return False
        except Exception as e:
            logger.error(f"An error occurred during create resume certificate: {e}")
            return False

    def update_resume_certificate(self, resume_certificate_id, certificate_data):
        try:
            update_data = {
                "title": certificate_data.get("title"),
                "certification_embedding": certificate_data.get("certification_embedding"),
                "date": certificate_data.get("date"),
                "resume_id": ObjectId(certificate_data.get("resume_id")),
                "updated_at": datetime.utcnow()
            }

            result = self.update(
                {"_id": ObjectId(resume_certificate_id)},
                update_data,
            )
            if result.modified_count > 0:
                logger.info(f"Resume certificate updated with ID: {resume_certificate_id}")
                return True
            else:
                logger.info(f"No resume certificate updated with ID: {resume_certificate_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during update resume certificate: {e}")
            return False

    def delete_resume_certificate(self, resume_certificate_id):
        try:
            result = self.update(
                {"_id": ObjectId(resume_certificate_id)},
                {"is_deleted": True, "updated_at": datetime.utcnow()},
            )
            if result.modified_count > 0:
                logger.info(f"Resume certificate deleted with ID: {resume_certificate_id}")
                return True
            else:
                logger.info(f"No resume certificate deleted with ID: {resume_certificate_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during delete resume certificate: {e}")
            return False
