from fastapi import FastAPI
from routes import base,data
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from helpers.config import get_settings


app = FastAPI()

async def startup_db_client():
    settings = get_settings()
    app.mongo_connection=AsyncIOMotorClient(settings.MONGO_URI)
    app.db_client=app.mongo_connection[settings.MONGO_DB_NAME]
    
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_connection.close()
    
app.include_router(base.base_router)
app.include_router(data.data_router)