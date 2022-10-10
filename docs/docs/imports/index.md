# Imports Endpoints

| Method | URL | Description |
| ------ | --- | ----------- |
| `GET` | `/api/v1/imports/status/{process_id}` | [Import Status](#Import-Status)  |
| `POST` | `/api/v1/imports/arcgis_service` | [ArcGIS Service](#ArcGIS-Service)  |
| `POST` | `/api/v1/imports/geographic_data_from_geographic_file` | [Geographic Data From Geographic File](#Geographic-Data-From-Geographic-File)  |
| `POST` | `/api/v1/imports/geographic_data_from_csv` | [Geographic Data From CSV](#Geographic-Data-From-CSV)  |
| `POST` | `/api/v1/imports/point_data_from_csv` | [Point Data From CSV](#Point-Data-From-CSV)  |
| `POST` | `/api/v1/imports/geographic_data_from_json_file` | [Geographic Data From Json File](#Geographic-Data-From-Json-File)  |
| `POST` | `/api/v1/imports/point_data_from_json_file` | [Point Data From Json File ](#Point-Data-From-Json-File)  |
| `POST` | `/api/v1/imports/geographic_data_from_json_url` | [Geographic Data From Json URL](#Geographic-Data-From-Json-Url)  |
| `POST` | `/api/v1/imports/point_data_from_json_url` | [Point Data From Json URL](#Point-Data-From-Json-Url)  |
| `POST` | `/api/v1/imports/geojson_from_url` | [Geojson From URL](#Geojson-From-Url)  |


## Endpoint Description's

## Import Status
Any time an import is submitted it given a process_id to have the import run in the background using [FastAPI's Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/). To check the
status of an import, you can call this endpoint with the process_id.

### Example Call
```shell
https://api.qwikgeo.com/api/v1/imports/status/472e29dc-91a8-41d3-b05f-cee34006e3f7
```

### Example Output - Still Running
```json
{
    "status": "PENDING"
}
```

### Example Output - Complete
```json
{
    "status": "SUCCESS",
    "new_table_id": "shnxppipxrppsdkozuroilkubktfodibtqorhucjvxlcdrqyhh",
    "completion_time": "2022-07-06T19:33:17.950059",
    "run_time_in_seconds": 1.78599
}
```

### Example Output - Error
```json
{
    "status": "FAILURE",
    "error": "ERROR HERE",
    "completion_time": "2022-07-08T13:39:47.961389",
    "run_time_in_seconds": 0.040892
}
```

## ArcGIS Service

### Description
Import data from any `FeatureServer` or `MapServer` that allows for geojson as an output.

Example: Download a point dataset of Tennesse State Parks.

### Example Input
```json
{
    "url": "https://services5.arcgis.com/bPacKTm9cauMXVfn/ArcGIS/rest/services/TN_State_Parks_Points/FeatureServer/0",
    "database": "data"
}
```

### Example Output
```json
{
  "process_id": "c8d7b8d8-3e82-4f93-b441-55a5f51c4171",
  "url": "https://api.qwikgeo.com/api/v1/imports/status/c8d7b8d8-3e82-4f93-b441-55a5f51c4171"
}
```

## Geographic Data From Geographic File

### Description
Import geographic data from a file/files.

Example: Import geojson from [file](/data/states.geojson).

### Example Input
```json
{
    "database": "data",
    "files": "FILES IN MULTI PART FORM"
}
```

### Example Output
```json
{
  "process_id": "c8d7b8d8-3e82-4f93-b441-55a5f51c4171",
  "url": "https://api.qwikgeo.com/api/v1/imports/status/c8d7b8d8-3e82-4f93-b441-55a5f51c4171"
}
```

## Geographic Data From CSV

### Description
Import a csv [file](/data/state_data.csv) and join to a map already within the database based off a column.

Example: Uploading a csv with two columns `state_abbr` and `Number of Rest Stops`
and joining to the `states` map based off of the `state_abbr` column.

### Example Input
```json
{
  "database": "data",
  "map": "states",
  "map_column": "state_abbr",
  "map_columns": ["state_abbr"],
  "table_column": "state_abbr",
  "table_columns": ["state_abbr","Number of Rest Stops"],
  "files": "FILES IN MULTI PART FORM"
}
```

### Example Output
```json
{
  "process_id": "c8d7b8d8-3e82-4f93-b441-55a5f51c4171",
  "url": "https://api.qwikgeo.com/api/v1/imports/status/c8d7b8d8-3e82-4f93-b441-55a5f51c4171"
}
```

## Point Data From CSV

### Description
Import a csv file with latitude and longitude columns into database.

Example: A csv [file](/data/us-states-capitals.csv) with latitude and longitude columns for US Capitals.

### Example Input
```json
{
  "database": "data",
  "longitude": "longitude",
  "latitude": "latitude",
  "table_columns": ["name","description","latitude","longitude"],
  "files": "FILES IN MULTI PART FORM"
}
```

### Example Output
```json
{
  "process_id": "c8d7b8d8-3e82-4f93-b441-55a5f51c4171",
  "url": "https://api.qwikgeo.com/api/v1/imports/status/c8d7b8d8-3e82-4f93-b441-55a5f51c4171"
}
```

## Geographic Data From Json File

### Description
Import json from a file and join to a map already within the database based off a column.

Example: Import state date from a json [file](/data/states.json).

### Example Input
```json
{
  "database": "data",
  "map": "states",
  "map_column": "state_abbr",
  "map_columns": ["state_abbr"],
  "table_column": "code",
  "table_columns": ["state","slug","code","nickname"],
  "files": "FILES IN MULTI PART FORM"
}
```

### Example Output
```json
{
  "process_id": "c8d7b8d8-3e82-4f93-b441-55a5f51c4171",
  "url": "https://api.qwikgeo.com/api/v1/imports/status/c8d7b8d8-3e82-4f93-b441-55a5f51c4171"
}
```

## Point Data From Json File

### Description
Import point data from a Json file with latitude and longitude columns.

Example: A json [file](/data/cities.json) that contains cities for the entire world.

### Example Input
```json
{
  "database": "data",
  "longitude": "longitude",
  "latitude": "latitude",
  "table_columns": ["id","name","latitude","longitude","state_id","state_code","state_name","country_id","country_code","country_name","wikiDataId"],
  "files": "FILES IN MULTI PART FORM"
}
```

### Example Output
```json
{
  "process_id": "c8d7b8d8-3e82-4f93-b441-55a5f51c4171",
  "url": "https://api.qwikgeo.com/api/v1/imports/status/c8d7b8d8-3e82-4f93-b441-55a5f51c4171"
}
```

## Geographic Data From Json URL

### Description
Import json from a url and join to a map already within the database based off a column.

Example: Import state information from a gitlab url

### Example Input
```json
{
    "database": "data",
    "map_column": "state_abbr",
    "table_column": "code",
    "table_columns": [
        "state",
        "slug",
        "code",
        "nickname"
    ],
    "map": "states",
    "map_columns": [
        "state_abbr"
    ],
    "url": "https://raw.githubusercontent.com/CivilServiceUSA/us-states/master/data/states.json"
}
```

### Example Output
```json
{
  "process_id": "c8d7b8d8-3e82-4f93-b441-55a5f51c4171",
  "url": "https://api.qwikgeo.com/api/v1/imports/status/c8d7b8d8-3e82-4f93-b441-55a5f51c4171"
}
```

## Point Data From Json URL

### Description
Import json data from a url with latitude and longitude columns into database.

Example: Import state centroids from a gitlab url

### Example Input
```json
{
  "url": "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/states.json",
  "database": "data",
  "longitude": "longitude",
  "latitude": "latitude",
  "table_columns": ["id","name","latitude","longitude","state_code","country_id","country_code","country_name","type"],
  "files": "FILES IN MULTI PART FORM"
}
```

### Example Output
```json
{
  "process_id": "c8d7b8d8-3e82-4f93-b441-55a5f51c4171",
  "url": "https://api.qwikgeo.com/api/v1/imports/status/c8d7b8d8-3e82-4f93-b441-55a5f51c4171"
}
```

## Geojson From URL

### Description
Import geojson from any url.

Example: Input large earthquakes for the past month

### Example Input
```json
{
    "database": "data",
    "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"
}
```

### Example Output
```json
{
  "process_id": "c8d7b8d8-3e82-4f93-b441-55a5f51c4171",
  "url": "https://api.qwikgeo.com/api/v1/imports/status/c8d7b8d8-3e82-4f93-b441-55a5f51c4171"
}
```