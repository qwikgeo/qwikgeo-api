"""QwikGeo API - Tables"""

import os
import shutil
from typing import List
from functools import reduce
from fastapi import APIRouter, Request, Depends, HTTPException, status
from tortoise.expressions import Q
from tortoise.query_utils import Prefetch
import asyncpg

import routers.tables.models as models
import utilities
import db_models

router = APIRouter()

@router.get(
    path="/",
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
    """
    List all tables.
    More information at https://docs.qwikgeo.com/tables/#tables
    """

    user_groups = await utilities.get_user_groups(user_name)

    portal_items = await db_models.Item_Pydantic.from_queryset(
        db_models.Item.filter(item_type='table').prefetch_related(
            Prefetch("item_read_access_list", queryset=db_models.ItemReadAccessList.filter(
                reduce(lambda x, y: x | y, [Q(name=group) for group in user_groups]))
            )
        )
    )

    portal_ids = []

    for portal_item in portal_items:
        portal_ids.append(portal_item.portal_id)

    portal_tables = await db_models.Table_Pydantic.from_queryset(
        db_models.Table.filter(portal_id_id__in=portal_ids)
    )

    return portal_tables

@router.get(
    path="/{table_id}",
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
    """
    Get a table.
    More information at https://docs.qwikgeo.com/tables/#table
    """

    await utilities.validate_table_access(
        table=table_id,
        user_name=user_name
    )

    portal_table = await db_models.Table_Pydantic.from_queryset_single(
        db_models.Table.get(table_id=table_id)
    )

    portal_item = await db_models.Item_Pydantic.from_queryset_single(
        db_models.Item.get(portal_id=portal_table.portal_id.portal_id)
    )

    await db_models.Item.filter(
        portal_id=portal_table.portal_id.portal_id
    ).update(views=portal_item.views+1)

    return portal_table

@router.post(
    path="/{table_id}/add_column",
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
    table_id: str,
    info: models.AddColumn,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a new column for a table.
    More information at https://docs.qwikgeo.com/tables/#add-column
    """

    await utilities.validate_table_access(
        table=table_id,
        user_name=user_name,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        query = f"""
            ALTER TABLE user_data."{table_id}"
            ADD COLUMN "{info.column_name}" {info.column_type};
        """

        await con.fetch(query)

        if os.path.exists(f'{os.getcwd()}/cache/user_data_{table_id}'):
            shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table_id}')

        return {"status": True}

@router.delete(
    path="/{table_id}/delete_column/{column}",
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
    table_id: str,
    column: str,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Delete a column for a table.
    More information at https://docs.qwikgeo.com/tables/#delete-column
    """

    await utilities.validate_table_access(
        table=table_id,
        user_name=user_name,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        query = f"""
            ALTER TABLE user_data."{table_id}"
            DROP COLUMN IF EXISTS "{column}";
        """

        await con.fetch(query)

        if os.path.exists(f'{os.getcwd()}/cache/user_data_{table_id}'):
            shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table_id}')

        return {"status": True}

@router.post(
    path="/create_table",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "status": True,
                        "table_id": "string"
                    }
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
    More information at https://docs.qwikgeo.com/tables/#create-table
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

        return {"status": True, "table_id": new_table_id}

@router.delete(
    path="/{table_id}",
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
    table_id: str,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Delete a table.
    More information at https://docs.qwikgeo.com/tables/#delete-table
    """

    await utilities.validate_table_access(
        table=table_id,
        user_name=user_name,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        query = f"""
            DROP TABLE IF EXISTS user_data."{table_id}";
        """

        await con.fetch(query)

        if os.path.exists(f'{os.getcwd()}/cache/user_data_{table_id}'):
            shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table_id}')

        return {"status": True}

@router.post(
    path="/{table_id}/statistics",
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
    table_id: str,
    info: models.StatisticsModel,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Retrieve statistics for a table.
    More information at https://docs.qwikgeo.com/tables/#statistics
    """

    await utilities.validate_table_access(
        table=table_id,
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
                FROM user_data."{table_id}"
            """

            query += await utilities.generate_where_clause(info, con)

            try:
                data = await con.fetchrow(query)
            
            except asyncpg.exceptions.UndefinedColumnError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'One of the columns usedZ does not exist for {table_id}.'
                )

            for col in col_names:
                final_results[col] = data[col]

        if distinct:
            for aggregate in info.aggregate_columns:
                if aggregate.type == 'distinct':
                    query = f"""
                    SELECT DISTINCT("{aggregate.column}"), {aggregate.group_method}("{aggregate.group_column}") 
                    FROM user_data."{table_id}" """

                    query += await utilities.generate_where_clause(info, con)

                    query += f"""
                    GROUP BY "{aggregate.column}"
                    ORDER BY "{aggregate.group_method}" DESC"""

                    try:
                        data = await con.fetchrow(query)
                    
                    except asyncpg.exceptions.UndefinedColumnError:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'One of the columns used does not exist for {table_id}.'
                        )

                    final_results[
                        f"""distinct_{aggregate.column}_{aggregate.group_method}_{aggregate.group_column}"""
                    ] = data

        return {
            "results": final_results,
            "status": "SUCCESS"
        }

@router.post(
    path="/{table_id}/bins",
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
    table_id: str,
    info: models.BinsModel,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Retrieve a numerical column's bins for a table.
    More information at https://docs.qwikgeo.com/tables/#bins
    """

    await utilities.validate_table_access(
        table=table_id,
        user_name=user_name
    )

    pool = request.app.state.database

    async with pool.acquire() as con:
        results = [

        ]
        query = f"""
            SELECT MIN("{info.column}"),MAX("{info.column}")
            FROM user_data."{table_id}"
        """

        query += await utilities.generate_where_clause(info, con)        

        try:
            data = await con.fetchrow(query)
        
        except asyncpg.exceptions.UndefinedColumnError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Column: {info.column} does not exist for {table_id}.'
            )

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
                FROM user_data."{table_id}"
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
    path="/{table_id}/numeric_breaks",
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
    table_id: str,
    info: models.NumericBreaksModel,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Retrieve a numerical column's breaks for a table.
    More information at https://docs.qwikgeo.com/tables/#numeric-breaks
    """

    await utilities.validate_table_access(
        table=table_id,
        user_name=user_name
    )

    pool = request.app.state.database

    async with pool.acquire() as con:
        results = [

        ]

        if info.break_type == "quantile":
            query = f"""
                SELECT {info.break_type}_bins(array_agg(CAST("{info.column}" AS integer)), {info.number_of_breaks}) 
                FROM user_data."{table_id}"
            """
        else:
            query = f"""
                SELECT {info.break_type}_bins(array_agg("{info.column}"), {info.number_of_breaks}) 
                FROM user_data."{table_id}"
            """

        query += await utilities.generate_where_clause(info, con)

        try:
            break_points = await con.fetchrow(query)
        
        except asyncpg.exceptions.UndefinedColumnError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Column: {info.column} does not exist for {table_id}.'
            )

        min_query = f"""
            SELECT MIN("{info.column}")
            FROM user_data."{table_id}"
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
                FROM user_data."{table_id}"
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
    path="/{table_id}/custom_break_values",
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
    table_id: str,
    info: models.CustomBreaksModel,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Retrieve custom break values for a column for a table.
    More information at https://docs.qwikgeo.com/tables/#numeric-breaks
    """

    await utilities.validate_table_access(
        table=table_id,
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
                FROM user_data."{table_id}"
                WHERE "{info.column}" > {minimum}
                AND "{info.column}" <= {maximum}
            """

            query += await utilities.generate_where_clause(info, con, True)

            try:
                data = await con.fetchrow(query)
            
            except asyncpg.exceptions.UndefinedColumnError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Column: {info.column} does not exist for {table_id}.'
                )

            results.append({
                "min": minimum,
                "max": maximum,
                "count": data['count']
            })

        return {
            "results": results,
            "status": "SUCCESS"
        }

@router.get(
    path="/{table_id}/autocomplete",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": ["str","str"]
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
async def table_autocomplete(
    table_id: str,
    column: str,
    q: str,
    request: Request,
    limit: int=10,
    user_name: int=Depends(utilities.get_token_header),

):
    """
    Retrieve distinct values for a column in a table.
    More information at https://docs.qwikgeo.com/tables/#table-autocomplete
    """

    await utilities.validate_table_access(
        table=table_id,
        user_name=user_name
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        results = []

        query = f"""
            SELECT distinct("{column}")
            FROM user_data.{table_id}
            WHERE "{column}" ilike '%{q}%'
            ORDER BY "{column}"
            LIMIT {limit}
        """

        try:
            data = await con.fetch(query)
        
        except asyncpg.exceptions.UndefinedColumnError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Column: {column} does not exist for {table_id}.'
            )

        for row in data:
            results.append(row[column])

        return results
