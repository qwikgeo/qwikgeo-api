"""QwikGeo API - Imports - Models"""

from pydantic import BaseModel, Field

class BaseResponseModel(BaseModel):
    """Model for base response"""

    process_id: str = Field(
        default="472e29dc-91a8-41d3-b05f-cee34006e3f7"
    )
    url: str = Field(
        default="https://api.qwikgeo.com/api/v1/analysis/status/472e29dc-91a8-41d3-b05f-cee34006e3f7"
    )

class ArcgisModel(BaseModel):
    """Model for importing arcgis data"""

    url: str = Field(
        title="The url that contains the service to download."
    )
    token: str = Field(
        default=None, title="If endpoint is authenticated, token will be used to download the service."
    )
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

class PointJsonUrl(BaseModel):
    """Model for importing json data with point data"""

    latitude: str
    longitude: str
    table_columns: list
    url: str
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

class GeographicJsonUrl(BaseModel):
    """Model for importing json data with geographic boundaries"""

    map_name: str
    map_column: str
    map_columns: list
    table_columns: list
    table_column: str
    url: str
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

class GeojsonUrl(BaseModel):
    """Model for importing geojson data from a url"""

    url: str
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
