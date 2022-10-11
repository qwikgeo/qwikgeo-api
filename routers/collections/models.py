"""QwikGeo API - Collections - Models"""

from typing import NamedTuple, Union, Literal, Optional
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
