from enum import Enum

class Response(Enum):
    
    FILE_VALIDATED_SUCCESS="File validate successfully"
    FILE_TYPE_NOT_SUPPORTED="File Type is Not supported"
    FILE_SIZE_EXCEEDED="File Size is Bigger than 16Mb"
    FILE_UPLOAD_SUCCED="File upload Succeed"
    FILE_VALIDATED_FALIED="File validate Failed"

