"""QwikGeo API - Imports"""

import os
import json
from typing import List
from fastapi import File, UploadFile, Depends, HTTPException, APIRouter, BackgroundTasks, Request, Form, status
import aiofiles
import aiohttp
from tortoise.expressions import Q

import qwikgeo_api.routers.imports.utilities as utilities
import qwikgeo_api.routers.imports.models as models
from qwikgeo_api import authentication_handler
from qwikgeo_api import utilities as qwikgeo_api_utilities

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 50  # 50 megabytes

router = APIRouter()

@router.get(
    path="/status/{process_id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "status": "SUCCESS",
                        "new_table_id": "shnxppipxrppsdkozuroilkubktfodibtqorhucjvxlcdrqyhh",
                        "completion_time": "2022-07-06T19:33:17.950059",
                        "run_time_in_seconds": 1.78599
                    }
                }
            }
        },
    }
)
def import_status(
    process_id: str,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Return status of an import.
    https://docs.qwikgeo.com/imports/#import-status
    """

    if process_id not in utilities.import_processes:
        return {"status": "UNKNOWN", "error": "This process_id does not exist."}
    return utilities.import_processes[process_id]

@router.post(
    path="/arcgis_service",
    response_model=models.BaseResponseModel
)
async def import_arcgis_service(
    info: models.ArcgisModel,
    request: Request,
    background_tasks: BackgroundTasks,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Create a new dataset from an arcgis service.
    https://docs.qwikgeo.com/imports/#arcgis-service
    """

    service_url = f"{info.url}?f=json"

    if info.token is not None:
        service_url += f"&token={info.token}"

    async with aiohttp.ClientSession() as session:

        try:

            async with session.get(service_url) as resp:

                if resp.status == 200:

                    data = await resp.json()

                    if 'error' in data:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=data['error']['message']
                        )

                    if 'layers' in data:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Please select a sublayer of {info.url}"
                        )
                    
                    if 'supportedExportFormats' not in data:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The following ArcGIS url does not have an export endpoint. Please provide a different url."
                        )
                    
                    if 'supportedExportFormats' in data:
                        if 'geojson' not in data['supportedExportFormats'].lower():
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="The following ArcGIS url does not allow an export of geojson. Qwikgeo API cannot fetch data from this endpoint."
                            )

                    table_id = qwikgeo_api_utilities.get_new_table_id()

                    process_id = qwikgeo_api_utilities.get_new_process_id()

                    process_url = str(request.base_url)

                    process_url += f"api/v1/imports/status/{process_id}"

                    utilities.import_processes[process_id] = {
                        "status": "PENDING"
                    }

                    background_tasks.add_task(
                        utilities.get_arcgis_data,
                        url=info.url,
                        token=info.token,
                        filter=info.filter,
                        table_id=table_id,
                        process_id=process_id,
                        username=username,
                        title=info.title,
                        description=info.description,
                        tags=info.tags,
                        read_access_list=info.read_access_list,
                        write_access_list=info.write_access_list,
                        searchable=info.searchable,
                        app=request.app
                    )

                    return {
                        "process_id": process_id,
                        "url": process_url
                    }
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid URL"
                )
        except aiohttp.client_exceptions.ClientConnectorError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL"
            ) from exc

@router.post(
    path="/geographic_data_from_geographic_file",
    response_model=models.BaseResponseModel,
    responses = {
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "There was an error uploading the file(s)"}
                }
            }
        }
    }
)
async def import_geographic_data_from_geographic_file(
    request: Request,
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: str= Form(...),
    files: List[UploadFile] = File(...),
    username: int=Depends(authentication_handler.JWTBearer()),
    tags: list=[],
    read_access_list: list=[],
    write_access_list: list=[],
    searchable: bool=True
):
    """
    Create a new dataset from a geographic file.
    https://docs.qwikgeo.com/imports/#geographic-data-from-geographic-file
    """

    new_table_id = qwikgeo_api_utilities.get_new_table_id()

    process_id = qwikgeo_api_utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    file_path = ""

    valid_file_type = False

    valid_file_types = ["geojson", "shp", "tab", "kml"]

    for new_file in files:
        if new_file.filename.split(".")[1] in valid_file_types:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{new_file.filename}"
            valid_file_type = True
    
    if valid_file_type is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Please upload a valid file type. {" ,".join(valid_file_types)}'
        )

    for new_file in files:
        try:
            write_file_path = f"{os.getcwd()}/media/{new_table_id}_{new_file.filename}"
            async with aiofiles.open(write_file_path, "wb") as file:
                while chunk := await new_file.read(DEFAULT_CHUNK_SIZE):
                    await file.write(chunk)
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There was an error uploading the file(s)"
            )

    utilities.import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.upload_geographic_file,
        file_path=file_path,
        new_table_id=new_table_id,
        process_id=process_id,
        username=username,
        title=title,
        description=description,
        tags=tags,
        read_access_list=read_access_list,
        write_access_list=write_access_list,
        searchable=searchable,
        app=request.app
    )

    return models.BaseResponseModel(
        process_id=process_id,
        url=process_url
    )

    

