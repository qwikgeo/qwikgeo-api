"""QwikGeo API - Utilities"""

import os
import json
import random
import re
import string
import uuid
import datetime
import subprocess
import shutil
import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, FastAPI, HTTPException, status
from pygeofilter.backends.sql import to_sql_where
from pygeofilter.parsers.ecql import parse
import aiohttp
import pandas as pd
import tortoise
from tortoise.query_utils import Prefetch
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, DecodeError
import asyncpg

import db_models
import config

import_processes = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def get_all_tables_from_db(
    app: FastAPI
) -> list:
    """
    Method to return list of tables in database.

    """

    pool = app.state.database

    db_tables = []

    async with pool.acquire() as con:
        tables_query = """
        SELECT tablename
        FROM pg_catalog.pg_tables
        WHERE schemaname = 'user_data'
        AND tablename != 'spatial_ref_sys'; 
        """
        tables = await con.fetch(tables_query)

        for table in tables:
            db_tables.append(table['tablename'])

        return db_tables

async def validate_table_access(
    table: str,
    user_name: str,
    write_access: bool=False
) -> bool:
    """
    Method to validate if user has access to table in portal.

    """

    try:
        table = await db_models.Table_Pydantic.from_queryset_single(
            db_models.Table.get(table_id=table)
        )

        item = await db_models.Item_Pydantic.from_queryset_single(
            db_models.Item.get(portal_id=table.portal_id.portal_id)
        )

        user_groups = await get_user_groups(user_name)

        access = False

        write_access_list = []
        read_access_list = []

        for access in item.item_write_access_list:
            write_access_list.append(access.name)

        for access in item.item_read_access_list:
            read_access_list.append(access.name)

        if write_access:
            if any(map(lambda v: v in user_groups, write_access_list)):
                access = True
        elif any(map(lambda v: v in user_groups, read_access_list)):
            access = True

        if access is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='No access to table.'
            )
    except tortoise.exceptions.DoesNotExist as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Table does not exist.'
        ) from exc

async def create_table(
    username: str,
    table_id: str,
    title: str,
    tags: list,
    description: str,
    searchable: bool,
    read_access_list: list,
    write_access_list: list
) -> object:
    """
    Method to create a table within the database of the portal.

    """

    if read_access_list == []:
        read_access_list = [username]
    if write_access_list == []:
        write_access_list = [username]
    item = await db_models.Item.create(
        username_id=username,
        title=title,
        tags=tags,
        description=description,
        views="1",
        searchable=searchable,
        item_type="table"
    )

    for name in read_access_list:
        await db_models.ItemReadAccessList.create(name=name, portal_id_id=item.portal_id)

    for name in write_access_list:
        await db_models.ItemWriteAccessList.create(name=name, portal_id_id=item.portal_id)

    await db_models.Table.create(
        username_id=username,
        portal_id_id=item.portal_id,
        table_id=table_id
    )

    return item

async def get_token_header(
    token: str=Depends(oauth2_scheme)
) -> str:
    """
    Method to return username via JWT token.

    """

    try:
        user = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    except (ExpiredSignatureError, InvalidSignatureError, DecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"JWT Error: {str(exc)}"
        ) from exc
    return user['username']

async def get_user_groups(
    username: str
) -> list:
    """
    Method to return a list of groups a user has access to within the portal.

    """

    groups_plus_username = [username]

    groups = (
        await db_models.Group.all()
        .prefetch_related(Prefetch(
            "group_users", queryset=db_models.GroupUser.filter(username=username)
        ))
    )

    for group in groups:
        groups_plus_username.append(group.name)

    return groups_plus_username

async def authenticate_user(
    username: str,
    password: str
) -> object:
    """
    Method to validate a user via their username and password and return
    the user's information.

    """

    try:
        user = await db_models.User.get(username=username)
    except tortoise.exceptions.DoesNotExist as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password.'
        ) from exc
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password.'
        )
    if not user.verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password.'
        )
    return user

