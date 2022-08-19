from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel

import db_models

class Status(BaseModel):
    message: str

User_Pydantic = pydantic_model_creator(db_models.User, name="User")
UserIn_Pydantic = pydantic_model_creator(db_models.User, name="UserIn", exclude_readonly=True)