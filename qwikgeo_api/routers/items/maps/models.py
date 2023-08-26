"""QwikGeo API - Maps - Models"""

from enum import Enum
from typing import List
import uuid
from pydantic import BaseModel, Extra

class BasemapsEnum(str, Enum):
    Streets = 'streets'
    Outdoors = 'outdoors'
    Light = 'light'
    Dark = 'dark'
    Satellite = 'satellite'
    SatelliteStreets = 'satellite streets'
    Navigation = 'navigation'

class MapTypesEnum(str, Enum):
    user_data = 'user_data'
    vector = 'vector'
    xyz = 'xyz'
    wms = 'wms'
    wmts = 'wmts'
    esri = 'esri'

class GeometryTypesEnum(str, Enum):
    point = 'point'
    line = 'line'
    polygon = 'polygon'
    raster = 'raster'

class Layer(BaseModel):

    title: str
    description: str
    mapbox_name: str
    map_type: MapTypesEnum
    geometry_type: GeometryTypesEnum
    style: object=None
    paint: object=None
    layout: object=None
    fill_paint: object=None
    border_paint: object=None
    bounding_box: list

    class Config:
        extra = Extra.allow # or 'allow' str


class Map(BaseModel):

    pitch: int
    bearing: int
    basemap: BasemapsEnum
    bounding_box: list
    layers: List[Layer]
    read_access_list: list
    write_access_list: list
    notification_access_list: list
    username: str
    updated_username: str
    title: str
    description: str
    tags: list
    searchable: bool

    class Config:
        extra = Extra.allow # or 'allow' str