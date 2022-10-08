"""QwikGeo API - Items - Models"""

from typing import NamedTuple, Union, Literal, List, Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated

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

class EditRowAttributes(BaseModel):
    """Model for editing row attributes"""

    table: str
    database: str
    gid: int
    values: object

class Coordinates(NamedTuple):
    """Class for creating coordinates"""

    lon: LonField
    lat: LatField

class Geojson(BaseModel):
    """Model for geojson"""

    type: Literal['Point','MultiPoint','LineString','MultiLineString','Polygon','MultiPolygon']
    coordinates: Coordinates

class EditRowGeometry(BaseModel):
    """Model for editing row geometry"""

    table: str
    database: str
    gid: int
    geojson: Geojson

class AddColumn(BaseModel):
    """Model for adding a column to a table"""

    table: str
    database: str
    column_name: str
    column_type: Literal['text','integer','bigint','double precision','boolean','time','uuid']

class DeleteColumn(BaseModel):
    """Model for deleting a column from a table"""

    table: str
    database: str
    column_name: str

class RowColumn(BaseModel):
    """Model for a row in a table"""

    column_name: str
    value: str

class AddRow(BaseModel):
    """Model for adding a row to a table"""

    table: str
    database: str
    columns: List[RowColumn]
    geojson: Geojson

class DeleteRow(BaseModel):
    """Model for deleting a row for a table"""

    table: str
    database: str
    gid: int

class Column(BaseModel):
    """Model for adding a column"""

    column_name: str
    column_type: Literal['text','integer','bigint','double precision','boolean','time','uuid']

class CreateTable(BaseModel):
    """Model for creating a table"""

    table: str
    database: str
    columns: List[Column]
    geometry_type: Literal['POINT','LINESTRING','POLYGON']
    srid: int=4326

class DeleteTable(BaseModel):
    """Model for deleting a table"""

    table: str
    database: str

class AggregateModel(BaseModel):
    """Model for aggregating data on a numerical column for a table"""

    type: Literal['distinct', 'avg', 'count', 'sum', 'max', 'min']=None
    column: str
    group_column: Optional[str]
    group_method: Optional[str]


class StatisticsModel(BaseModel):
    """Model for performing statistics on a numerical column for a table"""

    table: str = Field(
        title="Name of the table to perform analysis on."
    )
    database: str = Field(
        title="Name of the database the table belongs to."
    )
    coordinates: str = Field(
        default=None, title="A list of coordinates to perform statistics in a certain geographical area."
    )
    geometry_type: Literal['POINT', 'LINESTRING', 'POLYGON']=None
    spatial_relationship: Literal['ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches']=None
    aggregate_columns: List[AggregateModel]
    filter: str=None

class BinsModel(BaseModel):
    """Model for creating bins on a numerical column for a table"""

    table: str = Field(
        title="Name of the table to perform analysis on."
    )
    database: str = Field(
        title="Name of the database the table belongs to."
    )
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

    table: str = Field(
        title="Name of the table to perform analysis on."
    )
    database: str = Field(
        title="Name of the database the table belongs to."
    )
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

    table: str = Field(
        title="Name of the table to perform analysis on."
    )
    database: str = Field(
        title="Name of the database the table belongs to."
    )
    coordinates: str = Field(
        default=None, title="A list of coordinates to perform statistics in a certain geographical area."
    )
    geometry_type: Literal['POINT', 'LINESTRING', 'POLYGON']=None
    spatial_relationship: Literal['ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches']=None
    filter: str=None
    column: str
    breaks: List[BinModel]
