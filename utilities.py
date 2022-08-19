import os
import json
import jwt
import random
import re
import string
import uuid
import datetime
import subprocess
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, FastAPI
from pygeofilter.backends.sql import to_sql_where
from pygeofilter.parsers.ecql import parse
import aiohttp
import pandas as pd

import db_models
import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

SECRET_KEY = "asdasasfakjh324fds876921vdas7tfv1uqw76fasd87g2q"

async def get_token_header(token: str=Depends(oauth2_scheme)):
    user = jwt.decode(token, SECRET_KEY, algorithm='sha256')
    return user['id']

async def authenticate_user(username: str, password: str):
    user = await db_models.User.get(username=username)
    if not user:
        return False 
    if not user.verify_password(password):
        return False
    return user

async def get_tile(database: str, scheme: str, table: str, z: int,
    x: int, y: int, fields: str, cql_filter: str, db_settings: object, app: FastAPI) -> bytes:
    """
    Method to return vector tile from database.
    """

    cachefile = f'{os.getcwd()}/cache/{database}_{scheme}_{table}/{z}/{x}/{y}'

    if os.path.exists(cachefile):
        return '', True

    pool = app.state.databases[f'{database}_pool']

    async with pool.acquire() as con:


        sql_field_query = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table}'
        AND column_name != 'geom';
        """

        field_mapping = {}

        db_fields = await con.fetch(sql_field_query)

        for field in db_fields:
            field_mapping[field['column_name']] = field['column_name']

        if fields is None:
            field_list = ""

            for field in db_fields:
                column = field['column_name']
                field_list += f', "{column}"'
        else:
            field_list = f',"{fields}"'

        sql_vector_query = f"""
        SELECT ST_AsMVT(tile, '{scheme}.{table}', 4096)
        FROM (
            WITH
            bounds AS (
                SELECT ST_TileEnvelope({z}, {x}, {y}) as geom
            )
            SELECT
                st_asmvtgeom(
                    ST_Transform(t.geom, 3857)
                    ,bounds.geom
                ) AS mvtgeom {field_list}
            FROM {scheme}.{table} as t, bounds
            WHERE ST_Intersects(
                ST_Transform(t.geom, 4326),
                ST_Transform(bounds.geom, 4326)
            ) 	

        """
        if cql_filter:
            ast = parse(cql_filter)
            where_statement = to_sql_where(ast, field_mapping)
            sql_vector_query += f" AND {where_statement}"

        sql_vector_query += f"LIMIT {db_settings['max_features_per_tile']}) as tile"

        tile = await con.fetchval(sql_vector_query)

        if fields is None and cql_filter is None and db_settings['cache_age_in_seconds'] > 0:

            cachefile_dir = f'{os.getcwd()}/cache/{database}_{scheme}_{table}/{z}/{x}'

            if not os.path.exists(cachefile_dir):
                try:
                    os.makedirs(cachefile_dir)
                except OSError:
                    pass

            with open(cachefile, "wb") as file:
                file.write(tile)
                file.close()

        return tile, False

async def get_tables_metadata(app: FastAPI) -> list:
    """
    Method used to get tables metadata.
    """
    tables_metadata = []

    for database in config.DATABASES.items():

        pool = app.state.databases[f'{database[0]}_pool']

        async with pool.acquire() as con:
            tables_query = """
            SELECT schemaname, tablename
            FROM pg_catalog.pg_tables
            WHERE schemaname not in ('pg_catalog','information_schema', 'topology')
            AND tablename != 'spatial_ref_sys'; 
            """
            tables = await con.fetch(tables_query)
            for table in tables:
                tables_metadata.append(
                    {
                        "name" : table['tablename'],
                        "schema" : table['schemaname'],
                        "type" : "table",
                        "id" : f"{table['schemaname']}.{table['tablename']}",
                        "database" : config.DATABASES[database[0]]['database']
                    }
                )

    return tables_metadata

async def get_table_columns(database: str, scheme: str, table: str, app: FastAPI) -> list:
    """
    Method used to retrieve columns for a given table.
    """

    pool = app.state.databases[f'{database}_pool']

    async with pool.acquire() as con:
        column_query = f"""
        SELECT
            jsonb_agg(
                jsonb_build_object(
                    'name', attname,
                    'type', format_type(atttypid, null),
                    'description', col_description(attrelid, attnum)
                )
            )
        FROM pg_attribute
        WHERE attnum>0
        AND attrelid=format('%I.%I', '{scheme}', '{table}')::regclass
        """
        columns = await con.fetchval(column_query)

        return json.loads(columns)

async def get_table_geometry_type(database: str, scheme: str, table: str, app: FastAPI) -> list:
    """
    Method used to retrieve the geometry type for a given table.
    """

    pool = app.state.databases[f'{database}_pool']

    async with pool.acquire() as con:
        geometry_query = f"""
        SELECT ST_GeometryType(geom) as geom_type
        FROM {scheme}.{table}
        """
        geometry_type = await con.fetchval(geometry_query)

        return geometry_type

async def get_table_center(database: str, scheme: str, table: str, app: FastAPI) -> list:
    """
    Method used to retrieve the table center for a given table.
    """

    pool = app.state.databases[f'{database}_pool']

    async with pool.acquire() as con:
        query = f"""
        SELECT ST_X(ST_Centroid(ST_Union(geom))) as x,
        ST_Y(ST_Centroid(ST_Union(geom))) as y
        FROM {scheme}.{table}
        """
        center = await con.fetch(query)
        
        return [center[0][0],center[0][1]]

async def get_table_bounds(database: str, scheme: str, table: str, app: FastAPI) -> list:
    """
    Method used to retrieve the bounds for a given table.
    """

    pool = app.state.databases[f'{database}_pool']

    async with pool.acquire() as con:
        query = f"""
        SELECT ARRAY[
            ST_XMin(ST_Union(geom)),
            ST_YMin(ST_Union(geom)),
            ST_XMax(ST_Union(geom)),
            ST_YMax(ST_Union(geom))
        ]
        FROM {scheme}.{table}
        """
        extent = await con.fetchval(query)

        return extent

async def generate_where_clause(info: object, con, no_where: bool=False) -> str:
    """
    Method to generate where clause

    """
    
    query = ""

    if info.filter:
        sql_field_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{info.table}'
            AND column_name != 'geom';
        """

        db_fields = await con.fetch(sql_field_query)

        field_mapping = {}  

        for field in db_fields:
            field_mapping[field['column_name']] = field['column_name']

        ast = parse(info.filter)
        filter = to_sql_where(ast, field_mapping)

        if no_where is False:
            query += f" WHERE "
        else:
            query += f" AND "
        query += f" {filter}"
    
    if info.coordinates and info.geometry_type and info.spatial_relationship:
        if info.filter:
            query += " AND "
        else:
            if no_where is False:
                query += " WHERE "
        if info.geometry_type == 'POLYGON':
            query += f"{info.spatial_relationship}(ST_GeomFromText('{info.geometry_type}(({info.coordinates}))',4326) ,{info.table}.geom)"
        else:
            query += f"{info.spatial_relationship}(ST_GeomFromText('{info.geometry_type}({info.coordinates})',4326) ,{info.table}.geom)"

    return query

def get_new_table_id() -> str:
    """
    Method to return a new table id
    """
    letters = string.ascii_lowercase

    return ''.join(random.choice(letters) for i in range(50))

def get_new_process_id() -> str:
    """
    Method to return a new process id
    """

    return str(uuid.uuid4())

def remove_bad_characters(string: str) -> str:
    regex = re.compile('[^a-zA-Z0-9_]')
    return regex.sub('_', string).lower()

async def upload_csv_to_db_with_latitude_and_longitude(file_path: str, new_table_id: str, database: str,
    latitude: str, longitude: str, table_columns: list, app: FastAPI):
    """
    Method to upload data from from a csv file with latitude and longitude columns into db.

    """

    pd.options.display.max_rows = 10

    df = pd.read_csv(file_path)

    columns = ""

    formatted_table_columns = ""

    for col in table_columns:
        formatted_table_columns += f"{remove_bad_characters(col)},"

    formatted_table_columns = formatted_table_columns[:-1]

    create_table_sql = f"CREATE TABLE {new_table_id} ("

    for name, dtype in df.dtypes.iteritems():
        columns += f"{remove_bad_characters(name)},"
        create_table_sql += f'"{remove_bad_characters(name)}"'
        if dtype == "object" or dtype == "datetime64":
            create_table_sql += " text,"
        if dtype == "int64":
            create_table_sql += " integer,"            
        if dtype == "float64":
            create_table_sql += " double precision,"

    create_table_sql = create_table_sql[:-1]

    columns = columns[:-1]
    
    create_table_sql += ");"

    pool = app.state.databases[f'{database}_pool']

    async with pool.acquire() as con:
        await con.fetch(f"""DROP TABLE IF EXISTS "{new_table_id}";""")

        await con.fetch(create_table_sql)

        insert_sql = f"""COPY {new_table_id}({columns})
        FROM '{file_path}'
        DELIMITER ','
        CSV HEADER;"""

        await con.fetch(insert_sql)

        add_geom_sql = f"""
            SELECT AddGeometryColumn ('public','{new_table_id}','geom',4326,'POINT',2);                
        """

        await con.fetch(add_geom_sql)

        update_geom_sql = f"""
            UPDATE "{new_table_id}" 
            SET geom = ST_SetSRID(ST_MakePoint({longitude},{latitude}), 4326);
        """

        await con.fetch(update_geom_sql)

        delete_bad_geom_sql = f"""
            DELETE FROM "{new_table_id}" WHERE geom IS NULL;
        """

        await con.fetch(delete_bad_geom_sql)

async def upload_csv_to_db_with_geographic_data(file_path: str, new_table_id: str, database: str,
    map: str, map_column: str, table_column: str, table_columns: list, map_columns: list, app: FastAPI):
    """
    Method to upload data from from a csv file with geographic data into db.

    """

    pd.options.display.max_rows = 10

    df = pd.read_csv(file_path)

    columns = ""

    formatted_table_columns = ""

    formatted_map_columns = ""

    for col in table_columns:
        if col not in map_columns:
            formatted_table_columns += f"a.{remove_bad_characters(col)},"
    
    for column in map_columns:
        formatted_map_columns += f"b.{remove_bad_characters(column)},"

    create_table_sql = f"CREATE TABLE {new_table_id}_temp ("

    for name, dtype in df.dtypes.iteritems():
        columns += f"{remove_bad_characters(name)},"
        create_table_sql += f'"{remove_bad_characters(name)}"'
        if dtype == "object" or dtype == "datetime64":
            create_table_sql += " text,"
        if dtype == "int64":
            create_table_sql += " integer,"            
        if dtype == "float64":
            create_table_sql += " double precision,"

    create_table_sql = create_table_sql[:-1]
    columns = columns[:-1]
    
    create_table_sql += ");"

    pool = app.state.databases[f'{database}_pool']

    async with pool.acquire() as con:
        await con.fetch(f"""DROP TABLE IF EXISTS "{new_table_id}_temp";""")

        await con.fetch(create_table_sql)

        insert_sql = f"""COPY {new_table_id}_temp({columns})
        FROM '{file_path}'
        DELIMITER ','
        CSV HEADER;"""

        await con.fetch(insert_sql)

        join_sql = f"""CREATE TABLE "{new_table_id}" AS
            SELECT {formatted_table_columns} {formatted_map_columns} geom
            FROM "{new_table_id}_temp" as a
            LEFT JOIN "{map}" as b
            ON a."{table_column}" = b."{map_column}";
        """

        await con.fetch(join_sql)

        await con.fetch(f"""DROP TABLE IF EXISTS "{new_table_id}_temp";""")

async def get_arcgis_data(url: str, new_table_id: str, process_id: str, database: str, token: str=None):
    """
    Method get arcgis data from a given url and load it into a database.
    """

    start = datetime.datetime.now()

    try:
        service_url = f"{url}?f=json"

        if token is not None:
            service_url += f"&token={token}"
        
        async with aiohttp.ClientSession() as session:

            async with session.get(service_url) as resp:

                data = await resp.json()

                max_number_of_features_per_query = data['maxRecordCount']

                feature_stats_url = f"{url}/query?where=1%3D1&returnGeometry=false&returnIdsOnly=true&f=json"

                async with session.get(feature_stats_url) as feature_resp:

                    data = await feature_resp.text()

                    data = json.loads(data)

                    object_ids = data['objectIds']

                    number_of_features = len(data['objectIds'])

                    if number_of_features <= max_number_of_features_per_query:

                        async with session.get(f"{url}/query?where=1=1&outFields=*&returnGeometry=true&geometryPrecision=6&outSR=4326&f=geojson") as resp:

                            data = await resp.json()  
                            
                            with open(f'{new_table_id}.geojson', 'w') as json_file:
                                json.dump(data, json_file)
                            
                            load_geographic_data_to_server(
                                table_id=new_table_id,
                                file_path=f'{new_table_id}.geojson',
                                database=database
                            )

                    else:
                        start_counter = 0
                        
                        feature_collection = {
                            "type": "FeatureCollection",           
                            "features": []
                        }

                        for x in range( start_counter, number_of_features, max_number_of_features_per_query ):
                            ids_requested = object_ids[x: x + max_number_of_features_per_query ]
                            payload = { 'f': 'geojson', 'where': '1=1', 
                                'objectIds': str( ids_requested )[1:-1], 'outSR': '4326',  
                                'returnGeometry': 'true', 'outFields': '*', 
                                'geometryPrecision': '4'}

                            async with session.post( f"{url}/query", data=payload ) as resp:

                                data = await resp.text()

                                data = json.loads(data)

                                if 'error' in data:
                                    print(data['error'])

                                feature_collection['features'] += data['features']

                        with open(f'{new_table_id}.geojson', 'w') as json_file:
                            json.dump(feature_collection, json_file)
                        
                        load_geographic_data_to_server(
                            table_id=new_table_id,
                            file_path=f'{new_table_id}.geojson',
                            database=database
                        )
                os.remove(f'{new_table_id}.geojson')
                imports.import_processes[process_id]['status'] = "SUCCESS"
                imports.import_processes[process_id]['new_table_id'] = new_table_id
                imports.import_processes[process_id]['completion_time'] = datetime.datetime.now()
                imports.import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        if os.path.exists(f'{new_table_id}.geojson'):
            os.remove(f'{new_table_id}.geojson')
        imports.import_processes[process_id]['status'] = "FAILURE"
        imports.import_processes[process_id]['error'] = str(error)
        imports.import_processes[process_id]['completion_time'] = datetime.datetime.now()
        imports.import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def upload_geographic_file(file_path: str, new_table_id: str, process_id: str, database: str):
    """
    Method to upload data from geographic file.

    """

    start = datetime.datetime.now()

    try:
        load_geographic_data_to_server(
            table_id=new_table_id,
            file_path=file_path,
            database=database
        )
        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")  
        imports.import_processes[process_id]['status'] = "SUCCESS"
        imports.import_processes[process_id]['new_table_id'] = new_table_id
        imports.import_processes[process_id]['completion_time'] = datetime.datetime.now()
        imports.import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")  
        imports.import_processes[process_id]['status'] = "FAILURE"
        imports.import_processes[process_id]['error'] = str(error)
        imports.import_processes[process_id]['completion_time'] = datetime.datetime.now()
        imports.import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def import_geographic_data_from_csv(file_path: str, new_table_id: str, process_id: str, database: str,
    map: str, map_column: str, table_column: str, table_columns: list, map_columns: list, app: FastAPI):
    """
    Method to upload data from from a csv file with geographic data.

    """

    start = datetime.datetime.now()

    try:
        await upload_csv_to_db_with_geographic_data(
            file_path=file_path,
            new_table_id=new_table_id,
            database=database,
            map=map,
            map_column=map_column,
            table_column=table_column,
            table_columns=table_columns,
            map_columns=map_columns,
            app=app
        )

        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")  
        imports.import_processes[process_id]['status'] = "SUCCESS"
        imports.import_processes[process_id]['new_table_id'] = new_table_id
        imports.import_processes[process_id]['completion_time'] = datetime.datetime.now()
        imports.import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")  
        imports.import_processes[process_id]['status'] = "FAILURE"
        imports.import_processes[process_id]['error'] = str(error)
        imports.import_processes[process_id]['completion_time'] = datetime.datetime.now()
        imports.import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def import_point_data_from_csv(file_path: str, new_table_id: str, process_id: str, database: str,
    latitude: str, longitude: str, table_columns: list, app: FastAPI):
    """
    Method to upload data from csv with lat lng columns.

    """

    start = datetime.datetime.now()

    try:
        await upload_csv_to_db_with_latitude_and_longitude(
            file_path=file_path,
            new_table_id=new_table_id,
            database=database,
            latitude=latitude,
            longitude=longitude,
            table_columns=table_columns,
            app=app
        )

        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")  

        imports.import_processes[process_id]['status'] = "SUCCESS"
        imports.import_processes[process_id]['new_table_id'] = new_table_id
        imports.import_processes[process_id]['completion_time'] = datetime.datetime.now()
        imports.import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")  
        imports.import_processes[process_id]['status'] = "FAILURE"
        imports.import_processes[process_id]['error'] = str(error)
        imports.import_processes[process_id]['completion_time'] = datetime.datetime.now()
        imports.import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def import_point_data_from_json_file(file_path: str, new_table_id: str, process_id: str, database: str,
    latitude: str, longitude: str, table_columns: list, app: FastAPI):
    """
    Method to upload data from csv with lat lng columns.

    """

    start = datetime.datetime.now()

    try:
        df = pd.read_json(file_path)
        
        df.to_csv(f"{os.getcwd()}/media/{new_table_id}.csv", index=False, sep=',', encoding="utf-8")

        await upload_csv_to_db_with_latitude_and_longitude(
            file_path=f"{os.getcwd()}/media/{new_table_id}.csv",
            new_table_id=new_table_id,
            database=database,
            latitude=latitude,
            longitude=longitude,
            table_columns=table_columns,
            app=app
        )

        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")  
        imports.import_processes[process_id]['status'] = "SUCCESS"
        imports.import_processes[process_id]['new_table_id'] = new_table_id
        imports.import_processes[process_id]['completion_time'] = datetime.datetime.now()
        imports.import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")  
        imports.import_processes[process_id]['status'] = "FAILURE"
        imports.import_processes[process_id]['error'] = str(error)
        imports.import_processes[process_id]['completion_time'] = datetime.datetime.now()
        imports.import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def import_geographic_data_from_json_file(file_path: str, new_table_id: str, process_id: str, database: str,
    map: str, map_column: str, table_column: str, table_columns: list, map_columns: list, app: FastAPI):
    """
    Method to upload data from from a json file with geographic data.

    """

    start = datetime.datetime.now()

    try:
        df = pd.read_json(file_path)
        
        df.to_csv(f"{os.getcwd()}/media/{new_table_id}.csv", index=False, sep=',', encoding="utf-8")

        await upload_csv_to_db_with_geographic_data(
            file_path=f"{os.getcwd()}/media/{new_table_id}.csv",
            new_table_id=new_table_id,
            database=database,
            map=map,
            map_column=map_column,
            table_column=table_column,
            table_columns=table_columns,
            map_columns=map_columns,
            app=app
        )

        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")  
        imports.import_processes[process_id]['status'] = "SUCCESS"
        imports.import_processes[process_id]['new_table_id'] = new_table_id
        imports.import_processes[process_id]['completion_time'] = datetime.datetime.now()
        imports.import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")  
        imports.import_processes[process_id]['status'] = "FAILURE"
        imports.import_processes[process_id]['error'] = str(error)
        imports.import_processes[process_id]['completion_time'] = datetime.datetime.now()
        imports.import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

def load_geographic_data_to_server(table_id: str, file_path: str, database: object):

    db = config.DATABASES[database]
    host = db['host']
    username = db['username']
    password = db['password']
    database = db['database']
    subprocess.call(f'ogr2ogr -f "PostgreSQL" "PG:host={host} user={username} dbname={database} password={password}" "{file_path}" -lco GEOMETRY_NAME=geom -lco FID=gid -lco PRECISION=no -nln {table_id} -overwrite', shell=True)

async def get_table_columns(table: str, database: str, new_table_name: str=None, app: FastAPI) -> list:
    """
    Method to return a list of columns for a table.
    """
    
    pool = app.state.databases[f'{database}_pool']

    async with pool.acquire() as con:


        sql_field_query = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table}'
        AND column_name != 'geom';
        """

        db_fields = await con.fetch(sql_field_query)

        fields = []

        for field in db_fields:
            if new_table_name:
                column_name = field['column_name']
                fields.append(f"{new_table_name}.{column_name}")
            else:
                fields.append(field['column_name'])

        return fields
