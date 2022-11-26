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
import authentication_handler

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
    user_name: int=Depends(authentication_handler.JWTBearer())
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
    user_name: int=Depends(authentication_handler.JWTBearer())
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
    user_name: int=Depends(authentication_handler.JWTBearer())
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

        table_metadata = await db_models.Table_Pydantic.from_queryset_single(
            db_models.Table.get(table_id=table_id)
        )

        item_metadata = await db_models.Item_Pydantic.from_queryset_single(
            db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
        )

        await db_models.Item.filter(portal_id=item_metadata.portal_id).delete()

        await db_models.Table.filter(table_id=table_id).delete()

        if os.path.exists(f'{os.getcwd()}/cache/user_data_{table_id}'):
            shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table_id}')

        return {"status": True}

