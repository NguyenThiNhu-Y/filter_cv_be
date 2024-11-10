import hashlib
import sys
from fastapi import UploadFile, status, HTTPException

sys.path.append(".")
from config import cfg

cfg_file = cfg.file


def validate_file(file: UploadFile):
    if not file:
        return False, HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file found!",
        )

    if not 0 < file.size <= 1 * int(cfg_file["max_size_in_mb"]):
        return False, HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported file size is 0 - 5 MB",
        )

    if not file.content_type in cfg_file["support_file_types"]:
        return False, HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unsupported file type: {file.content_type}. Supported types are {cfg_file["support_file_types"]}'
        )

    return True, None

def calculate_hash(file: bytes):
    md5 = hashlib.md5()
    md5.update(file)

    return md5.hexdigest()

def calculate_hash_by_file_path(file_path: str):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    
    return md5.hexdigest()