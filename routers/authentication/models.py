from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel

import db_models

class GoogleTokenAuthenticate(BaseModel):
    token: str

class Status(BaseModel):
    message: str

User_Pydantic = pydantic_model_creator(db_models.User, name="User", exclude=("password_hash", ))
UserIn_Pydantic = pydantic_model_creator(db_models.User, name="UserIn", exclude_readonly=True)
