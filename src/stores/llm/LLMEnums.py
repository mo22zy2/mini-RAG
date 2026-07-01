from enum import Enum

class LLMType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    
    
class OpenAIEnums(Enum):
    SYSTEM="system"
    USER="user"
    ASSISTANT="assistant"
    
    
class CoHereEnums(Enum):
    SYSTEM="SYSTEM"
    USER="USER"
    ASSISTANT="ASSISTANT"