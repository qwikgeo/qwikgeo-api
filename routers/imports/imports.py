"""QwikGeo API - Imports"""

import os
import json
from typing import List
from fastapi import APIRouter, BackgroundTasks, Request, Form
from fastapi import File, UploadFile, Depends
import requests
import aiofiles

import utilities
import routers.imports.models as models

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 50  # 50 megabytes

router = APIRouter()

@router.get(
    path="/status/{process_id}",
    response_model=models.StatusResponseModel
)
def status(
    process_id: str,
    user_name: int=Depends(utilities.get_token_header)
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
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a new dataset from an arcgis service.
    https://docs.qwikgeo.com/imports/#arcgis-service
    """

    table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    utilities.import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.get_arcgis_data,
        url=info.url,
        token=info.token,
        table_id=table_id,
        process_id=process_id,
        username=user_name,
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

@router.post(
    path="/geographic_data_from_geographic_file",
    response_model=models.BaseResponseModel
)
async def import_geographic_data_from_geographic_file(
    request: Request,
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: str= Form(...),
    files: List[UploadFile] = File(...),
    user_name: int=Depends(utilities.get_token_header),
    tags: list=[],
    read_access_list: list=[],
    write_access_list: list=[],
    searchable: bool=True
):
    """
    Create a new dataset from a geographic file.
    https://docs.qwikgeo.com/imports/#geographic-data-from-geographic-file
    """

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    file_path = ""

    for file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{file.filename}"
            async with aiofiles.open(file_path, "wb") as file:
                while chunk := await file.read(DEFAULT_CHUNK_SIZE):
                    await file.write(chunk)
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")

            return {"message": "There was an error uploading the file(s)"}
        finally:
            await file.close()

    utilities.import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.upload_geographic_file,
        file_path=file_path,
        new_table_id=new_table_id,
        process_id=process_id,
        username=user_name,
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
    path="/geographic_data_from_csv",
    response_model=models.BaseResponseModel
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
    user_name: int=Depends(utilities.get_token_header),
    tags: list=[],
    read_access_list: list=[],
    write_access_list: list=[],
    searchable: bool=True
):
    """
    Create a new dataset from a csv file with geographic file.
    https://docs.qwikgeo.com/imports/#geographic-data-from-csv
    """

    await utilities.validate_table_access(
        table=map_name,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    file_path = ""

    for file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{file.filename}"
            async with aiofiles.open(file_path, "wb") as file:
                while chunk := await file.read(DEFAULT_CHUNK_SIZE):
                    await file.write(chunk)
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")

            return {"message": "There was an error uploading the file(s)"}
        finally:
            await file.close()

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
        username=user_name,
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
    response_model=models.BaseResponseModel
)
async def import_point_data_from_csv(
    request: Request,
    background_tasks: BackgroundTasks,
    latitude: str = Form(...),
    longitude: str = Form(...),
    table_columns: List = Form(...),
    files: List[UploadFile] = File(...),
    user_name: int=Depends(utilities.get_token_header),
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

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    file_path = ""

    for file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{file.filename}"
            async with aiofiles.open(file_path, "wb") as file:
                while chunk := await file.read(DEFAULT_CHUNK_SIZE):
                    await file.write(chunk)
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")

            return {"message": "There was an error uploading the file(s)"}


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
        username=user_name,
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
    response_model=models.BaseResponseModel
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
    user_name: int=Depends(utilities.get_token_header),
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

    await utilities.validate_table_access(
        table=map_name,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    file_path = ""

    for file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{file.filename}"
            async with aiofiles.open(file_path, "wb") as file:
                while chunk := await file.read(DEFAULT_CHUNK_SIZE):
                    await file.write(chunk)
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")

            return {"message": "There was an error uploading the file(s)"}
        finally:
            await file.close()

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
        username=user_name,
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
    response_model=models.BaseResponseModel
)
async def import_point_data_from_json_file(
    request: Request,
    background_tasks: BackgroundTasks,
    latitude: str = Form(...),
    longitude: str = Form(...),
    table_columns: List = Form(...),
    files: List[UploadFile] = File(...),
    user_name: int=Depends(utilities.get_token_header),
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

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    file_path = ""

    for file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{file.filename}"
            async with aiofiles.open(file_path, "wb") as file:
                while chunk := await file.read(DEFAULT_CHUNK_SIZE):
                    await file.write(chunk)
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")

            return {"message": "There was an error uploading the file(s)"}
        finally:
            await file.close()

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
        username=user_name,
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
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a new dataset from a json url with geographic file.
    https://docs.qwikgeo.com/imports/#geographic-data-from-json-url
    """

    await utilities.validate_table_access(
        table=info.map_name,
        user_name=user_name
    )

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    resp = requests.get(info.url, timeout=120)

    file_path = f"{os.getcwd()}/media/{new_table_id}.json"

    with open(f"{os.getcwd()}/media/{new_table_id}.json", "w") as my_file:
        my_file.write(resp.text)

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
        username=user_name,
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

@router.post(
    path="/point_data_from_json_url",
    response_model=models.BaseResponseModel
)
async def import_point_data_from_json_url(
    request: Request,
    background_tasks: BackgroundTasks,
    info: models.PointJsonUrl,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a new dataset from a json url with point data.
    https://docs.qwikgeo.com/imports/#point-data-from-json-url
    """

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    resp = requests.get(info.url, timeout=120)

    file_path = f"{os.getcwd()}/media/{new_table_id}.json"

    with open(f"{os.getcwd()}/media/{new_table_id}.json", "w") as my_file:
        my_file.write(resp.text)

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
        username=user_name,
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

@router.post("/geojson_from_url", response_model=models.BaseResponseModel)
async def import_geojson_from_url(
    request: Request,
    background_tasks: BackgroundTasks,
    info: models.GeojsonUrl,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a new dataset from a url with geojson data.
    https://docs.qwikgeo.com/imports/#geojson-from-url
    """

    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/imports/status/{process_id}"

    resp = requests.get(info.url, timeout=120)

    file_path = f"{os.getcwd()}/media/{new_table_id}.geojson"

    with open(f"{os.getcwd()}/media/{new_table_id}.geojson", "w") as my_file:
        my_file.write(resp.text)

    utilities.import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.upload_geographic_file,
        file_path=file_path,
        new_table_id=new_table_id,
        process_id=process_id,
        username=user_name,
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
