from .LLMEnums import LLMType
from .providers import OpenAIProvider, CoHereProvider


class LLMProviderFactory:
    
    def __init__(self,config:dict):
        self.config=config
        
    def create_provider(self,provider:str):
        
        if provider == LLMType.OPENAI.value:
            
            
            return OpenAIProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_generation_max_output_tokens=self.config.OPENAI_DEFAULT_GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.config.OPENAI_DEFAULT_GENERATION_TEMPERATURE,
                default_max_input_chars=self.config.OPENAI_DEFAULT_MAX_INPUT_CHARS
            )
        
        
        
        if provider == LLMType.COHERE.value:
            return CoHereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_generation_max_output_tokens=self.config.COHERE_DEFAULT_GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.config.COHERE_DEFAULT_GENERATION_TEMPERATURE,
                default_max_input_chars=self.config.COHERE_DEFAULT_MAX_INPUT_CHARS
            )
            
        
        return None
        