import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

import db_models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

SECRET_KEY = "asdasasfakjh324fds876921vdas7tfv1uqw76fasd87g2q"

async def get_token_header(token: str=Depends(oauth2_scheme)):
    user = jwt.decode(token, SECRET_KEY, algorithm='sha256')
    return user['id']

async def authenticate_user(username: str, password: str):
    user = await db_models.User.get(username=username)
    if not user:
        return False 
    if not user.verify_password(password):
        return False
    return user 