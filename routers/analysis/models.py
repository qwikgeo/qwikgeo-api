"""QwikGeo API - Analysis - Models"""

from pydantic import BaseModel, Field

class BaseAnalysisModel(BaseModel):
    """Model for base analysis"""

    table: str = Field(
        default=None, title="Name of the table to perform analysis on."
    )

class StatusResponseModel(BaseModel):
    """Model for analysis response"""

    status: str = Field(
        default="SUCCESS"
    )
    new_table_id: str = Field(
        default="shnxppipxrppsdkozuroilkubktfodibtqorhucjvxlcdrqyhh",
        title="50 character new table_id in postgresql."
    )
    completion_time: str = Field(
        default="2022-07-06T19:33:17.950059"
    )
    run_time_in_seconds: float = Field(
        default=1.78599
    )

class BaseResponseModel(BaseModel):
    """Model for base analysis response"""

    process_id: str = Field(
        default="472e29dc-91a8-41d3-b05f-cee34006e3f7"
    )
    url: str = Field(
        default="https://api.qwikgeo.com/api/v1/analysis/status/472e29dc-91a8-41d3-b05f-cee34006e3f7"
    )

class BadResponseModel(BaseModel):
    """Model for bad analysis response"""

    status: str = Field(
        default="FAILURE"
    )
    completion_time: str = Field(
        default="2022-07-06T19:33:17.950059"
    )
    run_time_in_seconds: float = Field(
        default=1.78599
    )

class BufferModel(BaseModel):
    """Model for buffer analysis"""

    table: str = Field(
        default=None, title="Name of the table to perform analysis on."
    )
    distance_in_kilometers: float = Field(
        default=None, title="Size of buffer in kilometers."
    )

class DissolveByValueModel(BaseModel):
    """Model for dissolve by value analysis"""

    table: str = Field(
        default=None, title="Name of the table to perform analysis on."
    )
    column: str = Field(
        default=None, title="Column used to dissolve geometry."
    )

class GridModel(BaseModel):
    """Model for grid analysis"""

    table: str = Field(
        default=None, title="Name of the table to perform analysis on."
    )
    grid_size_in_kilometers: float = Field(
        default=None, title="Size of grids in kilometers."
    )

class KMeansModel(BaseModel):
    """Model for k means cluster analysis"""

    table: str = Field(
        default=None, title="Name of the table to perform analysis on."
    )
    number_of_clusters: int = Field(
        default=None, title="Number of clusters to group points together."
    )

class FindWithinDistanceModel(BaseModel):
    """Model for find within distance analysis"""

    table: str = Field(
        default=None, title="Name of the table to perform analysis on."
    )
    latitude: float = Field(
        default=None, title="Starting Latitude."
    )
    longitude: float = Field(
        default=None, title="Starting Latitude."
    )
    distance_in_kilometers: float = Field(
        default=None, title="Size to search in kilometers."
    )

class PolygonsModel(BaseModel):
    """Model for polygon based analyses"""

    table: str = Field(
        default=None, title="Name of the table to perform analysis on."
    )
    polygons: str = Field(
        default=None, title="Name of the table of polygons."
    )

class AggregatePointsByGridsModel(BaseModel):
    """Model for aggregate points by grid analysis"""

    table: str = Field(
        default=None, title="Name of the table to perform analysis on."
    )
    distance_in_kilometers: float = Field(
        default=None, title="Size to search in kilometers."
    )
    grid_type: str = Field(
        default=None, title="Type of grid to use."
    )
