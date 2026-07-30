from pydantic_settings import BaseSettings,SettingsConfigDict
from typing import List, Optional
from pathlib import Path

class Settings (BaseSettings):
    APP_NAME:str
    APP_VERSION:str
    FILE_ALLOWED_TYPES:list
    FILE_MAX_SIZE:int
    FILE_DEFAULT_CHUNK_SIZE:int
    
    
    MONGODB_URL:Optional[str]=None
    MONGODB_DATABASE:Optional[str]=None
    
    POSTGRES_USERNAME:str
    POSTGRES_PASSWORD:str
    POSTGRES_HOST:str
    POSTGRES_PORT:int
    POSTGRES_MAIN_DATABASE:str
    
    GENERATION_BACKEND:str
    EMBEDDING_BACKEND:str

    OPENAI_API_KEY:Optional[str]=None
    OPENAI_BASE_URL:Optional[str]=None


    COHERE_API_KEY:Optional[str]=None

    GENERATION_MODEL_ID_LIST:Optional[str]=None
    GENERATION_MODEL_ID:Optional[str]=None
    EMBEDDING_MODEL_ID:Optional[str]=None
    EMBEDDING_MODEL_SIZE:Optional[int]=None


    INPUT_DEFAULT_MAX_CHARS:Optional[int]=None
    GENERATION_DEFAULT_MAX_TOKENS:Optional[int]=None
    GENERATION_DEFAULT_TEMPERATURE:float=0.8
    
    
    VECTOR_DB_BACKEND_LITERAL:Optional[List[str]]=None
    VECTOR_DB_BACKEND:str
    VECTOR_DB_PATH:str
    VECTOR_DB_DISTANCE_METHOD:str
    VECTOR_DB_PGVEC_INDEX_THRESHOLD:int
    VECTOR_DB_INDEX_TYPE:str
    
    DEFAULT_LANGUAGE:str
    
    class Config:
        env_file=Path(__file__).parent.parent / '.env'
        
def get_settings():
    return Settings()