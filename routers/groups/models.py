"""QwikGeo API - Groups - Models"""

from typing import List
import uuid
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

import db_models

class Status(BaseModel):
    """Model for returning a request with a message"""

    message: str

class User(BaseModel):
    """Model for a username"""

    username: str

class Group(BaseModel):
    """Model for creating a group"""

    name: str
    group_users: List[User]

class ListGroup(BaseModel):
    """Model for listing a group"""

    group_id: uuid.UUID
    name: str

class Groups(BaseModel):
    """Model for listing groups"""

    groups: List[ListGroup]

Group_Pydantic = pydantic_model_creator(db_models.Group, name="Group")
