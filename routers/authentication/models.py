"""QwikGeo API - Authentication - Models"""

from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel

import db_models

class Login(BaseModel):
    """Model for creating a new user"""

    username: str
    password: str

class GoogleTokenAuthenticate(BaseModel):
    """Model for logging in with Google JWT"""

    token: str

class Status(BaseModel):
    """Model for returning a request with a message"""

    message: str

class TokenResponse(BaseModel):
    """Model for returning an JWT token"""

    access_token: str
    token_type: str="Bearer"

User_Pydantic = pydantic_model_creator(db_models.User, name="User", exclude=("password_hash", ))
UserIn_Pydantic = pydantic_model_creator(db_models.User, name="UserIn", exclude_readonly=True)
