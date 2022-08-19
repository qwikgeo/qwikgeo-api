import json
from fastapi import APIRouter, Request, HTTPException

import routers.tables.models as models

router = APIRouter()

@router.post("/edit_row_attributes/", tags=["Tables"])
async def edit_row_attributes(
        request: Request,
        info: models.EditRowAttributes
    ):

    pool = request.app.state.databases[f'{info.database}_pool']

    async with pool.acquire() as con:
        sql_field_query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{info.table}'
        AND column_name != 'geom';
        """

        db_fields = await con.fetch(sql_field_query)

        db_columns = []

        db_column_types = {}

        for field in db_fields:
            db_columns.append(field['column_name'])
            db_column_types[field['column_name']] = field['data_type']

        string_columns = ",".join(db_columns)

        query = f"""
            UPDATE "{info.table}"
            SET 
        """

        numeric_field_types = ['integer','double precision']

        for field in info.values:
            if field not in db_columns:
                raise HTTPException(status_code=400, detail=f"Column: {field} is not a column for {info.table}. Please use one of the following columns. {string_columns}")
            if db_column_types[field] in numeric_field_types: 
                query += f"{field} = {info.values[field]},"
            else:
                query += f"{field} = '{info.values[field]}',"
        
        query = query[:-1]

        query += f" WHERE gid = {info.gid};"

        await con.fetch(query)

        return {"status": True}

@router.post("/edit_row_geometry/", tags=["Tables"])
async def edit_row_geometry(
        request: Request,
        info: models.EditRowGeometry
    ):

    pool = request.app.state.databases[f'{info.database}_pool']

    async with pool.acquire() as con:

        geojson = {
            "type": info.geojson.type,
            "coordinates": json.loads(json.dumps(info.geojson.coordinates))
        }

        query = f"""
            UPDATE "{info.table}"
            SET geom = ST_GeomFromGeoJSON('{json.dumps(geojson)}')
            WHERE gid = {info.gid};
        """

        await con.fetch(query)
        
        return {"status": True}

@router.post("/add_column/", tags=["Tables"])
async def add_column(
        request: Request,
        info: models.AddColumn
    ):

    pool = request.app.state.databases[f'{info.database}_pool']

    async with pool.acquire() as con:

        query = f"""
            ALTER TABLE "{info.table}"
            ADD COLUMN "{info.column_name}" {info.column_type};
        """

        await con.fetch(query)
        
        return {"status": True}

@router.delete("/delete_column/", tags=["Tables"])
async def delete_column(
        request: Request,
        info: models.DeleteColumn
    ):

    pool = request.app.state.databases[f'{info.database}_pool']

    async with pool.acquire() as con:
        
        query = f"""
            ALTER TABLE "{info.table}"
            DROP COLUMN IF EXISTS "{info.column_name}";
        """

        await con.fetch(query)
        
        return {"status": True}

@router.post("/add_row/", tags=["Tables"])
async def add_row(
        request: Request,
        info: models.AddRow
    ):

    pool = request.app.state.databases[f'{info.database}_pool']

    async with pool.acquire() as con:

        sql_field_query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{info.table}'
        AND column_name != 'geom'
        AND column_name != 'gid';
        """

        db_fields = await con.fetch(sql_field_query)

        db_columns = []

        db_column_types = {}

        for field in db_fields:
            db_columns.append(field['column_name'])
            db_column_types[field['column_name']] = field['data_type']

        string_columns = ",".join(db_columns)

        input_columns = ""
        values = ""

        numeric_field_types = ['integer','double precision']

        for column in info.columns:
            if column.column_name not in db_columns:
                raise HTTPException(status_code=400, detail=f"Column: {column.column_name} is not a column for {info.table}. Please use one of the following columns. {string_columns}")
            input_columns += f""""{column.column_name}","""
            if db_column_types[column.column_name] in numeric_field_types:
                values += f"""{float(column.value)},"""
            else:
                values += f"""'{column.value}',"""
        
        input_columns = input_columns[:-1]
        values = values[:-1]

        query = f"""
            INSERT INTO "{info.table}" ({input_columns})
            VALUES ({values})
            RETURNING gid;
        """

        result = await con.fetch(query)

        geojson = {
            "type": info.geojson.type,
            "coordinates": json.loads(json.dumps(info.geojson.coordinates))
        }

        geom_query = f"""
            UPDATE "{info.table}"
            SET geom = ST_GeomFromGeoJSON('{json.dumps(geojson)}')
            WHERE gid = {result[0]['gid']};
        """

        await con.fetch(geom_query)
        
        return {"status": True, "gid": result[0]['gid']}

