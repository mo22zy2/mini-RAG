from .BaseDataModel import BaseDataModel
from .db_schemas import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId # type: ignore

class ChunkModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection=self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
    
    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.dict())
        
        chunk._id = result.inserted_id
        
        return chunk
    
    
    async def get_chunk_by_id(self, chunk_id: str):
        record = await self.collection.find_one({
            "_id": chunk_id
        })
        
        if record is None:
            return None
        
        return DataChunk(**record)
    