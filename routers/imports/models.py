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
        default=None, title="The url that contains the service to download."
    )
    token: str = Field(
        default=None, title="If endpoint is authenticated, token will be used to download the service."
    )
    database: str = Field(
        default=None, title="Name of the database the table belongs to."
    )

class PointJsonUrl(BaseModel):
    database: str = Field(
        default=None, title="Name of the database the table belongs to."
    )
    latitude: str
    longitude: str
    table_columns: list
    url: str

class GeographicJsonUrl(BaseModel):
    database: str = Field(
        default=None, title="Name of the database the table belongs to."
    )
    map: str
    map_column: str
    map_columns: list
    table_columns: list
    table_column: str
    url: str

class GeojsonUrl(BaseModel):
    database: str = Field(
        default=None, title="Name of the database the table belongs to."
    )
    url: str