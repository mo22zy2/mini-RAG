from enum import Enum

class VectorDBType(Enum):
    QDRANT="QDRANT"
    
    
class DistanceMethodEnum(Enum):
    COSINE="cosine"
    DOT="dot"
    EUCLIDEAN="euclidean"