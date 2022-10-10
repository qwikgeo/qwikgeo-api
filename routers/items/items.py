"""QwikGeo API - Items"""

import json
import os
import shutil
from typing import List
from functools import reduce
from fastapi import APIRouter, Request, HTTPException, Depends
from tortoise.expressions import Q
from tortoise.query_utils import Prefetch

import routers.items.models as models
import utilities
import db_models
import config

router = APIRouter()

@router.get(
    path="/",
    response_model=List[db_models.Item_Pydantic],
    responses={
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def items(
    user_name: int=Depends(utilities.get_token_header)
):
    """List all items."""


    user_groups = await utilities.get_user_groups(user_name)

    portal_items = await db_models.Item_Pydantic.from_queryset(
        db_models.Item.all().prefetch_related(
            Prefetch("item_read_access_list", queryset=db_models.ItemReadAccessList.filter(
                reduce(lambda x, y: x | y, [Q(name=group) for group in user_groups])
                )
            )
        )
    )

    return portal_items


@router.get(
    path="/tables",
    response_model=List[db_models.Table_Pydantic],
    responses={
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def tables(
    user_name: int=Depends(utilities.get_token_header)
):
    """List all tables."""

    user_groups = await utilities.get_user_groups(user_name)

    portal_items = await db_models.Item_Pydantic.from_queryset(
        db_models.Item.filter(item_type='table').prefetch_related(
            Prefetch("item_read_access_list", queryset=db_models.ItemReadAccessList.filter(
                reduce(lambda x, y: x | y, [Q(name=group) for group in user_groups]))
            )
        )
    )

    portal_ids = []

    for item in portal_items:
        portal_ids.append(item.portal_id)

    portal_tables = await db_models.Table_Pydantic.from_queryset(
        db_models.Table.filter(portal_id_id__in=portal_ids)
    )

    return portal_tables

@router.get(
    path="/tables/table/{table_id}",
    response_model=db_models.Table_Pydantic,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def table(
    table_id: str,
    user_name: int=Depends(utilities.get_token_header)
):
    """Get a table."""

    await utilities.validate_table_access(
        table=table_id,
        user_name=user_name
    )

    portal_table = await db_models.Table_Pydantic.from_queryset_single(
        db_models.Table.get(table_id=table_id)
    )

    item = await db_models.Item_Pydantic.from_queryset_single(
        db_models.Item.get(portal_id=portal_table.portal_id.portal_id)
    )

    await db_models.Item.filter(
        portal_id=portal_table.portal_id.portal_id
    ).update(views=item.views+1)

    return portal_table

@router.post(
    path="/tables/edit_row_attributes",
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def edit_row_attributes(
    request: Request,
    info: models.EditRowAttributes,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Update a table's attributes.
    More information at https://docs.qwikgeo.com/items/#edit-row-attributes
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
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
                raise HTTPException(
                    status_code=400,
                    detail=f"""Column: {field} is not a column for {info.table}.
                    Please use one of the following columns. {string_columns}""")
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

@router.post(
    path="/tables/edit_row_geometry",
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def edit_row_geometry(
    request: Request,
    info: models.EditRowGeometry,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Update a table's geometry.
    More information at https://docs.qwikgeo.com/items/#edit-row-geometry
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
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

@router.post(
    path="/tables/add_column",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {"status": True}
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def add_column(
    request: Request,
    info: models.AddColumn,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a new column for a table.
    More information at https://docs.qwikgeo.com/items/#add-column
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
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

@router.delete(
    path="/tables/delete_column",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {"status": True}
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def delete_column(
    request: Request,
    info: models.DeleteColumn,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Delete a column for a table.
    More information at https://docs.qwikgeo.com/items/#delete-column
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
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

@router.post(
    path="/tables/add_row",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "status": True,
                        "gid": 0
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def add_row(
    request: Request,
    info: models.AddRow,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a new row for a table.
    More information at https://docs.qwikgeo.com/items/#add-row
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
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
                raise HTTPException(
                    status_code=400,
                    detail=f"""Column: {column.column_name} is not a column for {info.table}.
                    Please use one of the following columns. {string_columns}"""
                )
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

@router.delete(
    path="/tables/delete_row",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {"status": True}
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def delete_row(
    request: Request,
    info: models.DeleteRow,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Delete a row for a table.
    More information at https://docs.qwikgeo.com/items/#delete-row
    """

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

@router.post(
    path="/tables/create_table",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {"status": True}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def create_table(
    request: Request,
    info: models.CreateTable,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a new table.
    More information at https://docs.qwikgeo.com/items/#create-table
    """

    pool = request.app.state.database

    new_table_id = utilities.get_new_table_id()

    async with pool.acquire() as con:

        query = f"""
            CREATE TABLE "user_data.{new_table_id}"(
            gid SERIAL PRIMARY KEY
        """

        for column in info.columns:
            query += f""", "{column.column_name}" {column.column_type} """

        query += ")"

        await con.fetch(query)

        geom_query = f"""
            SELECT AddGeometryColumn ('user_data','{new_table_id}','geom',{info.srid},'{info.geometry_type}',2);
        """

        await con.fetch(geom_query)

        await utilities.create_table(
            username=user_name,
            table_id=new_table_id,
            title=info.title,
            tags=info.tags,
            description=info.description,
            searchable=info.searchable,
            read_access_list=info.read_access_list,
            write_access_list=info.write_access_list

        )

        return {"status": True}

@router.delete(
    path="/tables/delete_table",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {"status": True}
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def delete_table(
    request: Request,
    info: models.DeleteTable,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Delete a table.
    More information at https://docs.qwikgeo.com/items/#delete-table
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name,
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

@router.post(
    path="/tables/statistics",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "results": {
                            "count_gid": 19,
                            "avg_deed_ac": 64.28666666666666,
                            "distinct_first_name_count_first_name": [
                                {
                                    "first_name": "",
                                    "count": 3
                                },
                                {
                                    "first_name": "COLE",
                                    "count": 3
                                },
                                {
                                    "first_name": "% BAS",
                                    "count": 2
                                }
                            ]
                        },
                        "status": "SUCCESS"
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def statistics(
    info: models.StatisticsModel,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Retrieve statistics for a table.
    More information at https://docs.qwikgeo.com/items/#statistics
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        final_results= {}
        cols = []
        col_names = []
        distinct = False
        general_stats = False

        for aggregate in info.aggregate_columns:
            if aggregate.type == 'distinct':
                distinct = True
            else:
                general_stats = True
                cols.append(f"""
                {aggregate.type }("{aggregate.column}") as {aggregate.type}_{aggregate.column}
                """)
                col_names.append(f"{aggregate.type}_{aggregate.column}")

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
            for aggregate in info.aggregate_columns:
                if aggregate.type == 'distinct':
                    query = f"""
                    SELECT DISTINCT("{aggregate.column}"), {aggregate.group_method}("{aggregate.group_column}") 
                    FROM "{info.table}" """

                    query += await utilities.generate_where_clause(info, con)

                    query += f"""
                    GROUP BY "{aggregate.column}"
                    ORDER BY "{aggregate.group_method}" DESC"""

                    data = await con.fetch(query)

                    final_results[
                        f"""distinct_{aggregate.column}_{aggregate.group_method}_{aggregate.group_column}"""
                    ] = data

        return {
            "results": final_results,
            "status": "SUCCESS"
        }

@router.post(
    path="/tables/bins",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "min": 0.0,
                                "max": 145.158,
                                "count": 15993
                            },
                            {
                                "min": 145.158,
                                "max": 290.316,
                                "count": 1088
                            },
                        ],
                        "status": "SUCCESS"
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def bins(
    info: models.BinsModel,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Retrieve a numerical column's bins for a table.
    More information at https://docs.qwikgeo.com/items/#bins
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
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
                minimum = data['min']
                maximum = group_size
            else:
                minimum = group*group_size
                maximum = (group+1)*group_size
            query = f"""
                SELECT COUNT(*)
                FROM "{info.table}"
                WHERE "{info.column}" > {minimum}
                AND "{info.column}" <= {maximum}
            """

            query += await utilities.generate_where_clause(info, con, True)

            data = await con.fetchrow(query)

            results.append({
                "min": minimum,
                "max": maximum,
                "count": data['count']
            })

        return {
            "results": results,
            "status": "SUCCESS"
        }

@router.post(
    path="/tables/numeric_breaks",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "min": 0.0,
                                "max": 145.158,
                                "count": 15993
                            },
                            {
                                "min": 145.158,
                                "max": 290.316,
                                "count": 1088
                            },
                        ],
                        "status": "SUCCESS"
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def numeric_breaks(
    info: models.NumericBreaksModel,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Retrieve a numerical column's breaks for a table.
    More information at https://docs.qwikgeo.com/items/#numeric-breaks
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
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
                minimum = min_number['min']
                maximum = max_number
            else:
                minimum = break_points[f"{info.break_type}_bins"][index-1]
                maximum = max_number
            query = f"""
                SELECT COUNT(*)
                FROM "{info.table}"
                WHERE "{info.column}" > {minimum}
                AND "{info.column}" <= {maximum}
            """

            query += await utilities.generate_where_clause(info, con, True)

            data = await con.fetchrow(query)

            results.append({
                "min": minimum,
                "max": maximum,
                "count": data['count']
            })

        return {
            "results": results,
            "status": "SUCCESS"
        }

@router.post(
    path="/tables/custom_break_values",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "min": 0.0,
                                "max": 145.158,
                                "count": 15993
                            },
                            {
                                "min": 145.158,
                                "max": 290.316,
                                "count": 1088
                            },
                        ],
                        "status": "SUCCESS"
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def custom_break_values(
    info: models.CustomBreaksModel,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Retrieve custom break values for a column for a table.
    More information at https://docs.qwikgeo.com/items/#numeric-breaks
    """

    await utilities.validate_table_access(
        table=info.table,
        user_name=user_name
    )

    pool = request.app.state.database

    async with pool.acquire() as con:
        results = [

        ]

        for break_range in info.breaks:
            minimum = break_range.min
            maximum = break_range.max

            query = f"""
                SELECT COUNT(*)
                FROM "{info.table}"
                WHERE "{info.column}" > {minimum}
                AND "{info.column}" <= {maximum}
            """

            query += await utilities.generate_where_clause(info, con, True)

            data = await con.fetchrow(query)

            results.append({
                "min": minimum,
                "max": maximum,
                "count": data['count']
            })

        return {
            "results": results,
            "status": "SUCCESS"
        }
