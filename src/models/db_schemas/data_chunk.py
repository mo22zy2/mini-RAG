from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId # type: ignore



class DataChunk(BaseModel):
    
    _id: Optional[str] 
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order:int = Field(..., gt=0)
    chunk_project_id: ObjectId


    @validator("chunk_id")
    def validate_chunk_id(cls, v):
        if not v:
            raise ValueError("chunk_id must not be empty")

        if not v.isalnum():
            raise ValueError("chunk_id must be alphanumeric")

        return v

    @validator("project_id")
    def validate_project_id(cls, v):
        if not v:
            raise ValueError("project_id must not be empty")

        if not v.isalnum():
            raise ValueError("project_id must be alphanumeric")

        return v
    
    class Config:
        arbitrary_types_allowed = True