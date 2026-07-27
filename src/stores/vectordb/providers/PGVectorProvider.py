from ..VectortDBInterface import VectorDBInterface
from ..VectorDBEnums import (
    PgVectorDistanceMethodEnum,
    PgVectorIndexTypeEnums,
    PgVectorTableSchemaEnums,
    DistanceMethodEnum,
)
from typing import List
from models.db_schemas import RetrivedDocument
from sqlalchemy.sql import text as sql_text
import json, re
import logging


class PGVectorProvider(VectorDBInterface):

    # Maps the "friendly" distance method names to the pgvector operator
    # used in ORDER BY. Adjust the left-hand keys if your
    # PgVectorDistanceMethodEnum uses different values.
    _DISTANCE_OPERATORS = {
        DistanceMethodEnum.COSINE.value: "<=>",
        DistanceMethodEnum.DOT.value: "<#>",
        DistanceMethodEnum.L2.value: "<->",
    }

    def __init__(self, db_client, default_vector_size: int = 786, distance_method: str = None,index_threshold:int=100):
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.distance_method = distance_method or DistanceMethodEnum.COSINE.value
        self.pgvector_table_prefix = PgVectorTableSchemaEnums._PREFIX.value
        self.logger = logging.getLogger("uvicorn")
        self.default_index_name=lambda collection_name : f'{collection_name}_vector_idx'
        self.index_threshold=index_threshold

    # ------------------------------------------------------------------ #
    # helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _validate_collection_name(collection_name: str) -> str:
        """
        Table names can't be bound as SQL parameters, so we validate them
        strictly and then safely interpolate them (quoted) into the SQL
        string. This prevents SQL injection via the collection name.
        """
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", collection_name):
            raise ValueError(f"Invalid collection name: {collection_name!r}")
        return collection_name

    def _get_distance_operator(self) -> str:
        return self._DISTANCE_OPERATORS.get(self.distance_method, "<=>")

    # ------------------------------------------------------------------ #
    # lifecycle
    # ------------------------------------------------------------------ #
    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))

    async def disconnect(self):
        pass

    # ------------------------------------------------------------------ #
    # collection introspection
    # ------------------------------------------------------------------ #
    async def is_collection_existed(self, collection_name: str) -> bool:
        async with self.db_client() as session:
            async with session.begin():
                list_tbl = sql_text(
                    "SELECT tablename FROM pg_tables WHERE tablename = :collection_name"
                )
                results = await session.execute(list_tbl, {"collection_name": collection_name})
                record = results.first()

        return record is not None
    
    async def list_all_collections(self) -> List:
        async with self.db_client() as session:
            async with session.begin():
                list_tbl = sql_text(
                    "SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix"
                )
                results = await session.execute(
                    list_tbl, {"prefix": f"{self.pgvector_table_prefix}%"}
                )
                records = results.scalars().all()
        return records

    async def get_collection_info(self, collection_name: str):
        collection_name = self._validate_collection_name(collection_name)

        async with self.db_client() as session:
            async with session.begin():
                table_info_sql = sql_text(
                    """
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes
                    FROM pg_tables
                    WHERE tablename = :collection_name
                    """
                )
                count_sql = sql_text(f'SELECT COUNT(*) FROM "{collection_name}"')

                table_info = await session.execute(
                    table_info_sql, {"collection_name": collection_name}
                )
                table_data = table_info.fetchone()

                if table_data is None:
                    return None

                record_count = await session.execute(count_sql)
                count = record_count.scalar_one()

                return {
                    "table_info": dict(table_data._mapping),
                    "record_count": count,
                }

    # ------------------------------------------------------------------ #
    # collection management
    # ------------------------------------------------------------------ #
    async def delete_collection(self, collection_name: str):
        collection_name = self._validate_collection_name(collection_name)

        async with self.db_client() as session:
            async with session.begin():
                self.logger.info(f"Deleting collection: {collection_name}")
                delete_sql = sql_text(f'DROP TABLE IF EXISTS "{collection_name}"')
                await session.execute(delete_sql)

        return True

    async def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        do_reset: bool = False,
    ):
        if do_reset:
            await self.delete_collection(collection_name)

        if await self.is_collection_existed(collection_name):
            return False

        collection_name = self._validate_collection_name(collection_name)

        self.logger.info(f"Creating collection: {collection_name}")

        create_sql = sql_text(f"""
            CREATE TABLE "{collection_name}" (
                {PgVectorTableSchemaEnums.ID.value} BIGSERIAL PRIMARY KEY,
                {PgVectorTableSchemaEnums.TEXT.value} TEXT,
                {PgVectorTableSchemaEnums.VECTOR.value} VECTOR({embedding_size}),
                {PgVectorTableSchemaEnums.METADATA.value} JSONB DEFAULT '{{}}',
                {PgVectorTableSchemaEnums.CHUNK_ID.value} INTEGER,
                FOREIGN KEY ({PgVectorTableSchemaEnums.CHUNK_ID.value})
                    REFERENCES chunks(chunk_id)
            )
        """)

        async with self.db_client() as session:
            async with session.begin():
                await session.execute(create_sql)

        return True

    # ------------------------------------------------------------------ #
    # inserts
    # ------------------------------------------------------------------ #
    async def is_index_exsisted(self,collection_name:str)->str:
        index_name=self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                check_sql=sql_text(
                    '''
                    SELECT 1
                    FROM pg_indexes
                    WHERE tablename= :collection_name
                    AND indexname=:index_name
                    '''
                )
                
                results= await session.execute(check_sql,{
                    'collection_name':collection_name,
                    'index_name':index_name
                })
                
                return bool(results.scalar_one_or_none())
            
    async def create_vector_index(self,collection_name:str,index_type:str=PgVectorIndexTypeEnums.HNSW.value):
        is_index_exsisted=await self.is_index_exsisted(collection_name=collection_name)
        if is_index_exsisted:
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                count_sql=sql_text(f'SELECT COUNT (*) FROM {collection_name}')
        
        
    
    
    
    
    
    
    
    
    
    async def insert_one(
        self,
        collection_name,
        vector,
        text,
        metadata=None,
        record_id=None,
    ):
        if not await self.is_collection_existed(collection_name):
            self.logger.error(f"Collection '{collection_name}' does not exist.")
            return False

        if record_id is None:
            self.logger.error("chunk_id is required.")
            return False

        collection_name = self._validate_collection_name(collection_name)

        vector = "[" + ",".join(map(str, vector)) + "]"
        metadata = json.dumps(metadata or {})

        insert_sql = sql_text(f"""
            INSERT INTO "{collection_name}"
            (
                {PgVectorTableSchemaEnums.TEXT.value},
                {PgVectorTableSchemaEnums.VECTOR.value},
                {PgVectorTableSchemaEnums.METADATA.value},
                {PgVectorTableSchemaEnums.CHUNK_ID.value}
            )
            VALUES
            (
                :text,
                :vector,
                :metadata,
                :chunk_id
            )
        """)

        async with self.db_client() as session:
            async with session.begin():
                await session.execute(
                    insert_sql,
                    {
                        "text": text,
                        "vector": vector,
                        "metadata": metadata,
                        "chunk_id": record_id,
                    },
                )

        return True

    async def insert_many(
        self,
        collection_name,
        vectors,
        texts,
        metadata=None,
        record_ids=None,
        batch_size=50,
    ):
        if not await self.is_collection_existed(collection_name):
            self.logger.error(f"Collection '{collection_name}' does not exist.")
            return False

        if record_ids is None:
            self.logger.error("chunk_id is required.")
            return False

        if len(vectors) != len(record_ids):
            self.logger.error(f"Invalid data items for collection: {collection_name}")
            return False

        collection_name = self._validate_collection_name(collection_name)

        # Normalize metadata to a per-record list of JSON strings,
        # rather than turning the whole thing into a single JSON blob.
        if not metadata or len(metadata) == 0:
            metadata = [{}] * len(texts)
        metadata = [json.dumps(m or {}) for m in metadata]

        batch_insert_sql = sql_text(f"""
            INSERT INTO "{collection_name}"
            (
                {PgVectorTableSchemaEnums.TEXT.value},
                {PgVectorTableSchemaEnums.VECTOR.value},
                {PgVectorTableSchemaEnums.METADATA.value},
                {PgVectorTableSchemaEnums.CHUNK_ID.value}
            )
            VALUES
            (
                :text,
                :vector,
                :metadata,
                :chunk_id
            )
        """)

        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i + batch_size]
                    batch_vectors = vectors[i:i + batch_size]
                    batch_metadata = metadata[i:i + batch_size]
                    batch_record_ids = record_ids[i:i + batch_size]

                    values = []
                    for _text, _vector, _metadata, _record_id in zip(
                        batch_texts, batch_vectors, batch_metadata, batch_record_ids
                    ):
                        values.append({
                            "text": _text,
                            "vector": "[" + ",".join(map(str, _vector)) + "]",
                            "metadata": _metadata,
                            "chunk_id": _record_id,
                        })

                    await session.execute(batch_insert_sql, values)

        return True

    # ------------------------------------------------------------------ #
    # search
    # ------------------------------------------------------------------ #
    async def search_by_vector(self, collection_name, vector, limit):
        if not await self.is_collection_existed(collection_name):
            self.logger.error(f"Collection '{collection_name}' does not exist.")
            return False

        collection_name = self._validate_collection_name(collection_name)
        operator = self._get_distance_operator()

        vector = "[" + ",".join(map(str, vector)) + "]"

        async with self.db_client() as session:
            async with session.begin():
                search_sql = sql_text(f"""
                    SELECT
                        {PgVectorTableSchemaEnums.TEXT.value} AS text,
                        1 - ({PgVectorTableSchemaEnums.VECTOR.value} {operator} :vector) AS score
                    FROM "{collection_name}"
                    ORDER BY score DESC
                    LIMIT :limit
                """)

                results = await session.execute(
                    search_sql, {"vector": vector, "limit": limit}
                )
                records = results.fetchall()

                return [
                    RetrivedDocument(text=record.text, score=record.score)
                    for record in records
                ]