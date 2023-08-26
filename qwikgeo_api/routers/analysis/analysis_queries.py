"""QwikGeo API - Analysis - Analysis Queries"""

import datetime

from qwikgeo_api import main
from qwikgeo_api import utilities
from qwikgeo_api import db_models
from qwikgeo_api.routers.analysis import router as analysis_router


async def buffer(
    username: str,
    table_id: str,
    distance_in_kilometers: float,
    new_table_id: str,
    process_id: str
):
    """
    Method to buffer any geometric table
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        fields = await utilities.get_table_columns(
            table_id=table_id,
            app=main.app
        )

        fields = ','.join(fields)

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT {fields}, ST_Transform(ST_Buffer(ST_Transform(geom,3857), {distance_in_kilometers*1000}),4326) as geom
            FROM user_data."{table_id}";
            """

            await con.fetch(sql_query)

            buffer_column_query = f"""
            ALTER TABLE user_data."{new_table_id}"
            ADD COLUMN buffer_distance_in_kilometers float NOT NULL
            DEFAULT {distance_in_kilometers};
            """

            await con.fetch(buffer_column_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Buffer Analysis of {item_metadata.title}",
                description=f"A {distance_in_kilometers} kilometer buffer analysis of {item_metadata.title}.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def dissolve(
    username: str,
    table_id: str,
    new_table_id: str,
    process_id: str
):
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
            FROM user_data."{table_id}";
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Dissolve Analysis of {item_metadata.title}",
                description=f"A dissolve analysis of {item_metadata.title}.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def dissolve_by_value(
    username: str,
    table_id: str,
    new_table_id: str,
    column: str,
    process_id: str
):
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
            FROM user_data."{table_id}"
            GROUP BY "{column}";
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Dissolve By Value Analysis of {item_metadata.title}",
                description=f"A dissolve by value analysis of {item_metadata.title} using the column {column}.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def square_grids(
    username: str,
    table_id: str,
    new_table_id: str,
    grid_size_in_kilometers: int,
    process_id: str
):
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
            FROM user_data."{table_id}" a;
            """

            await con.fetch(sql_query)

            size_column_query = f"""
            ALTER TABLE user_data."{new_table_id}"
            ADD COLUMN grid_size_in_kilometers float NOT NULL
            DEFAULT {grid_size_in_kilometers};
            """

            await con.fetch(size_column_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Square Grid Analysis of {item_metadata.title}",
                description=f"A square grid analysis of {item_metadata.title} with a grid size of {grid_size_in_kilometers} kilometers.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def hexagon_grids(
    username: str,
    table_id: str,
    new_table_id: str,
    grid_size_in_kilometers: int,
    process_id: str
):
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
            FROM user_data."{table_id}" a;
            """

            await con.fetch(sql_query)

            size_column_query = f"""
            ALTER TABLE user_data."{new_table_id}"
            ADD COLUMN grid_size_in_kilometers float NOT NULL
            DEFAULT {grid_size_in_kilometers};
            """

            await con.fetch(size_column_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Hexagon Grid Analysis of {item_metadata.title}",
                description=f"A hexagon grid analysis of {item_metadata.title} with a grid size of {grid_size_in_kilometers} kilometers.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def bounding_box(
    username: str,
    table_id: str,
    new_table_id: str,
    process_id: str
):
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
            FROM user_data."{table_id}";
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Bounding Box Analysis of {item_metadata.title}",
                description=f"A bounding box analysis of {item_metadata.title}.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def k_means_cluster(
    username: str,
    table_id: str,
    new_table_id: str,
    number_of_clusters: int,
    process_id: str
):
    """
    Method to generate clusters based off a k means_clustering.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        fields = await utilities.get_table_columns(
            table_id=table_id,
            app=main.app
        )

        fields = ','.join(fields)

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT ST_ClusterKMeans(geom, {number_of_clusters}) over () as cluster_id, {fields}, geom
            FROM user_data."{table_id}";
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"K Means Cluster Analysis of {item_metadata.title}",
                description=f"A k means cluster analysis of {item_metadata.title} with {number_of_clusters} clusters.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def center_of_each_polygon(
    username: str,
    table_id: str,
    new_table_id: str,
    process_id: str
):
    """
    Method to find center of each polygon based off a given table.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        fields = await utilities.get_table_columns(
            table_id=table_id,
            app=main.app
        )

        fields = ','.join(fields)

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT {fields}, ST_Centroid(geom) geom
            FROM user_data."{table_id}";
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Center of Each Polygon Analysis of {item_metadata.title}",
                description=f"A center of each polygon analysis of {item_metadata.title}.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def center_of_dataset(
    username: str,
    table_id: str,
    new_table_id: str,
    process_id: str
):
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
            FROM user_data."{table_id}";
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Center of Dataset Analysis of {item_metadata.title}",
                description=f"A center of dataset analysis of {item_metadata.title}.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def find_within_distance(
    username: str,
    table_id: str,
    new_table_id: str,
    latitude: float,
    longitude: float,
    distance_in_kilometers: float,
    process_id: str
):
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
            FROM user_data."{table_id}"
            WHERE ST_Intersects(geom, ST_Transform(ST_Buffer(ST_Transform(ST_SetSRID(ST_Point({longitude}, {latitude}),4326),3857), {distance_in_kilometers*1000}),4326));
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Find Within Distance Analysis of {item_metadata.title}",
                description=f"A find within distance analysis of {item_metadata.title} to find all features within {distance_in_kilometers} kilometers of {latitude}, {longitude}.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def convex_hull(
    username: str,
    table_id: str,
    new_table_id: str,
    process_id: str
):
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
            FROM user_data."{table_id}";
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Convex Hull Analysis of {item_metadata.title}",
                description=f"A convex hull analysis of {item_metadata.title}.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def aggregate_points_by_grids(
    username: str,
    table_id: str,
    new_table_id: str,
    distance_in_kilometers: float,
    grid_type: str,
    process_id: str
):
    """
    Method to aggregate points into grids.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            WITH grids AS (
                SELECT ST_Transform((ST_{grid_type}Grid({distance_in_kilometers*1000}, ST_Transform(ST_ConvexHull(ST_Union(a.geom)), 3857))).geom,4326) AS geom
                FROM user_data."{table_id}" as a
            )

            SELECT COUNT(points.geom) AS number_of_points, polygons.geom
            FROM user_data."{table_id}" AS points
            LEFT JOIN grids AS polygons
            ON ST_Contains(polygons.geom,points.geom)
            GROUP BY polygons.geom;
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Aggregate Points By Grids Analysis of {item_metadata.title}",
                description=f"A aggregate points by grids analysis of {item_metadata.title} with a grid size of {distance_in_kilometers} kilometers.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def aggregate_points_by_polygons(
    username: str,
    table_id: str,
    new_table_id: str,
    polygons: str,
    process_id: str
):
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
            FROM user_data."{table_id}" AS points
            LEFT JOIN {polygons} AS polygons
            ON ST_Contains(polygons.geom,points.geom)
            GROUP BY polygons.gid;
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Aggregate Points By Polygons Analysis of {item_metadata.title}",
                description=f"A aggregate points by polygons analysis of {item_metadata.title}.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def select_inside(
    username: str,
    table_id: str,
    new_table_id: str,
    polygons: str,
    process_id: str
):
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
            FROM user_data."{table_id}" AS points
            JOIN user_data."{polygons}" AS polygons
            ON ST_Intersects(points.geom, polygons.geom);
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            polygon_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=polygons)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            polygon_item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=polygon_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Select Inside Analysis of {item_metadata.title}",
                description=f"A select inside analysis of {item_metadata.title} within {polygon_item_metadata.title}.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def select_outside(
    username: str,
    table_id: str,
    new_table_id: str,
    polygons: str,
    process_id: str
):
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
            FROM user_data."{table_id}" AS points
            JOIN user_data."{polygons}" AS polygons
            ON ST_Intersects(points.geom, polygons.geom)
            WHERE polygons.gid IS NULL;
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            polygon_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=polygons)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            polygon_item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=polygon_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Select Outside Analysis of {item_metadata.title}",
                description=f"A select outside analysis of {item_metadata.title} within {polygon_item_metadata.title}.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def clip(
    username: str,
    table_id: str,
    new_table_id: str,
    polygons: str,
    process_id: str
):
    """
    Method to clip geometries given polygon table.
    """

    start = datetime.datetime.now()

    try:

        pool = main.app.state.database

        fields = await utilities.get_table_columns(
            table_id=table_id,
            new_table_name="a",
            app=main.app
        )

        fields = ','.join(fields)

        async with pool.acquire() as con:
            sql_query = f"""
            CREATE TABLE user_data."{new_table_id}" AS
            SELECT {fields}, ST_Intersection(polygons.geom, a.geom) as geom
            FROM user_data."{table_id}" as a, user_data."{polygons}" as polygons
            WHERE ST_Intersects(a.geom, polygons.geom);
            """

            await con.fetch(sql_query)

            table_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=table_id)
            )

            polygon_metadata = await db_models.Table_Pydantic.from_queryset_single(
                db_models.Table.get(table_id=polygons)
            )

            item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
            )

            polygon_item_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=polygon_metadata.portal_id.portal_id)
            )

            await utilities.create_table(
                username=username,
                table_id=new_table_id,
                title=f"Clip Analysis of {item_metadata.title}",
                description=f"A clip analysis of {item_metadata.title} within {polygon_item_metadata.title}.",
                tags=["analysis"],
                searchable=False,
                read_access_list=[username],
                write_access_list=[username]
            )

            analysis_router.analysis_processes[process_id]['status'] = "SUCCESS"
            analysis_router.analysis_processes[process_id]['new_table_id'] = new_table_id
            analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
            analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        analysis_router.analysis_processes[process_id]['status'] = "FAILURE"
        analysis_router.analysis_processes[process_id]['error'] = str(error)
        analysis_router.analysis_processes[process_id]['completion_time'] = datetime.datetime.now()
        analysis_router.analysis_processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
