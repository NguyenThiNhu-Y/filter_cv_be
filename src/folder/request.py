from pydantic import BaseModel

from common.request import Pagination


class CreateFolderRequest(BaseModel):
    folder_name: str
    user_id: str

class UpdateFolderRequest(BaseModel):
    folder_id: str
    folder_name: str