from bson import ObjectId  # type: ignore
from pydantic import BaseModel, Field, field_validator, ConfigDict # type: ignore
from typing import Optional


class Project(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str = Field(..., min_length=1)

    @field_validator("id", mode="before")
    @classmethod
    def convert_object_id(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value

    @field_validator("project_id")
    
    @classmethod
    def validate_project_id(cls, value: str):
        if not value:
            raise ValueError("project_id must not be empty")

        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric")

        return value
    
    
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[
                    ("project_id", 1)
                ],
                "name": "project_id_index_1",
                "unique": True
            }
        ]