@router.delete("/delete_row/", tags=["Tables"])
async def delete_row(
        request: Request,
        info: models.DeleteRow
    ):

    pool = request.app.state.databases[f'{info.database}_pool']

    async with pool.acquire() as con:
        
        query = f"""
            DELETE FROM "{info.table}"
            WHERE gid = {info.gid};
        """

        await con.fetch(query)
        
        return {"status": True}

@router.post("/create_table/", tags=["Tables"])
async def create_table(
        request: Request,
        info: models.CreateTable
    ):

    pool = request.app.state.databases[f'{info.database}_pool']

    async with pool.acquire() as con:
        
        query = f"""
            CREATE TABLE "{info.table}"(
            gid SERIAL PRIMARY KEY
        """

        for column in info.columns:
            query += f""", "{column.column_name}" {column.column_type} """

        query += ")"

        await con.fetch(query)

        geom_query = f"""
            SELECT AddGeometryColumn ('public','{info.table}','geom',{info.srid},'{info.geometry_type}',2);
        """
        
        await con.fetch(geom_query)
        
        return {"status": True}

@router.delete("/delete_table/", tags=["Tables"])
async def delete_table(
        request: Request,
        info: models.DeleteTable
    ):

    pool = request.app.state.databases[f'{info.database}_pool']

    async with pool.acquire() as con:
        
        query = f"""
            DROP TABLE IF EXISTS "{info.table}";
        """

        await con.fetch(query)
        
        return {"status": True}

@router.get("/tables.json", tags=["Tables"])
async def tables(request: Request):
    """
    Method used to return a list of tables available to query for vector tiles.
    """

    def get_detail_url(table: object) -> str:
        """Return tile url for layer """
        url = str(request.base_url)
        url += f"api/v1/table/{table['database']}/{table['schema']}/{table['name']}.json"
        return url
    def get_viewer_url(table: object) -> str:
        """Return tile url for layer """
        url = str(request.base_url)
        url += f"viewer/{table['database']}/{table['schema']}/{table['name']}"
        return url
    db_tables = await utilities.get_tables_metadata(request.app)
    for table in db_tables:
        table['detailurl'] = get_detail_url(table)
        table['viewerurl'] = get_viewer_url(table)

    return db_tables

@router.get("/{database}/{scheme}/{table}.json", tags=["Tables"])
async def table_json(database: str, scheme: str, table: str, request: Request):
    """
    Method used to return a information for a given table.
    """

    def get_tile_url() -> str:
        """Return tile url for layer """
        url = str(request.base_url)
        url += f"api/v1/tiles/{database}/{scheme}/{table}"
        url += "/{z}/{x}/{y}.pbf"

        return url

    def get_viewer_url() -> str:
        """Return viewer url for layer """
        url = str(request.base_url)
        url += f"viewer/{database}/{scheme}/{table}"

        return url

    return {
        "id": f"{scheme}.{table}",
        "schema": scheme,
        "tileurl": get_tile_url(),
        "viewerurl": get_viewer_url(),
        "properties": await utilities.get_table_columns(database, scheme, table, request.app),
        "geometrytype": await utilities.get_table_geometry_type(database, scheme, table, request.app),
        "type": "table",
        "minzoom": 0,
        "maxzoom": 22,
        "bounds": await utilities.get_table_bounds(database, scheme, table, request.app),
        "center": await utilities.get_table_center(database, scheme, table, request.app)
    }