async def get_tile(
    scheme: str,
    table: str,
    tile_matrix_set_id: str,
    z: int,
    x: int,
    y: int,
    fields: str,
    cql_filter: str,
    app: FastAPI
) -> bytes:
    """
    Method to return vector tile from database.

    """

    cache_file = f'{os.getcwd()}/cache/{scheme}_{table}/{tile_matrix_set_id}/{z}/{x}/{y}'

    if os.path.exists(cache_file):
        return '', True

    pool = app.state.database

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

        sql_vector_query += f"LIMIT {config.MAX_FEATURES_PER_TILE}) as tile"

        tile = await con.fetchval(sql_vector_query)

        if fields is None and cql_filter is None and config.CACHE_AGE_IN_SECONDS > 0:

            cache_file_dir = f'{os.getcwd()}/cache/{scheme}_{table}/{tile_matrix_set_id}/{z}/{x}'

            if not os.path.exists(cache_file_dir):
                try:
                    os.makedirs(cache_file_dir)
                except OSError:
                    pass

            with open(cache_file, "wb") as file:
                file.write(tile)
                file.close()

        return tile, False

async def get_table_columns_list(
    scheme: str,
    table: str,
    app: FastAPI
) -> list:
    """
    Method used to retrieve columns for a given table.

    """

    pool = app.state.database

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

async def get_table_geometry_type(
    scheme: str,
    table: str,
    app: FastAPI
) -> list:
    """
    Method used to retrieve the geometry type for a given table.

    """

    pool = app.state.database

    async with pool.acquire() as con:
        geometry_query = f"""
        SELECT ST_GeometryType(geom) as geom_type
        FROM {scheme}.{table}
        """
        try:
            geometry_type = await con.fetchval(geometry_query)
        except asyncpg.exceptions.UndefinedTableError:
            return "unkown"

        geom_type = 'point'

        if 'Polygon' in geometry_type:
            geom_type = 'polygon'
        elif 'Line' in geometry_type:
            geom_type = 'line'

        return geom_type

async def get_table_center(
    scheme: str,
    table: str,
    app: FastAPI
) -> list:
    """
    Method used to retrieve the table center for a given table.

    """

    pool = app.state.database

    async with pool.acquire() as con:
        query = f"""
        SELECT ST_X(ST_Centroid(ST_Union(geom))) as x,
        ST_Y(ST_Centroid(ST_Union(geom))) as y
        FROM {scheme}.{table}
        """
        center = await con.fetch(query)

        return [center[0][0],center[0][1]]

async def generate_where_clause(
    info: object,
    con,
    no_where: bool=False
) -> str:
    """
    Method to generate where clause.

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
            query += " WHERE "
        else:
            query += " AND "
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
    Method to return a new table id.

    """
    letters = string.ascii_lowercase

    return ''.join(random.choice(letters) for i in range(50))

def get_new_process_id() -> str:
    """
    Method to return a new process id.

    """

    return str(uuid.uuid4())

def remove_bad_characters(
    string_of_characters: str
) -> str:
    """
    Method remove bad characters from a string.

    """

    regex = re.compile('[^a-zA-Z0-9_]')
    return regex.sub('_', string_of_characters).lower()

