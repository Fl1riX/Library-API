from fastapi import HTTPException, status

class HTTPNotFound(HTTPException):
    """404"""
    def __init__(self, detail="Not found"):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = detail

class HTTPConflict(HTTPException):
    """409"""
    def __init__(self, detail="Conflict"):
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = detail

class HTTPBadRequest(HTTPException):
    """400"""
    def __init__(self, detail="Bad request"):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = detail
        
class HTTPNotAuthorized(HTTPException):
    """401"""
    
    def __init__(self, detail="Unauthorized"):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = detail
        self.headers = {"XXX-Authentificate": "Bearer"}
        