@router.post("/statistics/", tags=["Tables"])
async def statistics(info: models.StatisticsModel, request: Request):

    pool = request.app.state.databases[f'{info.database}_pool']

    async with pool.acquire() as con:

        final_results= {}
        cols = []
        col_names = []
        distinct = False
        general_stats = False

        for aggregrate in info.aggregate_columns:
            if aggregrate.type == 'distinct':
                distinct = True
            else:
                general_stats = True
                cols.append(f"""{aggregrate.type }("{aggregrate.column}") as {aggregrate.type}_{aggregrate.column}""")
                col_names.append(f"{aggregrate.type}_{aggregrate.column}")

        if general_stats:
            formatted_columns = ','.join(cols)
            query = f"""
                SELECT {formatted_columns}
                FROM "{info.table}"
            """
            
            query += await utilities.generate_where_clause(info, con)

            data = await con.fetchrow(query)

            for col in col_names:
                final_results[col] = data[col]

        if distinct:
            for aggregrate in info.aggregate_columns:
                if aggregrate.type == 'distinct':
                    query = f"""SELECT DISTINCT("{aggregrate.column}"), {aggregrate.group_method}("{aggregrate.group_column}") FROM "{info.table}" """

                    query += await utilities.generate_where_clause(info, con)

                    query += f""" GROUP BY "{aggregrate.column}" ORDER BY "{aggregrate.group_method}" DESC"""

                    data = await con.fetch(query)

                    final_results[f"distinct_{aggregrate.column}_{aggregrate.group_method}_{aggregrate.group_column}"] = data

        return {
            "results": final_results,
            "status": "SUCCESS"
        }

@router.post("/bins/", tags=["Tables"])
async def bins(info: models.BinsModel, request: Request):

    pool = request.app.state.databases[f'{info.database}_pool']

    async with pool.acquire() as con:
        results = [

        ]
        query = f"""
            SELECT MIN("{info.column}"),MAX("{info.column}")
            FROM "{info.table}"
        """

        query += await utilities.generate_where_clause(info, con)

        data = await con.fetchrow(query)

        group_size = (data['max'] - data['min']) / info.number_of_bins

        for group in range(info.number_of_bins):
            if group == 0:
                min = data['min']
                max = group_size
            else:
                min = group*group_size
                max = (group+1)*group_size
            query = f"""
                SELECT COUNT(*)
                FROM "{info.table}"
                WHERE "{info.column}" > {min}
                AND "{info.column}" <= {max}
            """

            query += await utilities.generate_where_clause(info, con, True)

            data = await con.fetchrow(query)

            results.append({
                "min": min,
                "max": max,
                "count": data['count']
            })

        return {
            "results": results,
            "status": "SUCCESS"
        }

@router.post("/numeric_breaks/", tags=["Tables"])
async def numeric_breaks(info: models.NumericBreaksModel, request: Request):

    pool = request.app.state.databases[f'{info.database}_pool']

    async with pool.acquire() as con:
        results = [

        ]
        
        if info.break_type == "quantile":
            query = f"""
                SELECT {info.break_type}_bins(array_agg(CAST("{info.column}" AS integer)), {info.number_of_breaks}) 
                FROM "{info.table}"
            """
        else:
            query = f"""
                SELECT {info.break_type}_bins(array_agg("{info.column}"), {info.number_of_breaks}) 
                FROM "{info.table}"
            """

        query += await utilities.generate_where_clause(info, con)

        break_points = await con.fetchrow(query)

        min_query = f"""
            SELECT MIN("{info.column}")
            FROM "{info.table}"
        """

        min_query += await utilities.generate_where_clause(info, con)

        min_number = await con.fetchrow(min_query)

        for index, max_number in enumerate(break_points[f"{info.break_type}_bins"]):
            if index == 0:
                min = min_number['min']
                max = max_number
            else:
                min = break_points[f"{info.break_type}_bins"][index-1]
                max = max_number
            query = f"""
                SELECT COUNT(*)
                FROM "{info.table}"
                WHERE "{info.column}" > {min}
                AND "{info.column}" <= {max}
            """

            query += await utilities.generate_where_clause(info, con, True)

            data = await con.fetchrow(query)

            results.append({
                "min": min,
                "max": max,
                "count": data['count']
            })

        return {
            "results": results,
            "status": "SUCCESS"
        }

@router.post("/custom_break_values/", tags=["Tables"])
async def custom_break_values(info: models.CustomBreaksModel, request: Request):

    pool = request.app.state.databases[f'{info.database}_pool']

    async with pool.acquire() as con:
        results = [

        ]        

        for break_range in info.breaks:
            min = break_range.min
            max = break_range.max

            query = f"""
                SELECT COUNT(*)
                FROM "{info.table}"
                WHERE "{info.column}" > {min}
                AND "{info.column}" <= {max}
            """

            query += await utilities.generate_where_clause(info, con, True)

            data = await con.fetchrow(query)

            results.append({
                "min": min,
                "max": max,
                "count": data['count']
            })

        return {
            "results": results,
            "status": "SUCCESS"
        }