async def upload_csv_to_db_with_latitude_and_longitude(
    file_path: str,
    new_table_id: str,
    latitude: str,
    longitude: str,
    table_columns: list,
    app: FastAPI
) -> None:
    """
    Method to upload data from from a csv file with latitude and longitude columns into db.

    """

    pd.options.display.max_rows = 10

    data_frame = pd.read_csv(file_path)

    columns = ""

    formatted_table_columns = ""

    for col in table_columns:
        formatted_table_columns += f"{remove_bad_characters(col)},"

    formatted_table_columns = formatted_table_columns[:-1]

    create_table_sql = f"""CREATE TABLE user_data."{new_table_id}" ("""

    for name, data_type in data_frame.dtypes.iteritems():
        columns += f"{remove_bad_characters(name)},"
        create_table_sql += f'"{remove_bad_characters(name)}"'
        if data_type == "object" or data_type == "datetime64":
            create_table_sql += " text,"
        if data_type == "int64":
            create_table_sql += " integer,"
        if data_type == "float64":
            create_table_sql += " double precision,"

    create_table_sql = create_table_sql[:-1]

    columns = columns[:-1]

    create_table_sql += ");"

    pool = app.state.database

    async with pool.acquire() as con:
        await con.fetch(f"""DROP TABLE IF EXISTS user_data."{new_table_id}";""")

        await con.fetch(create_table_sql)

        insert_sql = f"""COPY user_data."{new_table_id}"({columns})
        FROM '{file_path}'
        DELIMITER ','
        CSV HEADER;"""

        await con.fetch(insert_sql)

        add_geom_sql = f"""
            SELECT AddGeometryColumn ('user_data','{new_table_id}','geom',4326,'POINT',2);                
        """

        await con.fetch(add_geom_sql)

        update_geom_sql = f"""
            UPDATE user_data."{new_table_id}" 
            SET geom = ST_SetSRID(ST_MakePoint({longitude},{latitude}), 4326);
        """

        await con.fetch(update_geom_sql)

        delete_bad_geom_sql = f"""
            DELETE FROM user_data."{new_table_id}" WHERE geom IS NULL;
        """

        await con.fetch(delete_bad_geom_sql)

async def upload_csv_to_db_with_geographic_data(
    file_path: str,
    new_table_id: str,
    map_name: str,
    map_column: str,
    table_column: str,
    table_columns: list,
    map_columns: list,
    app: FastAPI
) -> None:
    """
    Method to upload data from from a csv file with geographic data into db.

    """

    pd.options.display.max_rows = 10

    data_frame = pd.read_csv(file_path)

    columns = ""

    formatted_table_columns = ""

    formatted_map_columns = ""

    for col in table_columns:
        if col not in map_columns:
            formatted_table_columns += f"a.{remove_bad_characters(col)},"

    for column in map_columns:
        formatted_map_columns += f"b.{remove_bad_characters(column)},"

    create_table_sql = f"""CREATE TABLE user_data."{new_table_id}_temp" ("""

    for name, data_type in data_frame.dtypes.iteritems():
        columns += f"{remove_bad_characters(name)},"
        create_table_sql += f'"{remove_bad_characters(name)}"'
        if data_type == "object" or data_type == "datetime64":
            create_table_sql += " text,"
        if data_type == "int64":
            create_table_sql += " integer,"
        if data_type == "float64":
            create_table_sql += " double precision,"

    create_table_sql = create_table_sql[:-1]
    columns = columns[:-1]

    create_table_sql += ");"

    pool = app.state.database

    async with pool.acquire() as con:
        await con.fetch(f"""DROP TABLE IF EXISTS user_data."{new_table_id}_temp";""")

        await con.fetch(create_table_sql)

        insert_sql = f"""COPY user_data."{new_table_id}_temp"({columns})
        FROM '{file_path}'
        DELIMITER ','
        CSV HEADER;"""

        await con.fetch(insert_sql)

        join_sql = f"""CREATE TABLE user_data."{new_table_id}" AS
            SELECT {formatted_table_columns} {formatted_map_columns} geom
            FROM "{new_table_id}_temp" as a
            LEFT JOIN "{map_name}" as b
            ON a."{table_column}" = b."{map_column}";
        """

        await con.fetch(join_sql)

        await con.fetch(f"""DROP TABLE IF EXISTS user_data."{new_table_id}_temp";""")

