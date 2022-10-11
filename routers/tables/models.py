"""QwikGeo API - Tables - Models"""

from typing import Literal, List, Optional
from pydantic import BaseModel, Field

class AddColumn(BaseModel):
    """Model for adding a column to a table"""

    column_name: str
    column_type: Literal['text','integer','bigint','double precision','boolean','time','uuid']

class DeleteColumn(BaseModel):
    """Model for deleting a column from a table"""

    column_name: str

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

class AggregateModel(BaseModel):
    """Model for aggregating data on a numerical column for a table"""

    type: Literal['distinct', 'avg', 'count', 'sum', 'max', 'min']=None
    column: str
    group_column: Optional[str]
    group_method: Optional[str]


class StatisticsModel(BaseModel):
    """Model for performing statistics on a numerical column for a table"""

    coordinates: str = Field(
        default=None, title="A list of coordinates to perform statistics in a certain geographical area."
    )
    geometry_type: Literal['POINT', 'LINESTRING', 'POLYGON']=None
    spatial_relationship: Literal['ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches']=None
    aggregate_columns: List[AggregateModel]
    filter: str=None

class BinsModel(BaseModel):
    """Model for creating bins on a numerical column for a table"""

    coordinates: str = Field(
        default=None, title="A list of coordinates to perform statistics in a certain geographical area."
    )
    geometry_type: Literal['POINT', 'LINESTRING', 'POLYGON']=None
    spatial_relationship: Literal['ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches']=None
    filter: str=None
    number_of_bins: int=10
    column: str

class NumericBreaksModel(BaseModel):
    """Model for creating numerical breaks on a numerical column for a table"""

    coordinates: str = Field(
        default=None, title="A list of coordinates to perform statistics in a certain geographical area."
    )
    geometry_type: Literal['POINT', 'LINESTRING', 'POLYGON']=None
    spatial_relationship: Literal['ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches']=None
    filter: str=None
    number_of_breaks: int
    column: str
    break_type: Literal['equal_interval', 'head_tail', 'quantile', 'jenk']

class BinModel(BaseModel):
    """Model for creating bins"""

    min: float
    max: float

class CustomBreaksModel(BaseModel):
    """Model for creating custom breaks on a numerical column for a table"""

    coordinates: str = Field(
        default=None, title="A list of coordinates to perform statistics in a certain geographical area."
    )
    geometry_type: Literal['POINT', 'LINESTRING', 'POLYGON']=None
    spatial_relationship: Literal['ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches']=None
    filter: str=None
    column: str
    breaks: List[BinModel]