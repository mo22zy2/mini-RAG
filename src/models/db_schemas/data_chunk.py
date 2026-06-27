from typing import Optional

from bson.objectid import ObjectId  # type: ignore
from pydantic import BaseModel, Field, field_validator


class DataChunk(BaseModel):
    _id: Optional[str] = None
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId
    
    @field_validator("chunk_project_id")
    @classmethod
    def validate_project_id(cls, v: ObjectId) -> ObjectId:
        if not isinstance(v, ObjectId):
         raise ValueError("Invalid ObjectId")
        return v    

    @field_validator("chunk_text")
    @classmethod
    def validate_chunk_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("chunk_text must not be empty")
        return v

    class Config:
        arbitrary_types_allowed = True
        
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("chunk_project_id", 1)],
                "name": "chunk_project_id_index_1",
                "unique": False
            }
        ]