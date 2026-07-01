from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums
import cohere # type: ignore
import logging


class CoHereProvider(LLMInterface):
    
    
    def __init__(self,api_key:str ,
                 default_max_input_chars:int=1000,
                 default_max_output_tokens:int=1000,
                 default_temperature:float=0.1):
        
        self.api_key = api_key

        self.default_max_input_chars = default_max_input_chars
        self.default_max_output_tokens = default_max_output_tokens
        self.default_temperature = default_temperature
        self.generation_model_id=None
        self.embedding_model_id=None
        self.embedding_size=None
        self.logger = logging.getLogger(__name__) #Get a logger for this class (specific to this module)
         
         
        self.client=cohere.Client(self.api_key)
         
         
    def set_generation_model(self, model_id: str):
        self.generation_model = model_id
    
    def set_embedding_model(self, model_id: str):
        self.embedding_model = model_id
        
        
    def process_text(self,text:str):
            
            if len(text) > self.default_max_input_chars:
               
                self.logger.warning(f"Input text exceeds the maximum allowed characters ({self.default_max_input_chars}). It will be truncated.")
                
                text = text[:self.default_max_input_chars].strip()  # Truncate and remove leading/trailing whitespace
            
            return text        

    
    def generate_text(self, prompt: str,
                      chat_history: list = None,
                      max_output_tokens: int = None,
                      temperature: float = None):
        
        if not self.client:
                self.logger.error("OpenAI client is not initialized.")
                return None
            
        if not self.generation_model_id:
            self.logger.error("Generation model ID is not set. Please set it using set_generation_model().")
            return None
        
        response = self.client.chat.completions.create(
                model=self.generation_model_id,
                chat_history=chat_history,
                message=self.process_text(prompt),
            )
        
        
    def embed_text(self, text: str, document_type: str = None):
        # Implement the text embedding logic using the Cohere API
        pass
    
    def construct_prompt(self,prompt:str,role:str):
            return {
                "role":role,
                "text":self.process_text(prompt)
            }
