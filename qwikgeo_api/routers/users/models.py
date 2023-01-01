"""QwikGeo API - Users - Models"""

from typing import List
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel

from qwikgeo_api import db_models

class Status(BaseModel):
    """Model for returning a request with a message"""

    message: str

class User(BaseModel):
    """Model for listing a user"""

    username: str
    first_name: str
    last_name: str
    photo_url: str=None

User_Pydantic = pydantic_model_creator(db_models.User, name="User", exclude=("password_hash", ))
UserIn_Pydantic = pydantic_model_creator(db_models.User, name="UserIn", exclude_readonly=True)
