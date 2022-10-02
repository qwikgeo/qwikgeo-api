import json
import os
import shutil
from functools import reduce
from fastapi import APIRouter, Request, HTTPException, Depends
from tortoise.expressions import Q

import routers.tables.models as models
import utilities
import db_models
import config

router = APIRouter()

@router.get("/", tags=["Tables"])
async def tables(
        user_name: int=Depends(utilities.get_token_header)
    ):

    user_groups = await utilities.get_user_groups(user_name)

    tables = await db_models.Table_Pydantic.from_queryset(db_models.Table.filter(reduce(lambda x, y: x | y, [Q(read_access_list__contains=[group]) for group in user_groups])))

    return tables

@router.get("/table/{table_id}/", tags=["Tables"])
async def table(
        table_id: str,
        request: Request,
        user_name: int=Depends(utilities.get_token_header)
    ):

    await utilities.validate_table_access(
        table=table_id,
        user_name=user_name,
        app=request.app
    )

    table = await db_models.Table_Pydantic.from_queryset_single(db_models.Table.get(table_id=table_id))

    await db_models.Table.filter(table_id=table_id).update(views=table.views+1)

    return table

@router.post("/edit_row_attributes/", tags=["Tables"])
async def edit_row_attributes(
        request: Request,
        info: models.EditRowAttributes,
        user_name: int=Depends(utilities.get_token_header)
    ):

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
        app=request.app,
        write_access=True
    )

    pool = request.app.state.database

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

        numeric_field_types = config.NUMERIC_FIELDS

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

        if os.path.exists(f'{os.getcwd()}/cache/{info.scheme}_{info.table}'):
            shutil.rmtree(f'{os.getcwd()}/cache/{info.scheme}_{info.table}')

        return {"status": True}

@router.post("/edit_row_geometry/", tags=["Tables"])
async def edit_row_geometry(
        request: Request,
        info: models.EditRowGeometry,
        user_name: int=Depends(utilities.get_token_header)
    ):

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
        app=request.app,
        write_access=True
    )

    pool = request.app.state.database

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
        info: models.AddColumn,
        user_name: int=Depends(utilities.get_token_header)
    ):

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
        app=request.app,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        query = f"""
            ALTER TABLE "{info.table}"
            ADD COLUMN "{info.column_name}" {info.column_type};
        """

        await con.fetch(query)

        if os.path.exists(f'{os.getcwd()}/cache/{info.scheme}_{info.table}'):
            shutil.rmtree(f'{os.getcwd()}/cache/{info.scheme}_{info.table}')
        
        return {"status": True}

@router.delete("/delete_column/", tags=["Tables"])
async def delete_column(
        request: Request,
        info: models.DeleteColumn,
        user_name: int=Depends(utilities.get_token_header)
    ):

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:
        
        query = f"""
            ALTER TABLE "{info.table}"
            DROP COLUMN IF EXISTS "{info.column_name}";
        """

        await con.fetch(query)

        if os.path.exists(f'{os.getcwd()}/cache/{info.scheme}_{info.table}'):
            shutil.rmtree(f'{os.getcwd()}/cache/{info.scheme}_{info.table}')
        
        return {"status": True}

@router.post("/add_row/", tags=["Tables"])
async def add_row(
        request: Request,
        info: models.AddRow,
        user_name: int=Depends(utilities.get_token_header)
    ):

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
        app=request.app,
        write_access=True
    )

    pool = request.app.state.database

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

        if os.path.exists(f'{os.getcwd()}/cache/{info.scheme}_{info.table}'):
            shutil.rmtree(f'{os.getcwd()}/cache/{info.scheme}_{info.table}')
        
        return {"status": True, "gid": result[0]['gid']}

@router.delete("/delete_row/", tags=["Tables"])
async def delete_row(
        request: Request,
        info: models.DeleteRow,
        user_name: int=Depends(utilities.get_token_header)
    ):

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
        app=request.app,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:
        
        query = f"""
            DELETE FROM "{info.table}"
            WHERE gid = {info.gid};
        """

        await con.fetch(query)

        if os.path.exists(f'{os.getcwd()}/cache/{info.scheme}_{info.table}'):
            shutil.rmtree(f'{os.getcwd()}/cache/{info.scheme}_{info.table}')
        
        return {"status": True}

@router.post("/create_table/", tags=["Tables"])
async def create_table(
        request: Request,
        info: models.CreateTable,
        user_name: int=Depends(utilities.get_token_header)
    ):

    pool = request.app.state.database

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
        info: models.DeleteTable,
        user_name: int=Depends(utilities.get_token_header)
    ):

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
        app=request.app,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:
        
        query = f"""
            DROP TABLE IF EXISTS "{info.table}";
        """

        await con.fetch(query)

        if os.path.exists(f'{os.getcwd()}/cache/{info.scheme}_{table}'):
            shutil.rmtree(f'{os.getcwd()}/cache/{info.scheme}_{table}')
        
        return {"status": True}

@router.post("/statistics/", tags=["Tables"])
async def statistics(info: models.StatisticsModel, request: Request, user_name: int=Depends(utilities.get_token_header)):

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
        app=request.app
    )

    pool = request.app.state.database

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
async def bins(info: models.BinsModel, request: Request, user_name: int=Depends(utilities.get_token_header)):

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
        app=request.app
    )

    pool = request.app.state.database

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
async def numeric_breaks(info: models.NumericBreaksModel, request: Request, user_name: int=Depends(utilities.get_token_header)):

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
        app=request.app
    )

    pool = request.app.state.database

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
async def custom_break_values(info: models.CustomBreaksModel, request: Request, user_name: int=Depends(utilities.get_token_header)):

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
        app=request.app
    )

    pool = request.app.state.database

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
