"""QwikGeo API - Collections - Models"""

from typing import NamedTuple, Union, Literal, Optional, List
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

class Coordinates(NamedTuple):
    """Class for creating coordinates"""

    lon: LonField
    lat: LatField

class GeojsonGeometry(BaseModel):
    """Model for geojson geometry"""

    type: Literal['Point','MultiPoint','LineString','MultiLineString','Polygon','MultiPolygon']
    coordinates: Coordinates
    

class Geojson(BaseModel):
    """Model for geojson"""

    type: Literal['Feature']
    geometry: GeojsonGeometry
    properties: object
    id: Optional[int]

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