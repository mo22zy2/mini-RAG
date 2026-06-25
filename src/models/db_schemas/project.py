from pydantic import BaseModel, Field, validator
from typing import Optional

class Project(BaseModel):
    _id: Optional[str] 
    project_id: str = Field(..., min_length=1)

    @validator("project_id")
    def validate_project_id(cls, v):
        if not v:
            raise ValueError("project_id must not be empty")

        if not v.isalnum():
            raise ValueError("project_id must be alphanumeric")

        return v
    
    class Config:
        arbitrary_types_allowed = True