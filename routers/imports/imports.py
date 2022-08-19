import os
import json
from typing import List
from fastapi import APIRouter, BackgroundTasks, Request, Form
from fastapi import File, UploadFile, Depends
import requests

import utilities
import routers.imports.models as models

router = APIRouter()

import_processes = {}

@router.get("/status/{process_id}", tags=["Imports"])
def status(process_id: str, user_id: int=Depends(utilities.get_token_header)):
    if process_id not in import_processes:
        return {"status": "UNKNOWN", "error": "This process_id does not exist."}
    return import_processes[process_id]

@router.post("/arcgis_service/", tags=["Imports"], response_model=models.BaseResponseModel)
async def import_arcgis_service(info: models.ArcgisModel, request: Request, background_tasks: BackgroundTasks, user_id: int=Depends(utilities.get_token_header)):
    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/import/status/{process_id}"

    import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.get_arcgis_data,
        url=info.url,
        token=info.token,
        new_table_id=new_table_id,
        database=info.database,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post("/geographic_data_from_geographic_file/", tags=["Imports"], response_model=models.BaseResponseModel)
async def import_geographic_data_from_geographic_file(
        request: Request,
        background_tasks: BackgroundTasks,
        database: str = Form(...),
        files: List[UploadFile] = File(...),
        user_id: int=Depends(utilities.get_token_header)
    ):
    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/import/status/{process_id}"

    file_path = ""

    for file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{file.filename}"
            with open(file_path, 'wb') as f:
                [f.write(chunk) for chunk in iter(lambda: file.file.read(1000), b'')]
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")  

            return {"message": "There was an error uploading the file(s)"}
        finally:
            await file.close()

    import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.upload_geographic_file,
        file_path=file_path,
        new_table_id=new_table_id,
        database=database,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post("/geographic_data_from_csv/", tags=["Imports"], response_model=models.BaseResponseModel)
