from pydantic import BaseModel

class FileCheck(BaseModel):
    name: str
    size: int
    partial_hash: str
    full_hash: str

class FileInfo(BaseModel):
    name: str
    size: int
    full_hash: str
    location: str