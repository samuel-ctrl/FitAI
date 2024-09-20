from app.models.openSeachModel import AIFeedbackRequest, PromptLogger
from pymongo import IndexModel
from logging import info, error


class UserCrudService:
    def __init__(self, collection):
        self.collection = collection
        self.collection.create_indexes(
            [IndexModel([("user_id", 1)], unique=True), IndexModel([("email", 1)])]
        )

    def get_user_data(self, user_id, projection=None):
        try:
            user_data = self.collection.find_one({"user_id": user_id}, projection)
            return user_data
        except Exception as e:
            error(f"Failed to get user data: {e}")
            raise e

    def update_user_data(self, user_id, data):
        try:
            result = self.collection.update_one({"user_id": user_id}, {"$set": data})
            if result.modified_count == 0:
                info(f"No updates made for user_id: {user_id}")
                return False
            return True
        except Exception as e:
            error(f"Failed to update user data: {e}")
            raise e

    def create_user_data(self, user_id, data):
        try:
            self.collection.insert_one({"user_id": user_id, **data})
            return True
        except Exception as e:
            error(f"Failed to create user data: {e}")
            raise e

    def delete_user_data(self, user_id):
        try:
            result = self.collection.delete_one({"user_id": user_id})
            if result.deleted_count == 0:
                info(f"No user found to delete with user_id: {user_id}")
                return False
            return True
        except Exception as e:
            error(f"Failed to delete user data: {e}")
            raise e

    def get_all_users_data(self, projection=None):
        try:
            users_data = self.collection.find({}, projection)
            return list(users_data)
        except Exception as e:
            error(f"Failed to get all users data: {e}")
            raise e

    def get_user_by_email(self, email, projection=None):
        try:
            user_data = self.collection.find_one(
                {"email": email}, projection=projection
            )
            return user_data
        except Exception as e:
            error(f"Failed to get user data by email: {e}")
            raise e


class AIFeedBackCrudService:
    def __init__(self, collection):
        self.collection = collection

    async def create_feedback(self, data: AIFeedbackRequest):
        try:
            self.collection.insert_one(data.to_dict())
            return True
        except Exception as e:
            error(f"Failed to create feedback: {e}")
            raise e


class Logger:
    def __init__(self, collection):
        self.collection = collection

    async def create_logger(self, data: PromptLogger):
        try:
            self.collection.insert_one(data.to_dict())
            return True
        except Exception as e:
            error(f"Failed to create feedback: {e}")
            raise e