async def get_arcgis_data(
    url: str,
    table_id: str,
    process_id: str,
    username: str,
    title: str,
    tags: list,
    description: str,
    read_access_list: list,
    write_access_list: list,
    searchable: bool,
    token: str=None
) -> None:
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

                            with open(f'{table_id}.geojson', 'w') as json_file:
                                json.dump(data, json_file)

                            load_geographic_data_to_server(
                                table_id=table_id,
                                file_path=f'{table_id}.geojson'
                            )

                    else:
                        start_counter = 0

                        feature_collection = {
                            "type": "FeatureCollection",
                            "features": []
                        }

                        for x in range(
                            start_counter,
                            number_of_features,
                            max_number_of_features_per_query
                        ):
                            ids_requested = object_ids[x: x + max_number_of_features_per_query ]
                            payload = {
                                'f': 'geojson',
                                'where': '1=1',
                                'objectIds': str( ids_requested )[1:-1],
                                'outSR': '4326',
                                'returnGeometry': 'true',
                                'outFields': '*',
                                'geometryPrecision': '4'
                            }

                            async with session.post( f"{url}/query", data=payload ) as resp:

                                data = await resp.text()

                                data = json.loads(data)

                                if 'error' in data:
                                    print(data['error'])

                                feature_collection['features'] += data['features']

                        with open(f'{table_id}.geojson', 'w') as json_file:
                            json.dump(feature_collection, json_file)

                        load_geographic_data_to_server(
                            table_id=table_id,
                            file_path=f'{table_id}.geojson'
                        )

                await create_table(
                    username=username,
                    table_id=table_id,
                    title=title,
                    tags=tags,
                    description=description,
                    read_access_list=read_access_list,
                    write_access_list=write_access_list,
                    searchable=searchable
                )

                load_geographic_data_to_server(
                    table_id=table_id,
                    file_path=f'{table_id}.geojson'
                )

                os.remove(f'{table_id}.geojson')
                import_processes[process_id]['status'] = "SUCCESS"
                import_processes[process_id]['table_id'] = table_id
                import_processes[process_id]['completion_time'] = datetime.datetime.now()
                import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        if os.path.exists(f'{table_id}.geojson'):
            os.remove(f'{table_id}.geojson')
        import_processes[process_id]['status'] = "FAILURE"
        import_processes[process_id]['error'] = str(error)
        import_processes[process_id]['completion_time'] = datetime.datetime.now()
        import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def upload_geographic_file(
    file_path: str,
    new_table_id: str,
    process_id: str,
    username: str,
    title: str,
    tags: list,
    description: str,
    read_access_list: list,
    write_access_list: list,
    searchable: bool
) -> None:
    """
    Method to upload data from geographic file.

    """

    start = datetime.datetime.now()

    try:
        load_geographic_data_to_server(
            table_id=new_table_id,
            file_path=file_path
        )
        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")
        await create_table(
            username=username,
            table_id=new_table_id,
            title=title,
            tags=tags,
            description=description,
            read_access_list=read_access_list,
            write_access_list=write_access_list,
            searchable=searchable
        )
        import_processes[process_id]['status'] = "SUCCESS"
        import_processes[process_id]['new_table_id'] = new_table_id
        import_processes[process_id]['completion_time'] = datetime.datetime.now()
        import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")
        import_processes[process_id]['status'] = "FAILURE"
        import_processes[process_id]['error'] = str(error)
        import_processes[process_id]['completion_time'] = datetime.datetime.now()
        import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def import_geographic_data_from_csv(
    file_path: str,
    new_table_id: str,
    process_id: str,
    map_name: str,
    map_column: str,
    table_column: str,
    table_columns: list,
    map_columns: list,
    username: str,
    title: str,
    tags: list,
    description: str,
    read_access_list: list,
    write_access_list: list,
    searchable: bool,
    app: FastAPI
) -> None:
    """
    Method to upload data from from a csv file with geographic data.

    """

    start = datetime.datetime.now()

    try:
        await upload_csv_to_db_with_geographic_data(
            file_path=file_path,
            new_table_id=new_table_id,
            map_name=map_name,
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
        await create_table(
            username=username,
            table_id=new_table_id,
            title=title,
            tags=tags,
            description=description,
            read_access_list=read_access_list,
            write_access_list=write_access_list,
            searchable=searchable
        )
        import_processes[process_id]['status'] = "SUCCESS"
        import_processes[process_id]['new_table_id'] = new_table_id
        import_processes[process_id]['completion_time'] = datetime.datetime.now()
        import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")
        import_processes[process_id]['status'] = "FAILURE"
        import_processes[process_id]['error'] = str(error)
        import_processes[process_id]['completion_time'] = datetime.datetime.now()
        import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def import_point_data_from_csv(
    file_path: str,
    new_table_id: str,
    process_id: str,
    latitude: str,
    longitude: str,
    table_columns: list,
    username: str,
    title: str,
    tags: list,
    description: str,
    read_access_list: list,
    write_access_list: list,
    searchable: bool,
    app: FastAPI
) -> None:
    """
    Method to upload data from csv with lat lng columns.

    """

    start = datetime.datetime.now()

    try:
        await upload_csv_to_db_with_latitude_and_longitude(
            file_path=file_path,
            new_table_id=new_table_id,
            latitude=latitude,
            longitude=longitude,
            table_columns=table_columns,
            app=app
        )

        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")
        await create_table(
            username=username,
            table_id=new_table_id,
            title=title,
            tags=tags,
            description=description,
            read_access_list=read_access_list,
            write_access_list=write_access_list,
            searchable=searchable
        )
        import_processes[process_id]['status'] = "SUCCESS"
        import_processes[process_id]['new_table_id'] = new_table_id
        import_processes[process_id]['completion_time'] = datetime.datetime.now()
        import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")
        import_processes[process_id]['status'] = "FAILURE"
        import_processes[process_id]['error'] = str(error)
        import_processes[process_id]['completion_time'] = datetime.datetime.now()
        import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def import_point_data_from_json_file(
    file_path: str,
    new_table_id: str,
    process_id: str,
    latitude: str,
    longitude: str,
    table_columns: list,
    username: str,
    title: str,
    tags: list,
    description: str,
    read_access_list: list,
    write_access_list: list,
    searchable: bool,
    app: FastAPI
) -> None:
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
            latitude=latitude,
            longitude=longitude,
            table_columns=table_columns,
            app=app
        )

        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")
        await create_table(
            username=username,
            table_id=new_table_id,
            title=title,
            tags=tags,
            description=description,
            read_access_list=read_access_list,
            write_access_list=write_access_list,
            searchable=searchable
        )
        import_processes[process_id]['status'] = "SUCCESS"
        import_processes[process_id]['new_table_id'] = new_table_id
        import_processes[process_id]['completion_time'] = datetime.datetime.now()
        import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")
        import_processes[process_id]['status'] = "FAILURE"
        import_processes[process_id]['error'] = str(error)
        import_processes[process_id]['completion_time'] = datetime.datetime.now()
        import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def import_geographic_data_from_json_file(
    file_path: str,
    new_table_id: str,
    process_id: str,
    map_name: str,
    map_column: str,
    table_column: str,
    table_columns: list,
    map_columns: list,
    username: str,
    title: str,
    tags: list,
    description: str,
    read_access_list: list,
    write_access_list: list,
    searchable: bool,
    app: FastAPI
) -> None:
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
            map_name=map_name,
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
        await create_table(
            username=username,
            table_id=new_table_id,
            title=title,
            tags=tags,
            description=description,
            read_access_list=read_access_list,
            write_access_list=write_access_list,
            searchable=searchable
        )
        import_processes[process_id]['status'] = "SUCCESS"
        import_processes[process_id]['new_table_id'] = new_table_id
        import_processes[process_id]['completion_time'] = datetime.datetime.now()
        import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")
        import_processes[process_id]['status'] = "FAILURE"
        import_processes[process_id]['error'] = str(error)
        import_processes[process_id]['completion_time'] = datetime.datetime.now()
        import_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

