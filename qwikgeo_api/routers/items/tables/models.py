"""QwikGeo API - Tables - Models"""

from typing import Literal, List
from pydantic import BaseModel, Field

class Column(BaseModel):
    """Model for adding a column"""

    column_name: str
    column_type: Literal['text','integer','bigint','double precision','boolean','time','uuid']

class CreateTable(BaseModel):
    """Model for creating a table"""

    title: str = Field(
        title="The name of the dataset within GeoPortal."
    )
    tags: list=[]
    description: str = Field(
        title="A description about the dataset.",
        default=""
    )
    read_access_list: list=[]
    write_access_list: list=[]
    searchable: bool=True
    columns: List[Column]
    geometry_type: Literal['POINT','LINESTRING','POLYGON']
    srid: int=4326
