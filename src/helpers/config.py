from pydantic_settings import BaseSettings,SettingsConfigDict
from typing import Optional

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


    GENERATION_MODEL_ID:Optional[str]=None
    EMBEDDING_MODEL_ID:Optional[str]=None
    EMBEDDING_MODEL_SIZE:Optional[int]=None


    INPUT_DEFAULT_MAX_CHARS:Optional[int]=None
    GENERATION_DEFAULT_MAX_TOKENS:Optional[int]=None
    GENERATION_DEFAULT_TEMPERATURE:float=0.8
    
    
    VECTOR_DB_BACKEND:str
    VECTOR_DB_PATH:str
    VECTOR_DB_DISTANCE_METHOD:str
    
    DEFAULT_LANGUAGE:str
    
    class Config:
        env_file='.env'
        
def get_settings():
    return Settings()