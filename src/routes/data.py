from fastapi import APIRouter,FastAPI,Depends,UploadFile,status
from fastapi.responses import JSONResponse
from helpers.config import get_settings,Settings
from controllers import DataController,ProjectController,ProcessController
from models import Response
from .schemes.data import ProccessRequest
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
    
    file_path,file_id=data_controller.generate_unique_filepath(original_file_name=file.filename,
                                                       project_id=project_id,
                                                       )
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
            "signal":Response.FILE_UPLOAD_SUCCED.value,
            "file_id":file_id
        }
    )
    
    
@data_router.post("/process/{project_id}")

async def process_endpoint(project_id:str,process_request:ProccessRequest):
    
    file_id=process_request.file_id
    chunk_size=process_request.chunck_size
    overlap_size=process_request.overlap_size
    
    process_controller=ProcessController(project_id)
    
    file_content=process_controller.get_file_content(file_id=file_id)
    
    file_chunks=process_controller.process_file_content(
        file_contnet=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        chunk_overlap=overlap_size
        )
    
    if file_chunks is None or len(file_chunks)==0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal":Response.FILE_PROCESSING_FALIED}
            )
    return file_chunks
