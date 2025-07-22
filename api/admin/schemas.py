from pydantic import BaseModel
from typing import List, Optional

class FileUploadResponse(BaseModel):
    success: bool
    table_name: str
    records_processed: int
    records_inserted: int
    errors: List[str]
    message: str

class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str