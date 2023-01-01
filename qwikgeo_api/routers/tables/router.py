"""QwikGeo API - Tables"""

import os
import shutil
from typing import List
from fastapi import APIRouter, Request, Depends
from tortoise.expressions import Q

import qwikgeo_api.routers.tables.models as models
from qwikgeo_api import utilities
from qwikgeo_api import db_models
from qwikgeo_api import authentication_handler

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
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    List all tables.
    More information at https://docs.qwikgeo.com/tables/#tables
    """

    items = await utilities.get_multiple_items_in_database(
        user_name=user_name,
        model_name="Table"
    )

    return items

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
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get a table.
    More information at https://docs.qwikgeo.com/tables/#table
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name
    )

    item = await utilities.get_item_in_database(
        user_name=user_name,
        model_name="Table",
        query_filter=Q(table_id=table_id)
    )

    return item

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
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Create a new column for a table.
    More information at https://docs.qwikgeo.com/tables/#add-column
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
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
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Delete a column for a table.
    More information at https://docs.qwikgeo.com/tables/#delete-column
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
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
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Create a new table.
    More information at https://docs.qwikgeo.com/tables/#create-table
    """

    pool = request.app.state.database

    new_table_id = utilities.get_new_table_id()

    async with pool.acquire() as con:

        query = f"""
            CREATE TABLE user_data."{new_table_id}"(
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

        utilities.check_if_username_in_access_list(user_name, info.read_access_list, "read")

        utilities.check_if_username_in_access_list(user_name, info.write_access_list, "write")

        item = {
            "user_name": user_name,
            "table_id": new_table_id,
            "title": info.title,
            "tags": info.tags,
            "description": info.description,
            "searchable": info.searchable,
            "read_access_list": info.read_access_list,
            "write_access_list": info.write_access_list
        }

        await utilities.create_single_item_in_database(
            item=item,
            model_name="Table"
        )

        return {"status": True, "table_id": new_table_id}

@router.delete(
    path="/{table_id}/delete_table",
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
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Delete a table.
    More information at https://docs.qwikgeo.com/tables/#delete-table
    """

    await utilities.delete_single_item_in_database(
        user_name=user_name,
        model_name="Table",
        query_filter=Q(table_id=table_id)
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
