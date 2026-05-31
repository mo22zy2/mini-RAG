from fastapi import APIRouter,FastAPI,Depends,UploadFile,status
from fastapi.responses import JSONResponse
from helpers.config import get_settings,Settings
from controllers import DataController,ProjectController
from models import Response
import os
import aiofiles
import logging

logger=logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1,data"]
)

@data_router.post("/upload/{project_id}")

async def upload_data(project_id:str,
                      file:UploadFile,
                      app_settings:Settings =Depends(get_settings)):
    data_controller=DataController()
    isValid,response_signal = data_controller.validate_upload_file(file=file)
    
    if not isValid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal":response_signal}
        )
        
    project_dir_path=ProjectController().get_project_path(project_id=project_id)
    
    os.makedirs(project_dir_path, exist_ok=True)
    
    file_path=data_controller.generate_unique_filename(original_file_name=file.filename,
                                                       project_id=project_id)
    try:
        
        async with aiofiles.open(file_path,"wb")as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
                
    except Exception as e:
        logger.error(f"Error while uploading file : {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal":Response.FILE_VALIDATED_FALIED}
        )
        
        
    return JSONResponse(
        content={
            "signal":Response.FILE_UPLOAD_SUCCED.value
        }
    )

