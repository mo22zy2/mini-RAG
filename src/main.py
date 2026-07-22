from fastapi import FastAPI
from routes import base, data ,nlp
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.templates.template_parser import Template_Parser
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080", "http://localhost:8080"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)



async def startup_span():
    settings = get_settings()
    app.mongo_connection = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_connection[settings.MONGODB_DATABASE]
    
    llm_provider_factory = LLMProviderFactory(config=settings)
    vectordb_provider_factory= VectorDBProviderFactory(config=settings)
    
    app.generation_client=llm_provider_factory.create_provider(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    
    
    
    app.embedding_client=llm_provider_factory.create_provider(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE
)
# Vector DB app settings



    app.vectordb_client= vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    
    app.vectordb_client.connect()
    
    
    app.template_parser=Template_Parser(
        language=settings.DEFAULT_LANGUAGE,
        default_language=settings.DEFAULT_LANGUAGE
    )

async def shutdown_span():
    app.mongo_connection.close()
    app.vectordb_client.disconnect()
    
    
# app.router.lifespan.on_startup.append(startup_span)
# app.router.lifespan.on_shutdown.append(shutdown_span)

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)



app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)