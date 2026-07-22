from sqlalchemy import Index

from .mini_rag_base import SQLAlchmeyBase
from sqlalchemy import ForeignKey, String, column,Integer,DateTime, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
import uuid


class Asset(SQLAlchmeyBase):
    
    __tablename__='assets'
    
    
    asset_id=column(Integer,primary_kay=True,autoincrement=True)
    asset_uuid=column(UUID(True),default=uuid.uuid4,uniqe=True,nullable=False)
    
    asset_name=column(String,nullable=False)
    asset_type=column(String,nullable=False)
    asset_size=column(String,nullable=False)
    asset_config =column(JSONB,nullabale=True)
    
    
    asset_project_id=column(Integer,ForeignKey('projects.project_id'),nullable=False)
    
    project = relationship('project',back_populates='assets')
    
    __table_args__=(
        Index('ix_asset_project_id',asset_project_id),
        Index('ix_asset_type',asset_type),
    )
    
    created_at=column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at=column(DateTime(timezone=True),onupdate=func.now(),nullable=False)
    