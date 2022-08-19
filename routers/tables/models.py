from pydantic import BaseModel, Field
from typing import NamedTuple, Union, Literal, List, Optional
from typing_extensions import Annotated

class EditRowAttributes(BaseModel):
    
    table: str
    database: str
    gid: int
    values: object

LonField = Annotated[
    Union[float, int],
    Field(
        title='Coordinate longitude',
        gt=-180,
        lt=180,
    ),
]

LatField = Annotated[
    Union[float, int],
    Field(
        title='Coordinate latitude',
        gt=-90,
        lt=90,
    ),
]

class Coordinates(NamedTuple):
    lon: LonField
    lat: LatField
    
class Geojson(BaseModel):
    type: Literal['Point','MultiPoint','LineString','MultiLineString','Polygon','MultiPolygon']
    coordinates: Coordinates

class EditRowGeometry(BaseModel):
    
    table: str
    database: str
    gid: int
    geojson: Geojson

class AddColumn(BaseModel):
    
    table: str
    database: str
    column_name: str
    column_type: Literal['text','integer','bigint','double precision','booelan','time','uuid']

class DeleteColumn(BaseModel):
    
    table: str
    database: str
    column_name: str

class RowColumn(BaseModel):
    
    column_name: str
    value: str

class AddRow(BaseModel):
    
    table: str
    database: str
    columns: List[RowColumn]
    geojson: Geojson

class DeleteRow(BaseModel):
    
    table: str
    database: str
    gid: int

class Column(BaseModel):
    
    column_name: str
    column_type: Literal['text','integer','bigint','double precision','booelan','time','uuid']

class CreateTable(BaseModel):
    
    table: str
    database: str
    columns: List[Column]
    geometry_type: Literal['POINT','LINESTRING','POLYGON']
    srid: int=4326

class DeleteTable(BaseModel):
    
    table: str
    database: str

class AggregateModel(BaseModel):
    type: Literal['distinct', 'avg', 'count', 'sum', 'max', 'min']=None
    column: str
    group_column: Optional[str]
    group_method: Optional[str]


class StatisticsModel(BaseModel):
    table: str = Field(
        title="Name of the table to perform analysis on."
    )
    database: str = Field(
        title="Name of the database the table belongs to."
    )
    coordinates: str = Field(
        default=None, title="A list of coordinates to perfrom statistics in a certain geographical area."
    )
    geometry_type: Literal['POINT', 'LINESTRING', 'POLYGON']=None
    spatial_relationship: Literal['ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches']=None
    aggregate_columns: List[AggregateModel]
    filter: str=None

class BinsModel(BaseModel):
    table: str = Field(
        title="Name of the table to perform analysis on."
    )
    database: str = Field(
        title="Name of the database the table belongs to."
    )
    coordinates: str = Field(
        default=None, title="A list of coordinates to perfrom statistics in a certain geographical area."
    )
    geometry_type: Literal['POINT', 'LINESTRING', 'POLYGON']=None
    spatial_relationship: Literal['ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches']=None
    filter: str=None
    number_of_bins: int=10
    column: str

class NumericBreaksModel(BaseModel):
    table: str = Field(
        title="Name of the table to perform analysis on."
    )
    database: str = Field(
        title="Name of the database the table belongs to."
    )
    coordinates: str = Field(
        default=None, title="A list of coordinates to perfrom statistics in a certain geographical area."
    )
    geometry_type: Literal['POINT', 'LINESTRING', 'POLYGON']=None
    spatial_relationship: Literal['ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches']=None
    filter: str=None
    number_of_breaks: int
    column: str
    break_type: Literal['equal_interval', 'head_tail', 'quantile', 'jenk']

class BinModel(BaseModel):
    min: float
    max: float

class CustomBreaksModel(BaseModel):
    table: str = Field(
        title="Name of the table to perform analysis on."
    )
    database: str = Field(
        title="Name of the database the table belongs to."
    )
    coordinates: str = Field(
        default=None, title="A list of coordinates to perfrom statistics in a certain geographical area."
    )
    geometry_type: Literal['POINT', 'LINESTRING', 'POLYGON']=None
    spatial_relationship: Literal['ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches']=None
    filter: str=None
    column: str
    breaks: List[BinModel]
