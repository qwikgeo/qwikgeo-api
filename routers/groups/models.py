from typing import List
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
import uuid

import db_models

class User(BaseModel):

    username: str

class Group(BaseModel):

    name: str
    group_users: List[User]

class ListGroup(BaseModel):

    group_id: uuid.UUID
    name: str

class Groups(BaseModel):

    groups: List[ListGroup]

Group_Pydantic = pydantic_model_creator(db_models.Group, name="Group")
