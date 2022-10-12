"""QwikGeo API - Analysis - Analysis Queries"""

import datetime

import main
import utilities
from routers import analysis


async def buffer(table: str, distance_in_kilometers: float, new_table_id: str, process_id: str):
    """
    Method to buffer any geometric table
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        fields = await utilities.get_table_columns(
            table=table,
            app=main.app
        )

        fields = ','.join(fields)

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT {fields}, ST_Transform(ST_Buffer(ST_Transform(geom,3857), {distance_in_kilometers*1000}),4326) as geom
            FROM user_data."{table}";
            """

            await con.fetch(sql_query)

            buffer_column_query = f"""
            ALTER TABLE user_data."{new_table_id}"
            ADD COLUMN buffer_distance_in_kilometers float NOT NULL
            DEFAULT {distance_in_kilometers};
            """

            await con.fetch(buffer_column_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def dissolve(table: str, new_table_id: str, process_id: str):
    """
    Method to dissolve any geometric table into one geometry.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT ST_Union(geom) as geom
            FROM user_data."{table}";
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def dissolve_by_value(table: str, new_table_id: str, column: str, process_id: str):
    """
    Method to dissolve any geometric table into one geometry based off a column.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT DISTINCT("{column}"), ST_Union(geom) as geom
            FROM user_data."{table}"
            GROUP BY "{column}";
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def square_grids(table: str, new_table_id: str, grid_size_in_kilometers: int, process_id: str):
    """
    Method to generate square grids based off a given table.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT ST_Transform((ST_SquareGrid({grid_size_in_kilometers*1000}, ST_Transform(a.geom, 3857))).geom,4326) as geom
            FROM user_data."{table}" a;
            """

            await con.fetch(sql_query)

            size_column_query = f"""
            ALTER TABLE user_data."{new_table_id}"
            ADD COLUMN grid_size_in_kilometers float NOT NULL
            DEFAULT {grid_size_in_kilometers};
            """

            await con.fetch(size_column_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def hexagon_grids(table: str, new_table_id: str, grid_size_in_kilometers: int, process_id: str):
    """
    Method to generate hexagon grids based off a given table.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT ST_Transform((ST_HexagonGrid({grid_size_in_kilometers*1000}, ST_Transform(a.geom, 3857))).geom,4326) as geom
            FROM user_data."{table}" a;
            """

            await con.fetch(sql_query)

            size_column_query = f"""
            ALTER TABLE user_data."{new_table_id}"
            ADD COLUMN grid_size_in_kilometers float NOT NULL
            DEFAULT {grid_size_in_kilometers};
            """

            await con.fetch(size_column_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def bounding_box(table: str, new_table_id: str, process_id: str):
    """
    Method to generate a bounding box based off a given table.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT ST_Envelope(ST_Union(geom)) as geom
            FROM user_data."{table}";
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def k_means_cluster(table: str, new_table_id: str, number_of_clusters: int, process_id: str):
    """
    Method to generate clusters based off a k means_clustering.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        fields = await utilities.get_table_columns(
            table=table,
            app=main.app
        )

        fields = ','.join(fields)

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT ST_ClusterKMeans(geom, {number_of_clusters}) over () as cluster_id, {fields}, geom
            FROM user_data."{table}";
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def center_of_each_polygon(table: str, new_table_id: str, process_id: str):
    """
    Method to find center of each polygon based off a given table.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        fields = await utilities.get_table_columns(
            table=table,
            app=main.app
        )

        fields = ','.join(fields)

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT {fields}, ST_Centroid(geom) geom
            FROM user_data."{table}";
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def center_of_dataset(table: str, new_table_id: str, process_id: str):
    """
    Method to find center of all geometries based off a given table.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT ST_Centroid(ST_Union(geom)) geom
            FROM user_data."{table}";
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def find_within_distance(table: str, new_table_id: str,
    latitude: float, longitude: float, distance_in_kilometers: float, process_id: str):
    """
    Method to find all geometries within set distance of latitude and longitude.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT *
            FROM user_data."{table}"
            WHERE ST_Intersects(geom, ST_Transform(ST_Buffer(ST_Transform(ST_SetSRID(ST_Point({longitude}, {latitude}),4326),3857), {distance_in_kilometers*1000}),4326));
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def convex_hull(table: str, new_table_id: str, process_id: str):
    """
    Method to find the convex hull of all geometries based off a given table.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT ST_ConvexHull(ST_Union(geom)) geom
            FROM user_data."{table}";
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def aggregate_points_by_grids(table: str, new_table_id: str, distance_in_kilometers: float, grid_type: str,process_id: str):
    """
    Method to aggegate points into grids.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            WITH grids AS (
                SELECT ST_Transform((ST_{grid_type}Grid({distance_in_kilometers*1000}, ST_Transform(ST_ConvexHull(ST_Union(a.geom)), 3857))).geom,4326) AS geom
                FROM user_data."{table}" as a
            )

            SELECT COUNT(points.geom) AS number_of_points, polygons.geom
            FROM user_data."{table}" AS points
            LEFT JOIN grids AS polygons
            ON ST_Contains(polygons.geom,points.geom)
            GROUP BY polygons.geom;
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def aggregate_points_by_polygons(table: str, new_table_id: str, polygons: str, process_id: str):
    """
    Method to aggregate points into polygons.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT polygons.gid, COUNT(points.geom) AS number_of_points, polygons.geom
            FROM user_data."{table}" AS points
            LEFT JOIN {polygons} AS polygons
            ON ST_Contains(polygons.geom,points.geom)
            GROUP BY polygons.gid;
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def select_inside(table: str, new_table_id: str, polygons: str, process_id: str):
    """
    Method to find geometries within a given polygon table.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT points.*
            FROM user_data."{table}" AS points
            JOIN user_data."{polygons}" AS polygons
            ON ST_Intersects(points.geom, polygons.geom);
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def select_outside(table: str, new_table_id: str, polygons: str, process_id: str):
    """
    Method to find geometries outside a given polygon table.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT *
            FROM user_data."{table}" AS points
            JOIN user_data."{polygons}" AS polygons
            ON ST_Intersects(points.geom, polygons.geom)
            WHERE polygons.gid IS NULL;
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def clip(table: str, new_table_id: str, polygons: str, process_id: str):
    """
    Method to clip geometries given polygon table.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        fields = await utilities.get_table_columns(
            table=table,
            new_table_name="a",
            app=main.app
        )

        fields = ','.join(fields)

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT {fields}, ST_Intersection(polygons.geom, a.geom) as geom
            FROM user_data."{table}" as a, user_data."{polygons}" as polygons
            WHERE ST_Intersects(a.geom, polygons.geom);
            """

            await con.fetch(sql_query)

            analysis.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis.analysis_processes[process_id]['status'] = "FAILURE"
        analysis.analysis_processes[process_id]['error'] = str(error)
        analysis.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    