def load_geographic_data_to_server(
    table_id: str,
    file_path: str
) -> None:
    """
    Method used to load a geographic file into the database.

    """
    host = config.DB_HOST
    username = config.DB_USERNAME
    password = config.DB_PASSWORD
    database = config.DB_DATABASE
    subprocess.call(f'ogr2ogr -f "PostgreSQL" "PG:host={host} user={username} dbname={database} password={password} port={config.DB_PORT}" "{file_path}" -lco GEOMETRY_NAME=geom -lco FID=gid -lco PRECISION=no -nln user_data.{table_id} -overwrite', shell=True)

async def get_table_columns(
    table: str,
    app: FastAPI,
    new_table_name: str=None
) -> list:
    """
    Method to return a list of columns for a table.

    """

    pool = app.state.database

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

async def get_table_geojson(
    scheme: str,
    table: str,
    app: FastAPI,
    filter: str=None,
    bbox :str=None,
    limit: int=200000,
    offset: int=0,
    properties: str="*",
    sort_by: str="gid",
    srid: int=4326
) -> object:
    """
    Method used to retrieve the table geojson.

    """

    pool = app.state.database

    async with pool.acquire() as con:
        query = """
        SELECT
        json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(ST_AsGeoJSON(t.*)::json)
        )
        FROM (
        """

        if properties != '*':
            query += f"SELECT {properties},ST_Transform(geom,{srid})"
        else:
            query += f"SELECT ST_Transform(geom,{srid})"

        query += f" FROM {scheme}.{table} "

        count_query = f"""SELECT COUNT(*) FROM {scheme}.{table} """

        if filter != "" :
            query += f"WHERE {filter}"
            count_query += f"WHERE {filter}"

        if bbox is not None:
            if filter != "":
                query += " AND "
                count_query += " AND "
            else:
                query += " WHERE "
                count_query += " WHERE "
            coords = bbox.split(',')
            query += f" ST_INTERSECTS(geom,ST_MakeEnvelope({coords[0]}, {coords[1]}, {coords[2]}, {coords[3]}, 4326)) "
            count_query += f" ST_INTERSECTS(geom,ST_MakeEnvelope({coords[0]}, {coords[1]}, {coords[2]}, {coords[3]}, 4326)) "

        if sort_by != "gid":
            order = sort_by.split(':')
            sort = "asc"
            if len(order) == 2 and order[1] == "D":
                sort = "desc"
            query += f" ORDER BY {order[0]} {sort}"

        query += f" OFFSET {offset} LIMIT {limit}"

        query += ") AS t;"

        geojson = await con.fetchrow(query)
        count = await con.fetchrow(count_query)

        formatted_geojson = json.loads(geojson['json_build_object'])

        if formatted_geojson['features'] is not None:
            for feature in formatted_geojson['features']:
                feature['id'] = feature['properties']['gid']

        formatted_geojson['numberMatched'] = count['count']
        formatted_geojson['numberReturned'] = 0
        if formatted_geojson['features'] is not None:
            formatted_geojson['numberReturned'] = len(formatted_geojson['features'])

        return formatted_geojson

async def get_table_bounds(
    scheme: str,
    table: str,
    app: FastAPI
) -> list:
    """
    Method used to retrieve the bounds for a given table.

    """

    pool = app.state.database

    async with pool.acquire() as con:

        query = f"""
        SELECT ST_Extent(geom)
        FROM {scheme}.{table}
        """

        table_extent = []

        try:
            extent = await con.fetchval(query)
        except asyncpg.exceptions.UndefinedTableError:
            return []

        extent = extent.replace('BOX(','').replace(')','')

        for corner in extent.split(','):
            table_extent.append(float(corner.split(' ')[0]))
            table_extent.append(float(corner.split(' ')[1]))

        return table_extent

def delete_user_tile_cache(
    table: str
) -> None:
    """
    Method to remove tile cache for a user's table    

    """

    if os.path.exists(f'{os.getcwd()}/cache/user_data_{table}'):
        shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table}')