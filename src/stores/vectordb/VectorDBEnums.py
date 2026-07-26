from enum import Enum

class VectorDBType(Enum):
    QDRANT="QDRANT"
    
    
class DistanceMethodEnum(Enum):
    COSINE="cosine"
    DOT="dot"
    EUCLIDEAN="euclidean"
    
    
class PgVectorTableSchemaEnums(Enum):
    ID='id'
    TEXT='text'
    VECTOR='vector'
    CHUNK_ID='chunk_id'
    METADATA='metadata'
    _PREFIX='pgvector'
    
class PgVectorDistanceMethodEnum(Enum):
    COSINE="vector_cosine_ops"
    DOT="vector_l2_ops"
