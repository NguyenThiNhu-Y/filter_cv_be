from bson import ObjectId  
from datetime import datetime

# Import necessary classes and modules
from .mongodb import MongoDB
from config import cfg
from logger import logger

# Get database configuration
db_cfg = cfg.db

class ResumeReference(MongoDB):
    def __init__(self):
        super().__init__(db_cfg.resume_references_collection)

    def get_resume_reference(self, reference_id):
        try:
            resume_reference = self.find_one({"_id": ObjectId(reference_id), "is_deleted": False})
            if resume_reference:
                logger.info(f"Resume reference retrieved successfully: {resume_reference}")
            else:
                logger.info(f"No resume reference found with ID: {reference_id}")
            return resume_reference
        except Exception as e:
            logger.error(f"An error occurred while retrieving resume reference {reference_id}: {e}")
            return None

    def create_resume_reference(self, reference_data):
        try:
            # Create a new resume reference document
            new_resume_reference = {
                "reference_link": reference_data.reference_link,
                "resume_id": ObjectId(reference_data.resume_id),
                "is_deleted": False,
                "create_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insert the new resume reference document into the database
            reference_id = self.add(new_resume_reference)

            # If the reference_id is returned, the creation is successful
            if reference_id:
                logger.info(f"Resume reference created successfully with ID: {reference_id}")
                return str(reference_id)
            else:
                logger.error("Failed to create resume reference.")
                return False
        except Exception as e:
            logger.error(f"An error occurred during create resume reference: {e}")
            return False

    def update_resume_reference(self, reference_id, reference_data):
        try:
            update_data = {
                "reference_link": reference_data.get("reference_link"),
                "resume_id": ObjectId(reference_data.get("resume_id")),
                "updated_at": datetime.utcnow()
            }

            result = self.update(
                {"_id": ObjectId(reference_id)},
                update_data,
            )
            if result.modified_count > 0:
                logger.info(f"Resume reference updated with ID: {reference_id}")
                return True
            else:
                logger.info(f"No resume reference updated with ID: {reference_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during update resume reference: {e}")
            return False

    def delete_resume_reference(self, reference_id):
        try:
            result = self.update(
                {"_id": ObjectId(reference_id)},
                {"is_deleted": True, "updated_at": datetime.utcnow()},
            )
            if result.modified_count > 0:
                logger.info(f"Resume reference deleted with ID: {reference_id}")
                return True
            else:
                logger.info(f"No resume reference deleted with ID: {reference_id}")
                return False
        except Exception as e:
            logger.error(f"An error occurred during delete resume reference: {e}")
            return False
