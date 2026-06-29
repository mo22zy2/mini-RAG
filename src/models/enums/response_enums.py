from enum import Enum

class Response(Enum):
    
    FILE_VALIDATED_SUCCESS="File validate successfully"
    FILE_TYPE_NOT_SUPPORTED="File Type is Not supported"
    FILE_SIZE_EXCEEDED="File Size is Bigger than 16Mb"
    FILE_UPLOAD_SUCCED="File upload Succeed"
    FILE_VALIDATED_FALIED="File validate Failed"
    FILE_PROCESSING_FALIED="File Processing Failed"
    FILE_PROCESSING_SUCCEED="File Processing SUCESS"
    PROCESSING_FAILED="File Processing Failed"
    NO_FILES_ERROR="Not Found Files"
    FILE_ID_ERROR="No File Record found with this ID"