async def import_geographic_data_from_csv(
        request: Request,
        background_tasks: BackgroundTasks,
        database: str = Form(...),
        map: str = Form(...),
        map_column: str = Form(...),
        map_columns: List = Form(...),
        table_column: str = Form(...),
        table_columns: List = Form(...),
        files: List[UploadFile] = File(...),
        user_id: int=Depends(utilities.get_token_header)
    ):
    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/import/status/{process_id}"

    file_path = ""

    for file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{file.filename}"
            with open(file_path, 'wb') as f:
                [f.write(chunk) for chunk in iter(lambda: file.file.read(1000), b'')]
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")  

            return {"message": "There was an error uploading the file(s)"}
        finally:
            await file.close()

    import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.import_geographic_data_from_csv,
        file_path=file_path,
        new_table_id=new_table_id,
        database=database,
        map_column=map_column,
        table_column=table_column,
        map_columns=json.loads(map_columns[0]),
        table_columns=json.loads(table_columns[0]),
        map=map,
        process_id=process_id,
        app=request.app
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post("/point_data_from_csv/", tags=["Imports"], response_model=models.BaseResponseModel)
async def import_point_data_from_csv(
        request: Request,
        background_tasks: BackgroundTasks,
        database: str = Form(...),
        latitude: str = Form(...),
        longitude: str = Form(...),
        table_columns: List = Form(...),
        files: List[UploadFile] = File(...),
        user_id: int=Depends(utilities.get_token_header)
    ):
    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/import/status/{process_id}"

    file_path = ""

    for file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{file.filename}"
            with open(file_path, 'wb') as f:
                [f.write(chunk) for chunk in iter(lambda: file.file.read(1000), b'')]
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")  

            return {"message": "There was an error uploading the file(s)"}
        finally:
            await file.close()

    import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.import_point_data_from_csv,
        file_path=file_path,
        new_table_id=new_table_id,
        database=database,
        latitude=latitude,
        longitude=longitude,
        table_columns=json.loads(table_columns[0]),
        process_id=process_id,
        app=request.app
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post("/geographic_data_from_json_file/", tags=["Imports"], response_model=models.BaseResponseModel)
async def import_geographic_data_from_json_file(
        request: Request,
        background_tasks: BackgroundTasks,
        database: str = Form(...),
        map: str = Form(...),
        map_column: str = Form(...),
        map_columns: List = Form(...),
        table_column: str = Form(...),
        table_columns: List = Form(...),
        files: List[UploadFile] = File(...),
        user_id: int=Depends(utilities.get_token_header)
    ):
    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/import/status/{process_id}"

    file_path = ""

    for file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{file.filename}"
            with open(file_path, 'wb') as f:
                [f.write(chunk) for chunk in iter(lambda: file.file.read(1000), b'')]
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")  

            return {"message": "There was an error uploading the file(s)"}
        finally:
            await file.close()

    import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.import_geographic_data_from_json_file,
        file_path=file_path,
        new_table_id=new_table_id,
        database=database,
        map_column=map_column,
        table_column=table_column,
        map_columns=json.loads(map_columns[0]),
        table_columns=json.loads(table_columns[0]),
        map=map,
        process_id=process_id,
        app=request.app
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post("/point_data_from_json_file/", tags=["Imports"], response_model=models.BaseResponseModel)
async def import_point_data_from_json_file(
        request: Request,
        background_tasks: BackgroundTasks,
        database: str = Form(...),
        latitude: str = Form(...),
        longitude: str = Form(...),
        table_columns: List = Form(...),
        files: List[UploadFile] = File(...),
        user_id: int=Depends(utilities.get_token_header)
    ):
    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/import/status/{process_id}"

    file_path = ""

    for file in files:
        try:
            file_path = f"{os.getcwd()}/media/{new_table_id}_{file.filename}"
            with open(file_path, 'wb') as f:
                [f.write(chunk) for chunk in iter(lambda: file.file.read(1000), b'')]
        except Exception:
            media_directory = os.listdir(f"{os.getcwd()}/media/")
            for file in media_directory:
                if new_table_id in file:
                    os.remove(f"{os.getcwd()}/media/{file}")  

            return {"message": "There was an error uploading the file(s)"}
        finally:
            await file.close()

    import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.import_point_data_from_json_file,
        file_path=file_path,
        new_table_id=new_table_id,
        database=database,
        latitude=latitude,
        longitude=longitude,
        table_columns=json.loads(table_columns[0]),
        process_id=process_id,
        app=request.app
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post("/geographic_data_from_json_url/", tags=["Imports"], response_model=models.BaseResponseModel)
async def import_geographic_data_from_json_url(
        request: Request,
        background_tasks: BackgroundTasks,
        info: models.GeographicJsonUrl,
        user_id: int=Depends(utilities.get_token_header)
    ):
    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/import/status/{process_id}"

    resp = requests.get(info.url)

    file_path = f"{os.getcwd()}/media/{new_table_id}.json"

    with open(f"{os.getcwd()}/media/{new_table_id}.json", "w") as my_file:
        my_file.write(resp.text)

    import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.import_geographic_data_from_json_file,
        file_path=file_path,
        new_table_id=new_table_id,
        database=info.database,
        map_column=info.map_column,
        table_column=info.table_column,
        map_columns=info.map_columns,
        table_columns=info.table_columns,
        map=info.map,
        process_id=process_id,
        app=request.app
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post("/point_data_from_json_url/", tags=["Imports"], response_model=models.BaseResponseModel)
async def import_point_data_from_json_url(
        request: Request,
        background_tasks: BackgroundTasks,
        info: models.PointJsonUrl,
        user_id: int=Depends(utilities.get_token_header)
    ):
    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/import/status/{process_id}"

    resp = requests.get(info.url)

    file_path = f"{os.getcwd()}/media/{new_table_id}.json"

    with open(f"{os.getcwd()}/media/{new_table_id}.json", "w") as my_file:
        my_file.write(resp.text)

    import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.import_point_data_from_json_file,
        file_path=file_path,
        new_table_id=new_table_id,
        database=info.database,
        latitude=info.latitude,
        longitude=info.longitude,
        table_columns=info.table_columns,
        process_id=process_id,
        app=request.app
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post("/geojson_from_url/", tags=["Imports"], response_model=models.BaseResponseModel)
async def import_geojson_from_url(
        request: Request,
        background_tasks: BackgroundTasks,
        info: models.GeojsonUrl,
        user_id: int=Depends(utilities.get_token_header)
    ):
    new_table_id = utilities.get_new_table_id()

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/import/status/{process_id}"

    resp = requests.get(info.url)

    file_path = f"{os.getcwd()}/media/{new_table_id}.geojson"

    with open(f"{os.getcwd()}/media/{new_table_id}.geojson", "w") as my_file:
        my_file.write(resp.text)

    import_processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        utilities.upload_geographic_file,
        file_path=file_path,
        new_table_id=new_table_id,
        database=info.database,        
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }