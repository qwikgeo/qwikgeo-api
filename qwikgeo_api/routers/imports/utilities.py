"""QwikGeo API - Import Utilities"""

import os
import json

import datetime
import subprocess
from fastapi import FastAPI
import aiohttp
import pandas as pd

from qwikgeo_api import utilities
from qwikgeo_api import config

import_processes = {}

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
        formatted_table_columns += f"{utilities.remove_bad_characters(col)},"

    formatted_table_columns = formatted_table_columns[:-1]

    create_table_sql = f"""CREATE TABLE user_data."{new_table_id}" ("""

    for name, data_type in data_frame.dtypes.iteritems():
        columns += f"{utilities.remove_bad_characters(name)},"
        create_table_sql += f'"{utilities.remove_bad_characters(name)}"'
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

        await clean_up_table(
            table_id=new_table_id,
            app=app
        )

        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")

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

    table_column = utilities.remove_bad_characters(table_column)

    columns = ""

    formatted_table_columns = ""

    formatted_map_columns = ""

    for col in table_columns:
        if col not in map_columns:
            formatted_table_columns += f"a.{utilities.remove_bad_characters(col)},"

    for column in map_columns:
        formatted_map_columns += f"b.{utilities.remove_bad_characters(column)},"

    create_table_sql = f"""CREATE TABLE user_data."{new_table_id}_temp" ("""

    for name, data_type in data_frame.dtypes.iteritems():
        columns += f"{utilities.remove_bad_characters(name)},"
        create_table_sql += f'"{utilities.remove_bad_characters(name)}"'
        if utilities.remove_bad_characters(name) == table_column:
            create_table_sql += " text,"
        else:
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

        insert_sql = f"""COPY user_data."{new_table_id}_temp" ({columns})
        FROM '{file_path}'
        DELIMITER ','
        CSV HEADER;"""

        await con.fetch(insert_sql)

        join_sql = f"""CREATE TABLE user_data."{new_table_id}" AS
            SELECT {formatted_table_columns} {formatted_map_columns} geom
            FROM user_data."{new_table_id}_temp" as a
            LEFT JOIN user_data."{map_name}" as b
            ON a."{table_column}" = b."{map_column}";
        """

        await con.fetch(join_sql)

        await con.fetch(f"""DROP TABLE IF EXISTS user_data."{new_table_id}_temp";""")

        await clean_up_table(
            table_id=new_table_id,
            app=app
        )

        media_directory = os.listdir(f"{os.getcwd()}/media/")
        for file in media_directory:
            if new_table_id in file:
                os.remove(f"{os.getcwd()}/media/{file}")

