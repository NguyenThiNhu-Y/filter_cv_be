import hashlib
from bson import ObjectId  
from datetime import datetime

# Import necessary classes and modules
from .mongodb import MongoDB
from config import cfg
from logger import logger

# Get database configuration
db_cfg = cfg.db

class Users(MongoDB):
    def __init__(self):
        super().__init__(db_cfg.users_collection)

    def get_user(self, email):
        """
        Retrieve a user from the database based on their email.

        Parameters:
            email (str): The email of the user to retrieve.

        Returns:
            dict: The user document if found, None otherwise.
        """
        try:
            user = self.find_one({"email": email, "is_deleted": False})
            if user:
                logger.info(f"User retrieved successfully: {user}")
            else:
                logger.info(f"No user found with ID: {email}")
            return user
        except Exception as e:
            logger.error(f"An error occurred while retrieving user {email}: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """
        Retrieve a user from the database based on their id.

        Parameters:
            user_id (str): The ID of the user to retrieve.

        Returns:
            dict: The user document if found, None otherwise.
        """
        try:
            user = self.find_one({"_id": ObjectId(user_id), "is_deleted": False})
            if user:
                logger.info(f"User retrieved successfully: {user}")
            else:
                logger.info(f"No user found with ID: {user_id}")
            return user
        except Exception as e:
            logger.error(f"An error occurred while retrieving user {user_id}: {e}")
            return None

    def login(self, email, password):
        """
        Authenticate a user by verifying the provided email and password.

        Parameters:
            email (str): The email of the user attempting to log in.
            password (str): The password provided by the user.

        Returns:
            A tuple where the first element is a boolean indicating if the authentication is successful,
            and the second element is the user_id if authentication is successful, None otherwise.
        """
        try:
            # Hash the provided password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Query the database to find a user with the provided email and hashed password
            user = self.find_one({"email": email, "password": hashed_password, "is_deleted": False})

            # If a user is found, authentication is successful
            if user:
                msg = f"User '{email}' logged in successfully!"
                logger.info(msg)
                # Assuming user object has an 'id' field. Adjust as per your user object structure.
                user_id = user.get('_id')  # Adjust this line to match the actual key for user_id in your user object
                return True, str(user_id), msg
            else:
                msg = "Invalid email or password."
                logger.info(msg)
                return False, None, msg
        except Exception as e:
            logger.error(f"An error occurred during authentication: {e}")
            return False, None

    def register(self, email, password):
        """
        Register a new user in the database.

        Parameters:
            email (str): The email of the new user.
            password (str): The password of the new user.
            birth_date (str): The birth date of the new user in a specific format.
            ip_address (str): The IP address of the new user.

        Returns:
            bool: True if the registration is successful, False otherwise.
        """
        try:
            # Hash the provided password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Create a new user document
            new_user = {
                "email": email,
                "password": hashed_password,
                "is_deleted": False,
                "create_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insert the new user document into the database
            user_id = self.add(new_user)

            # If the user ID is returned, the registration is successful
            if user_id:
                logger.info(f"User '{email}' registered successfully!")
                return str(user_id)
            else:
                logger.error(f"Failed to register user '{email}'.")
                return False
        except Exception as e:
            logger.error(f"An error occurred during registration: {e}")
            return False