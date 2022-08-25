from pydantic import BaseModel, Field

class BaseResponseModel(BaseModel):
    process_id: str = Field(
        default="472e29dc-91a8-41d3-b05f-cee34006e3f7"
    )
    url: str = Field(
        default="http://127.0.0.1:8000/api/v1/analysis/status/472e29dc-91a8-41d3-b05f-cee34006e3f7"
    )

class ArcgisModel(BaseModel):
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
    latitude: str
    longitude: str
    table_columns: list
    url: str

class GeographicJsonUrl(BaseModel):
    map: str
    map_column: str
    map_columns: list
    table_columns: list
    table_column: str
    url: str

class GeojsonUrl(BaseModel):
    url: str