from typing import List

from models.db_schemas.data_chunk import DataChunk
from stores.llm.LLMEnums import DocumentType

from .BaseController import BaseController
from models.db_schemas import Project
import json
class NLPController(BaseController):
    
    def __init__(self, vectordb_client,generation_client,embedding_client,template_parser):
        super().__init__()
        self.vectordb_client=vectordb_client
        self.generation_client=generation_client
        self.embedding_client=embedding_client
        self.template_parser=template_parser
        
        
    def create_collection_name(self,project_id:str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self,project:Project):
        collection_name=self.create_collection_name(project_id=project.project_id)
        self.vectordb_client.delete_collection(collection_name)
    
    def get_vector_db_collection_info(self ,project:Project):
        collection_name=self.create_collection_name(project_id=project.project_id)
        collection_info=self.vectordb_client.get_collection_info(collection_name)
        
        return json.loads(
            json.dumps(collection_info,default=lambda x: x.__dict__)
        )
    
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
    
    
    def search_vector_db_collection(self,project:Project,text:str,limit:int =5):
        
        collection_name=self.create_collection_name(project_id=project.project_id)
        vector = self.embedding_client.embed_text(
        text=text,
        document_type=DocumentType.QUERY.value
        )
        
        if not vector or len(vector)==0:
            return False
        
        results= self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )
        
        if not results:
            return False
        
        return json.loads(
            json.dumps(results,default=lambda x: x.__dict__)
        )
        
        
    def answer_rag_question(self,project:Project,query:str,limit:int =5):
        
        answer , full_prompt , chat_history=None,None,None
        
        collection_name=self.create_collection_name(project_id=project.project_id)
        retrived_document= self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit
        )
        
        if not retrived_document or len(retrived_document)==0:
            return answer , full_prompt , chat_history
        
        
        
        system_prompt=self.template_parser.get("rag","system_prompt")
        
        
        documnets_prompts="\n".join([
                self.template_parser.get("rag","document_prompt",{
                    "doc_num":idx+1,
                    "chunk_text":doc["text"]
                })
            for idx,doc in enumerate(retrived_document)
        ])
        
        footer_prompt=self.template_parser.get("rag","footer_prompt")
        
        chat_history = [
        self.generation_client.construct_prompt(
            prompt=system_prompt,
            role=self.generation_client.enums.SYSTEM.value,
                        )
                    ]

        full_prompt = "\n\n".join([
            documnets_prompts,
            f"## User Question:\n{query}",
            footer_prompt,
        ])
            
        answer=self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )
        
        return answer , full_prompt , chat_history
        