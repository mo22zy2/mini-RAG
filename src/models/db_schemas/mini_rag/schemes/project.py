from .mini_rag_base import SQLAlchmeyBase
from sqlalchemy import column,Integer,DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Project(SQLAlchmeyBase):
    
    __tablename__="projects"
    
    project_id=column(Integer,primary_kay=True,autoincrement=True)
    project_uuid=column(UUID(True),default=uuid.uuid4,uniqe=True,nullable=False)
    
    created_at=column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at=column(DateTime(timezone=True),onupdate=func.now(),nullable=False)
    