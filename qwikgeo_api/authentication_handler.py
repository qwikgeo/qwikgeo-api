from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from qwikgeo_api import config

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        url_path_credentials = self.verify_api_key_param(request)
        header_credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)

        if url_path_credentials:
            if not self.verify_jwt(request.query_params['api_key']):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            user = jwt.decode(request.query_params['api_key'], config.SECRET_KEY, algorithms=["HS256"])
            return user['username']
        
        if header_credentials:
            if not header_credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(header_credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            user = jwt.decode(header_credentials.credentials, config.SECRET_KEY, algorithms=["HS256"])
            return user['username']
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_api_key_param(self, request: Request) -> bool:

        if 'api_key' in request.query_params:
            return {
                "scheme": "Bearer",
                "credentials": request.query_params['api_key']
            }
        else:
            return None

    def verify_jwt(self, jwt_token: str) -> bool:
        is_token_valid: bool = False

        try:
            payload = jwt.decode(jwt_token, config.SECRET_KEY, algorithms=["HS256"])  
        except:
            payload = None
        if payload:
            is_token_valid = True
        return is_token_valid