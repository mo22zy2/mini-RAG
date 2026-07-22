from openai import BaseModel
from sqlalchemy import Index

from .mini_rag_base import SQLAlchmeyBase
from sqlalchemy import ForeignKey, String, column,Integer,DateTime, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
import uuid


class DataChunk(SQLAlchmeyBase):
    __tablename__='chunks'
    
    chunk_id=column(Integer,primary_kay=True,autoincrement=True)
    chunk_uuid=column(UUID(True),default=uuid.uuid4,uniqe=True,nullable=False)
        
    chunk_text=column(String,nullable=False)
    chunk_metadata=column(String,nullable=True)
    chunk_order=column(String,nullable=False)
    
    
    chunk_project_id=column(Integer,ForeignKey('projects.project_id'),nullable=False)
    chunk_asset_id = column(Integer,ForeignKey('assets.asset_id'),nullable=False)
    
    project=relationship("Project",back_populates='chunks')
    asset=relationship('Asset',back_populates='chunks')
    
    created_at=column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at=column(DateTime(timezone=True),onupdate=func.now(),nullable=False)
    
    
    __table_args__=(
        Index('ix_chunk_project_id',chunk_project_id),
        Index('ix_chunk_asset_id',chunk_asset_id),
    )
    
class RetrivedDocument(BaseModel):
    text:str
    score:float