async def validate_table(
    table_id: str,
    app: FastAPI
) -> bool:
    pool = app.state.database

    async with pool.acquire() as con:
        exists = await con.fetchrow(f"""
        SELECT EXISTS (
        SELECT FROM 
            pg_tables
        WHERE 
            schemaname = 'user_data' AND 
            tablename  = '{table_id}'
        );
        """)

        if exists['exists']:
            count = await con.fetchrow(f"""
            SELECT COUNT(*)
            FROM user_data.{table_id}
            """)

            if count['count'] > 0:
                return True

        return False


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
    app: FastAPI,
    token: str=None,
    filter: str="1=1"
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

                feature_stats_url = f"{url}/query?where={filter}&returnGeometry=false&returnIdsOnly=true&f=json"

                async with session.get(feature_stats_url) as feature_resp:

                    data = await feature_resp.text()

                    data = json.loads(data)

                    object_ids = data['objectIds']

                    number_of_features = len(data['objectIds'])

                    error = ""

                    if number_of_features <= max_number_of_features_per_query:

                        async with session.get(f"{url}/query?where={filter}&outFields=*&returnGeometry=true&geometryPrecision=6&outSR=4326&f=geojson") as resp:

                            data = await resp.json()

                            if 'error' in data:
                                error = data['error']

                            with open(f'{table_id}.geojson', 'w') as json_file:
                                json.dump(data, json_file)

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
                                'where': filter,
                                'objectIds': str( ids_requested )[1:-1],
                                'outSR': '4326',
                                'returnGeometry': 'true',
                                'outFields': '*',
                                'geometryPrecision': '4'
                            }

                            async with session.post( f"{url}/query", data=payload ) as resp:

                                data = await resp.json()

                                if 'error' in data:
                                    error = data['error']

                                feature_collection['features'] += data['features']

                        with open(f'{table_id}.geojson', 'w') as json_file:
                            json.dump(feature_collection, json_file)                

                load_geographic_data_to_server(
                    table_id=table_id,
                    file_path=f'{table_id}.geojson'
                )

                valid_table = await validate_table(
                    table_id=table_id,
                    app=app
                )

                if valid_table:

                    await clean_up_table(
                        table_id=table_id,
                        app=app
                    )

                    item = {
                        "user_name": username,
                        "table_id": table_id,
                        "title": title,
                        "tags": tags,
                        "description": description,
                        "read_access_list": read_access_list,
                        "write_access_list": write_access_list,
                        "searchable": searchable
                    }

                    await utilities.create_single_item_in_database(
                        item=item,
                        model_name="Table"
                    )

                    import_processes[process_id]['status'] = "SUCCESS"
                    import_processes[process_id]['table_id'] = table_id
                else:
                    import_processes[process_id]['status'] = "FAILURE"
                    import_processes[process_id]['error'] = f"No data within ArcGIS Service. Error: {str(error)}"
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
    searchable: bool,
    app: FastAPI
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

        valid_table = await validate_table(
            table_id=new_table_id,
            app=app
        )

        if valid_table:

            await clean_up_table(
                table_id=new_table_id,
                app=app
            )
            
            item = {
                "user_name": username,
                "table_id": new_table_id,
                "title": title,
                "tags": tags,
                "description": description,
                "read_access_list": read_access_list,
                "write_access_list": write_access_list,
                "searchable": searchable
            }

            await utilities.create_single_item_in_database(
                item=item,
                model_name="Table"
            )

            import_processes[process_id]['status'] = "SUCCESS"
            import_processes[process_id]['new_table_id'] = new_table_id
        else:
            import_processes[process_id]['status'] = "FAILURE"
            import_processes[process_id]['error'] = "No data within files loaded."
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

        item = {
            "user_name": username,
            "table_id": new_table_id,
            "title": title,
            "tags": tags,
            "description": description,
            "read_access_list": read_access_list,
            "write_access_list": write_access_list,
            "searchable": searchable
        }

        await utilities.create_single_item_in_database(
            item=item,
            model_name="Table"
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

        item = {
            "user_name": username,
            "table_id": new_table_id,
            "title": title,
            "tags": tags,
            "description": description,
            "read_access_list": read_access_list,
            "write_access_list": write_access_list,
            "searchable": searchable
        }

        await utilities.create_single_item_in_database(
            item=item,
            model_name="Table"
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
    
        item = {
            "user_name": username,
            "table_id": new_table_id,
            "title": title,
            "tags": tags,
            "description": description,
            "read_access_list": read_access_list,
            "write_access_list": write_access_list,
            "searchable": searchable
        }

        await utilities.create_single_item_in_database(
            item=item,
            model_name="Table"
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

        item = {
            "user_name": username,
            "table_id": new_table_id,
            "title": title,
            "tags": tags,
            "description": description,
            "read_access_list": read_access_list,
            "write_access_list": write_access_list,
            "searchable": searchable
        }

        await utilities.create_single_item_in_database(
            item=item,
            model_name="Table"
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
    subprocess.call(f'ogr2ogr -f "PostgreSQL" "PG:host={host} user={username} dbname={database} password={password} port={config.DB_PORT}" "{file_path}" -lco GEOMETRY_NAME=geom -lco FID=gid -nlt PROMOTE_TO_MULTI -lco PRECISION=no -nln user_data.{table_id} -overwrite', shell=True)
    media_directory = os.listdir(f"{os.getcwd()}/media/")
    for file in media_directory:
        if table_id in file:
            os.remove(f"{os.getcwd()}/media/{file}")
async def clean_up_table(
    table_id: str,
    app: FastAPI
):
    """Method to clean up table in postgres after upload."""


    pool = app.state.database

    async with pool.acquire() as con:

        await con.fetch(f"""
        DELETE FROM user_data.{table_id}
        WHERE geom IS NULL;
        """)

        await con.fetch(f"""
        CREATE INDEX {table_id}_geom_idx
        ON user_data.{table_id}
        USING GIST (geom);
        """)

        await con.fetch(f"""
        CLUSTER user_data.{table_id}
        USING {table_id}_geom_idx;
        """)

        await con.fetch(f"""
        ALTER TABLE user_data.{table_id} 
        DROP COLUMN IF EXISTS gid;
        """)

        await con.fetch(f"""
        ALTER TABLE user_data.{table_id} 
        ADD COLUMN gid SERIAL PRIMARY KEY;
        """)

        await con.fetch(f"""
        UPDATE user_data.{table_id}
        SET geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(geom)))
        WHERE ST_IsValid(geom) = false;
        """)

        await con.fetch(f"""
        VACUUM ANALYZE user_data.{table_id};
        """)