@router.post(
    path="/geographic_data_from_csv",
    response_model=models.BaseResponseModel,
    responses = {
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "There was an error uploading the file(s)"}
                }
            }
        }
    }
)
async def import_geographic_data_from_csv(
    request: Request,
    background_tasks: BackgroundTasks,
    map_name: str = Form(...),
    table_column: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    map_column: str = Form(...),
    map_columns: List = Form(...),
    table_columns: List = Form(...),
    files: List[UploadFile] = File(...),
    username: int=Depends(authentication_handler.JWTBearer()),
    tags: list=[],
    read_access_list: list=[],
    write_access_list: list=[],
    searchable: bool=True
):
    """
    Create a new dataset from a csv file with geographic file.
    https://docs.qwikgeo.com/imports/#geographic-data-from-csv
    """

    valid_file_type = False

    valid_file_types = ["csv"]

    for new_file in files:
        if new_file.filename.split(".")[1] in valid_file_types:
            valid_file_type = True
    
    if valid_file_type is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Please upload a valid csv file'
        )

    await qwikgeo_api_utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=map_name),
        username=username
    )

    new_table_id = qwikgeo_api_utilities.get_new_table_id()

    process_id = qwikgeo_api_utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    file_path = ""

    for new_file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{new_file.filename}"
            async with aiofiles.open(file_path, "wb") as file:
                while chunk := await new_file.read(DEFAULT_CHUNK_SIZE):
                    await file.write(chunk)
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There was an error uploading the file(s)"
            )

    utilities.import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.import_geographic_data_from_csv,
        file_path=file_path,
        new_table_id=new_table_id,
        map_column=map_column,
        table_column=table_column,
        map_columns=json.loads(map_columns[0]),
        table_columns=json.loads(table_columns[0]),
        map_name=map_name,
        process_id=process_id,
        app=request.app,
        username=username,
        title=title,
        description=description,
        tags=tags,
        read_access_list=read_access_list,
        write_access_list=write_access_list,
        searchable=searchable
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/point_data_from_csv",
    response_model=models.BaseResponseModel,
    responses = {
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "There was an error uploading the file(s)"}
                }
            }
        }
    }
)
async def import_point_data_from_csv(
    request: Request,
    background_tasks: BackgroundTasks,
    latitude: str = Form(...),
    longitude: str = Form(...),
    table_columns: List = Form(...),
    files: List[UploadFile] = File(...),
    username: int=Depends(authentication_handler.JWTBearer()),
    title: str = Form(...),
    description: str = Form(...),
    tags: list=[],
    read_access_list: list=[],
    write_access_list: list=[],
    searchable: bool=True
):
    """
    Create a new dataset from a csv file with point data.
    https://docs.qwikgeo.com/imports/#point-data-from-csv
    """

    valid_file_type = False

    valid_file_types = ["csv"]

    for new_file in files:
        if new_file.filename.split(".")[1] in valid_file_types:
            valid_file_type = True
    
    if valid_file_type is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Please upload a valid csv file'
        )

    new_table_id = qwikgeo_api_utilities.get_new_table_id()

    process_id = qwikgeo_api_utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    file_path = ""

    for new_file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{new_file.filename}"
            async with aiofiles.open(file_path, "wb") as file:
                while chunk := await new_file.read(DEFAULT_CHUNK_SIZE):
                    await file.write(chunk)
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There was an error uploading the file(s)"
            )


    utilities.import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.import_point_data_from_csv,
        file_path=file_path,
        new_table_id=new_table_id,
        latitude=latitude,
        longitude=longitude,
        table_columns=json.loads(table_columns[0]),
        process_id=process_id,
        app=request.app,
        username=username,
        title=title,
        description=description,
        tags=tags,
        read_access_list=read_access_list,
        write_access_list=write_access_list,
        searchable=searchable
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/geographic_data_from_json_file",
    response_model=models.BaseResponseModel,
    responses = {
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "There was an error uploading the file(s)"}
                }
            }
        }
    }
)
async def import_geographic_data_from_json_file(
    request: Request,
    background_tasks: BackgroundTasks,
    map_name: str = Form(...),
    map_column: str = Form(...),
    map_columns: List = Form(...),
    table_column: str = Form(...),
    table_columns: List = Form(...),
    files: List[UploadFile] = File(...),
    username: int=Depends(authentication_handler.JWTBearer()),
    title: str = Form(...),
    description: str = Form(...),
    tags: list=[],
    read_access_list: list=[],
    write_access_list: list=[],
    searchable: bool=True
):
    """
    Create a new dataset from a json file with geographic file.
    https://docs.qwikgeo.com/imports/#geographic-data-from-json-file
    """

    valid_file_type = False

    valid_file_types = ["json"]

    for new_file in files:
        if new_file.filename.split(".")[1] in valid_file_types:
            valid_file_type = True
    
    if valid_file_type is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Please upload a valid json file'
        )

    await qwikgeo_api_utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=map_name),
        username=username
    )

    new_table_id = qwikgeo_api_utilities.get_new_table_id()

    process_id = qwikgeo_api_utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    file_path = ""

    for new_file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{new_file.filename}"
            async with aiofiles.open(file_path, "wb") as file:
                while chunk := await new_file.read(DEFAULT_CHUNK_SIZE):
                    await file.write(chunk)
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There was an error uploading the file(s)"
            )

    utilities.import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.import_geographic_data_from_json_file,
        file_path=file_path,
        new_table_id=new_table_id,
        map_column=map_column,
        table_column=table_column,
        map_columns=json.loads(map_columns[0]),
        table_columns=json.loads(table_columns[0]),
        map_name=map_name,
        process_id=process_id,
        app=request.app,
        username=username,
        title=title,
        description=description,
        tags=tags,
        read_access_list=read_access_list,
        write_access_list=write_access_list,
        searchable=searchable
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/point_data_from_json_file",
    response_model=models.BaseResponseModel,
    responses = {
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "There was an error uploading the file(s)"}
                }
            }
        }
    }
)
async def import_point_data_from_json_file(
    request: Request,
    background_tasks: BackgroundTasks,
    latitude: str = Form(...),
    longitude: str = Form(...),
    table_columns: List = Form(...),
    files: List[UploadFile] = File(...),
    username: int=Depends(authentication_handler.JWTBearer()),
    title: str = Form(...),
    description: str = Form(...),
    tags: list=[],
    read_access_list: list=[],
    write_access_list: list=[],
    searchable: bool=True
):
    """
    Create a new dataset from a json file with point data.
    https://docs.qwikgeo.com/imports/#point-data-from-json-file
    """

    valid_file_type = False

    valid_file_types = ["json"]

    for new_file in files:
        if new_file.filename.split(".")[1] in valid_file_types:
            valid_file_type = True
    
    if valid_file_type is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Please upload a valid json file'
        )

    new_table_id = qwikgeo_api_utilities.get_new_table_id()

    process_id = qwikgeo_api_utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    file_path = ""

    for new_file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{new_file.filename}"
            async with aiofiles.open(file_path, "wb") as file:
                while chunk := await new_file.read(DEFAULT_CHUNK_SIZE):
                    await file.write(chunk)
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There was an error uploading the file(s)"
            )

    utilities.import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.import_point_data_from_json_file,
        file_path=file_path,
        new_table_id=new_table_id,
        latitude=latitude,
        longitude=longitude,
        table_columns=json.loads(table_columns[0]),
        process_id=process_id,
        app=request.app,
        username=username,
        title=title,
        description=description,
        tags=tags,
        read_access_list=read_access_list,
        write_access_list=write_access_list,
        searchable=searchable
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post(
    path="/geographic_data_from_json_url",
    response_model=models.BaseResponseModel
)
async def import_geographic_data_from_json_url(
    request: Request,
    background_tasks: BackgroundTasks,
    info: models.GeographicJsonUrl,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Create a new dataset from a json url with geographic file.
    https://docs.qwikgeo.com/imports/#geographic-data-from-json-url
    """

    await qwikgeo_api_utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=info.map_name),
        username=username
    )

    new_table_id = qwikgeo_api_utilities.get_new_table_id()

    process_id = qwikgeo_api_utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    async with aiohttp.ClientSession() as session:

        try:

            async with session.get(info.url) as resp:

                if resp.status == 200:

                    file_path = f"{os.getcwd()}/media/{new_table_id}.json"

                    with open(f"{os.getcwd()}/media/{new_table_id}.json", "w") as my_file:
                        my_file.write(await resp.text())

                    utilities.import_processes[process_id] = {
                        "status": "PENDING"
                    }

                    background_tasks.add_task(
                        utilities.import_geographic_data_from_json_file,
                        file_path=file_path,
                        new_table_id=new_table_id,
                        map_column=info.map_column,
                        table_column=info.table_column,
                        map_columns=info.map_columns,
                        table_columns=info.table_columns,
                        map_name=info.map_name,
                        process_id=process_id,
                        app=request.app,
                        username=username,
                        title=info.title,
                        description=info.description,
                        tags=info.tags,
                        read_access_list=info.read_access_list,
                        write_access_list=info.write_access_list,
                        searchable=info.searchable
                    )

                    return {
                        "process_id": process_id,
                        "url": process_url
                    }
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid URL"
                )
        except aiohttp.client_exceptions.ClientConnectorError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL"
            ) from exc

@router.post(
    path="/point_data_from_json_url",
    response_model=models.BaseResponseModel
)
async def import_point_data_from_json_url(
    request: Request,
    background_tasks: BackgroundTasks,
    info: models.PointJsonUrl,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Create a new dataset from a json url with point data.
    https://docs.qwikgeo.com/imports/#point-data-from-json-url
    """

    new_table_id = qwikgeo_api_utilities.get_new_table_id()

    process_id = qwikgeo_api_utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    async with aiohttp.ClientSession() as session:

        try:

            async with session.get(info.url) as resp:

                if resp.status == 200:

                    file_path = f"{os.getcwd()}/media/{new_table_id}.json"

                    with open(f"{os.getcwd()}/media/{new_table_id}.json", "w") as my_file:
                        my_file.write(await resp.text())

                    utilities.import_processes[process_id] = {
                        "status": "PENDING"
                    }

                    background_tasks.add_task(
                        utilities.import_point_data_from_json_file,
                        file_path=file_path,
                        new_table_id=new_table_id,
                        latitude=info.latitude,
                        longitude=info.longitude,
                        table_columns=info.table_columns,
                        process_id=process_id,
                        app=request.app,
                        username=username,
                        title=info.title,
                        description=info.description,
                        tags=info.tags,
                        read_access_list=info.read_access_list,
                        write_access_list=info.write_access_list,
                        searchable=info.searchable
                    )

                    return {
                        "process_id": process_id,
                        "url": process_url
                    }
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid URL"
                )
        except aiohttp.client_exceptions.ClientConnectorError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL"
            ) from exc

