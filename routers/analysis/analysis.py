"""QwikGeo API - Analysis"""

from fastapi import APIRouter, BackgroundTasks, Request, Depends

import utilities
import routers.analysis.analysis_queries as analysis_queries
import routers.analysis.models as models

router = APIRouter()

analysis_processes = {}

@router.get(
    path="/status/{process_id}",
    # response_model=models.StatusResponseModel
)
def status(
    process_id: str,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Return status of an analysis.
    https://docs.qwikgeo.com/analysis/#analysis-status
    """

    if process_id not in analysis_processes:
        return {"status": "UNKNOWN", "error": "This process_id does not exist."}
    return analysis_processes[process_id]

@router.post(
    path="/buffer",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def buffer(
    info: models.BufferModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a buffer analysis.
    More information at https://docs.qwikgeo.com/analysis/#buffer
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.buffer,
        username=user_name,
        table=info.table,
        distance_in_kilometers=info.distance_in_kilometers,
        new_table_id=new_table_id,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/dissolve",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def dissolve(
    info: models.BaseAnalysisModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a dissolve analysis.
    More information at https://docs.qwikgeo.com/analysis/#dissolve
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.dissolve,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/dissolve_by_value",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def dissolve_by_value(
    info: models.DissolveByValueModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a dissolve by value analysis.
    More information at https://docs.qwikgeo.com/analysis/#dissolve-by-value
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.dissolve_by_value,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        column=info.column,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/square_grids",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def square_grids(
    info: models.GridModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a square grid analysis.
    More information at https://docs.qwikgeo.com/analysis/#square-grids
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.square_grids,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        grid_size_in_kilometers=info.grid_size_in_kilometers,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/hexagon_grids",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def hexagon_grids(
    info: models.GridModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a hexagon grid analysis.
    More information at https://docs.qwikgeo.com/analysis/#hexagon-grids
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.hexagon_grids,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        grid_size_in_kilometers=info.grid_size_in_kilometers,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/bounding_box",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def bounding_box(
    info: models.BaseAnalysisModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a bounding box analysis.
    More information at https://docs.qwikgeo.com/analysis/#bounding-box
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.bounding_box,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/k_means_cluster",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def k_means_cluster(
    info: models.KMeansModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a k means cluster analysis.
    More information at https://docs.qwikgeo.com/analysis/#k-means-cluster
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.k_means_cluster,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        number_of_clusters=info.number_of_clusters,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/center_of_each_polygon",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def center_of_each_polygon(
    info: models.BaseAnalysisModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a center of each polygon analysis.
    More information at https://docs.qwikgeo.com/analysis/#center-of-each-polygon
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.center_of_each_polygon,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/center_of_dataset",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def center_of_dataset(
    info: models.BaseAnalysisModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a center of dataset analysis.
    More information at https://docs.qwikgeo.com/analysis/#center-of-dataset
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.center_of_dataset,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/find_within_distance",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def find_within_distance(
    info: models.FindWithinDistanceModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a find within distance analysis.
    More information at https://docs.qwikgeo.com/analysis/#find-within-distance
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.find_within_distance,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        latitude=info.latitude,
        longitude=info.longitude,
        distance_in_kilometers=info.distance_in_kilometers,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/convex_hull",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def convex_hull(
    info: models.BaseAnalysisModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a convex hull analysis.
    More information at https://docs.qwikgeo.com/analysis/#convex-hull
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.convex_hull,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/aggregate_points_by_grids",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def aggregate_points_by_grids(
    info: models.AggregatePointsByGridsModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a aggregate points by grid analysis.
    More information at https://docs.qwikgeo.com/analysis/#aggregate-points-by-grid
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.aggregate_points_by_grids,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        distance_in_kilometers=info.distance_in_kilometers,
        grid_type=info.grid_type,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/aggregate_points_by_polygons",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def aggregate_points_by_polygons(
    info: models.PolygonsModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a aggregate points by polygons analysis.
    More information at https://docs.qwikgeo.com/analysis/#aggregate-points-by-polygons
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    await utilities.validate_table_access(
        table=info.polygons,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.aggregate_points_by_polygons,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        polygons=info.polygons,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/select_inside",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def select_inside(
    info: models.PolygonsModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a select inside analysis.
    More information at https://docs.qwikgeo.com/analysis/#select-inside
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    await utilities.validate_table_access(
        table=info.polygons,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.select_inside,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        polygons=info.polygons,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/select_outside",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def select_outside(
    info: models.PolygonsModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a select outside analysis.
    More information at https://docs.qwikgeo.com/analysis/#select-outside
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    await utilities.validate_table_access(
        table=info.polygons,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.select_outside,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        polygons=info.polygons,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/clip",
    response_model=models.BaseResponseModel,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def clip(
    info: models.PolygonsModel,
    request: Request,
    background_tasks: BackgroundTasks,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a clip analysis.
    More information at https://docs.qwikgeo.com/analysis/#clip
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    await utilities.validate_table_access(
        table=info.polygons,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/analysis/status/{process_id}"

    analysis_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        analysis_queries.clip,
        username=user_name,
        table=info.table,
        new_table_id=new_table_id,
        polygons=info.polygons,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }
