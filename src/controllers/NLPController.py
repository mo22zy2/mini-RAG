from typing import List

from models.db_schemas.data_chunk import DataChunk
from stores.llm.LLMEnums import DocumentType

from .BaseController import BaseController
from models.db_schemas import Project

class NLPController(BaseController):
    
    def __init__(self, vectordb_client,generation_client,embedding_client):
        super().__init__()
        self.vectordb_client=vectordb_client
        self.generation_client=generation_client
        self.embedding_client=embedding_client
        
    def create_collection_name(self,project_id:str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self,project:Project):
        collection_name=self.create_collection_name(project_id=project.project_id)
        self.vectordb_cleint.delete_collection(collection_name)
    
    def get_vector_db_collection_info(self ,project:Project):
        collection_name=self.create_collection_name(project_id=project.project_id)
        collection_info=self.vectordb_cleint.get_collection_info(collection_name)
        
        return collection_info
    
    def index_into_vector_db(self,project:Project,
                             chunks:List[DataChunk],
                             chunk_ids:List[int],
                             do_reset:bool=False
                             ):
        collection_name=self.create_collection_name(project_id=project.project_id)
        texts=[c.chunk_text for c in chunks]
        metadata=[c.chunk_metadata for c in chunks]
        vectors=[
            self.embedding_client.embed_text(text=text,document_type=DocumentType.DOCUMENT.value)
            for text in texts
        ]
        
        _= self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
            
            
        )
        _= self.vectordb_client.insert_many(collection_name=collection_name,
                                            texts=texts,
                                            metadata= metadata,
                                            vector=vectors,
                                            record_ids=chunk_ids
                                            )
        
        
        return True
    
    