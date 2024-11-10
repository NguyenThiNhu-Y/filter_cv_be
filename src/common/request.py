import sys

sys.path.append(".")
from config import cfg

cfg_db = cfg.db
from pydantic import BaseModel


class Pagination(BaseModel):
    page: int = 1
    limit: int = cfg_db["default_limit"]