@router.post("/geojson_from_url", response_model=models.BaseResponseModel)
async def import_geojson_from_url(
    request: Request,
    background_tasks: BackgroundTasks,
    info: models.GeojsonUrl,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Create a new dataset from a url with geojson data.
    https://docs.qwikgeo.com/imports/#geojson-from-url
    """

    new_table_id = qwikgeo_api_utilities.get_new_table_id()

    process_id = qwikgeo_api_utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    async with aiohttp.ClientSession() as session:

        try:

            async with session.get(info.url) as resp:

                if resp.status_code == 200:

                    file_path = f"{os.getcwd()}/media/{new_table_id}.geojson"

                    with open(f"{os.getcwd()}/media/{new_table_id}.geojson", "w") as my_file:
                        my_file.write(await resp.text())

                    utilities.import_processes[process_id] = {
                        "status": "PENDING"
                    }

                    background_tasks.add_task(
                        utilities.upload_geographic_file,
                        file_path=file_path,
                        new_table_id=new_table_id,
                        process_id=process_id,
                        username=username,
                        title=info.title,
                        description=info.description,
                        tags=info.tags,
                        read_access_list=info.read_access_list,
                        write_access_list=info.write_access_list,
                        searchable=info.searchable,
                        app=request.app
                    )

                    return {
                        "process_id": process_id,
                        "url": process_url
                    }
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid URL"
                )
        except aiohttp.client_exceptions.ClientConnectorError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL"
            ) from exc