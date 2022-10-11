"""QwikGeo API - Collections"""

import os
import json
import shutil
from typing import Optional
from functools import reduce
from fastapi import Request, APIRouter, Depends, status, Response, HTTPException
from starlette.responses import FileResponse
from pygeofilter.backends.sql import to_sql_where
from pygeofilter.parsers.ecql import parse
from tortoise.expressions import Q
from tortoise.query_utils import Prefetch

import routers.collections.models as models
import utilities
import db_models
import config

router = APIRouter()

@router.get(
    path="/",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "collections": [
                            {
                                "id": "{scheme}.{table}",
                                "title": "string",
                                "description": "string",
                                "keywords": ["string"],
                                "links": [
                                    {
                                        "type": "application/json",
                                        "rel": "self",
                                        "title": "This document as JSON",
                                        "href": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}"
                                    }
                                ],
                                "geometry": "point",
                                "extent": {
                                    "spatial": {
                                        "bbox": [
                                            -180,
                                            -90,
                                            180,
                                            90
                                        ],
                                        "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                                    }
                                },
                                "itemType": "feature"
                            }
                        ]
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
async def collections(
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Get a list of collections available to query.
    More information at https://docs.qwikgeo.com/collections/#collections
    """

    url = str(request.base_url)

    db_tables = []

    user_groups = await utilities.get_user_groups(user_name)

    table_items = await db_models.Item.filter(item_type='table').prefetch_related(
        Prefetch("item_read_access_list", queryset=db_models.ItemReadAccessList.filter(
                reduce(lambda x, y: x | y, [Q(name=group) for group in user_groups])
            ))
        )

    if len(table_items) > 0:
        tables = await db_models.Table_Pydantic.from_queryset(
            db_models.Table.filter(
                reduce(lambda x, y: x | y, [
                    Q(portal_id_id=table.portal_id) for table in table_items
                ])
            )
        )

        for table in tables:
            table_metadata = await db_models.Item_Pydantic.from_queryset_single(
                db_models.Item.get(portal_id=table.portal_id.portal_id)
            )
            db_tables.append(
                {
                    "id" : f"user_data.{table.table_id}",
                    "title" : table_metadata.title,
                    "description" : table_metadata.description,
                    "keywords": table_metadata.tags,
                    "links": [
                        {
                            "type": "application/json",
                            "rel": "self",
                            "title": "This document as JSON",
                            "href": f"{url}api/v1/collections/user_data.{table.table_id}"
                        }
                    ],
                    "geometry": await utilities.get_table_geometry_type(
                        scheme="user_data",
                        table=table.table_id,
                        app=request.app
                    ),
                    "extent": {
                        "spatial": {
                            "bbox": await utilities.get_table_bounds(
                                scheme="user_data",
                                table=table.table_id,
                                app=request.app
                            ),
                            "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                        }
                    },
                    "itemType": "feature"
                }
            )

    return {"collections": db_tables}

@router.get(
    path="/{scheme}.{table}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "id": "{scheme}.{table}",
                        "title": "string",
                        "description": "string",
                        "keywords": ["string"],
                        "links": [
                            {
                                "type": "application/json",
                                "rel": "self",
                                "title": "Items as GeoJSON",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items"
                            },
                            {
                                "type": "application/json",
                                "rel": "queryables",
                                "title": "Queryables for this collection as JSON",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/queryables"
                            },
                            {
                                "type": "application/json",
                                "rel": "tiles",
                                "title": "Tiles as JSON",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles"
                            }
                        ],
                        "geometry": "point",
                        "extent": {
                            "spatial": {
                                "bbox": [
                                    -180,
                                    -90,
                                    180,
                                    90
                                ],
                                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                            }
                        },
                        "itemType": "feature"
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
async def collection(
    scheme: str,
    table: str,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Get information about a collection.
    More information at https://docs.qwikgeo.com/collections/#collection
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name
    )

    table_metadata = await db_models.Table_Pydantic.from_queryset_single(
        db_models.Table.get(table_id=table)
    )

    item_metadata = await db_models.Item_Pydantic.from_queryset_single(
        db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
    )

    url = str(request.base_url)

    return {
        "id": f"{scheme}.{table}",
        "title" : item_metadata.title,
        "description" : item_metadata.description,
        "keywords": item_metadata.tags,
        "links": [
            {
                "type": "application/json",
                "rel": "self",
                "title": "This document as JSON",
                "href": f"{url}api/v1/collections/{scheme}.{table}"
            },
            {
                "type": "application/json",
                "rel": "items",
                "title": "Items as GeoJSON",
                "href": f"{url}api/v1/collections/{scheme}.{table}/items"
            },
            {
                "type": "application/json",
                "rel": "queryables",
                "title": "Queryables for this collection as JSON",
                "href": f"{url}api/v1/collections/{scheme}.{table}/queryables"
            },
            {
                "type": "application/json",
                "rel": "tiles",
                "title": "Tiles as JSON",
                "href": f"{url}api/v1/collections/{scheme}.{table}/tiles"
            }
        ],
        "geometry": await utilities.get_table_geometry_type(
            scheme="user_data",
            table=table_metadata.table_id,
            app=request.app
        ),
        "extent": {
            "spatial": {
                "bbox": await utilities.get_table_bounds(
                    scheme=scheme,
                    table=table,
                    app=request.app
                ),
                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            }
        },
        "itemType": "feature"
    }

@router.get(
    path="/{scheme}.{table}/queryables",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "$id": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/queryables",
                        "title": "string",
                        "type": "object",
                        "$schema": "http://json-schema.org/draft/2019-09/schema",
                        "properties": {
                            "string": {
                                "title": "string",
                                "type": "numeric"
                            }
                        }
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
async def queryables(
    scheme: str,
    table: str,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Get queryable information about a collection.
    More information at https://docs.qwikgeo.com/collections/#queryables
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name
    )

    table_metadata = await db_models.Table_Pydantic.from_queryset_single(
        db_models.Table.get(table_id=table)
    )

    item_metadata = await db_models.Item_Pydantic.from_queryset_single(
        db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
    )

    url = str(request.base_url)

    queryable = {
        "$id": f"{url}api/v1/collections/{scheme}.{table}/queryables",
        "title": item_metadata.title,
        "type": "object",
        "$schema": "http://json-schema.org/draft/2019-09/schema",
        "properties": {}
    }

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table}'
            AND column_name != 'geom';
        """

        db_fields = await con.fetch(sql_field_query)

        for field in db_fields:
            data_type = 'string'
            if field['data_type'] in config.NUMERIC_FIELDS:
                data_type = 'numeric'
            queryable['properties'][field['column_name']] = {
                "title": field['column_name'],
                "type": data_type
            }

        return queryable

@router.get(
    path="/{scheme}.{table}/items",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [
                                        -88.8892,
                                        36.201015
                                    ]
                                },
                                "properties": {},
                                "id": 1
                            }
                        ],
                        "numberMatched": 56,
                        "numberReturned": 10,
                        "links": [
                            {
                                "type": "application/json",
                                "rel": "self",
                                "title": "This document as GeoJSON",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items"
                            },
                            {
                                "type": "application/json",
                                "title": "{scheme}.{table}",
                                "rel": "collection",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}"
                            }
                        ]
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
async def items(
    scheme: str,
    table: str,
    request: Request,
    bbox: str=None,
    limit: int=100,
    offset: int=0,
    properties: str="*",
    sortby: str="gid",
    filter: str=None,
    srid: int=4326,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Get geojson from a collection.
    More information at https://docs.qwikgeo.com/collections/#items
    """

    url = str(request.base_url)

    await utilities.validate_table_access(
        table=table,
        user_name=user_name
    )

    blacklist_query_parameters = ["bbox","limit","offset","properties","sortby","filter"]

    new_query_parameters = []

    for query in request.query_params:
        if query not in blacklist_query_parameters:
            new_query_parameters.append(query)

    column_where_parameters = ""

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table}'
            AND column_name != 'geom';
        """

        db_fields = await con.fetch(sql_field_query)

        if properties == '*':
            properties = ""
            for field in db_fields:
                column = field['column_name']
                properties += f'"{column}",'
            properties = properties[:-1]

        if new_query_parameters:

            for field in db_fields:
                if field['column_name'] in new_query_parameters:
                    if len(column_where_parameters) != 0:
                        column_where_parameters += " AND "
                    column_where_parameters += f""" {field['column_name']} = '{request.query_params[field['column_name']]}' """

        if filter is not None:

            field_mapping = {}

            for field in db_fields:
                field_mapping[field['column_name']] = field['column_name']

            ast = parse(filter)
            filter = to_sql_where(ast, field_mapping)

        if filter is not None and column_where_parameters != "":
            filter += f" AND {column_where_parameters}"
        elif filter is None:
            filter = column_where_parameters

        results = await utilities.get_table_geojson(
            scheme=scheme,
            table=table,
            limit=limit,
            offset=offset,
            properties=properties,
            sort_by=sortby,
            bbox=bbox,
            filter=filter,
            srid=srid,
            app=request.app
        )

        results['links'] = [
            {
                "type": "application/json",
                "rel": "self",
                "title": "This document as GeoJSON",
                "href": request.url._url
            },
            {
                "type": "application/json",
                "title": f"{scheme}.{table}",
                "rel": "collection",
                "href": f"{url}api/v1/collections/{scheme}.{table}"
            }
        ]

        return results

@router.post(
    path="/{scheme}.{table}/items",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                -88.8892,
                                36.201015
                            ]
                        },
                        "properties": {},
                        "id": 1
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
async def create_item(
    scheme: str,
    table: str,
    info: models.Geojson,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Create a new item to a collection.
    More information at https://docs.qwikgeo.com/collections/#create-item
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table}'
        AND column_name != 'geom'
        AND column_name != 'gid';
        """

        db_fields = await con.fetch(sql_field_query)

        db_columns = []

        db_column_types = {}

        for field in db_fields:
            db_columns.append(field['column_name'])
            db_column_types[field['column_name']] = {
                "used": False,
                "type": field['data_type']
            }

        string_columns = ",".join(db_columns)

        input_columns = ""
        values = ""
        
        for column in info.properties:
            if column not in db_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"""Column: {column} is not a column for {table}.
                    Please use one of the following columns. {string_columns}"""
                )
            input_columns += f""""{column}","""
            if db_column_types[column]['type'] in config.NUMERIC_FIELDS:
                values += f"""{float(info.properties[column])},"""
            else:
                values += f"""'{info.properties[column]}',"""
            
            db_column_types[column]['used'] = True
        
        for column in db_column_types:
            if db_column_types[column]['used'] == False:
                raise HTTPException(
                    status_code=400,
                    detail=f"""Column {column} was not used. Add {column} to your properties."""
                )

        input_columns = input_columns[:-1]
        values = values[:-1]

        query = f"""
            INSERT INTO user_data."{table}" ({input_columns})
            VALUES ({values})
            RETURNING gid;
        """

        result = await con.fetch(query)

        geojson = {
            "type": info.geometry.type,
            "coordinates": json.loads(json.dumps(info.geometry.coordinates))
        }

        geom_query = f"""
            UPDATE user_data."{table}"
            SET geom = ST_GeomFromGeoJSON('{json.dumps(geojson)}')
            WHERE gid = {result[0]['gid']};
        """

        await con.fetch(geom_query)

        if os.path.exists(f'{os.getcwd()}/cache/user_data{table}'):
            shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table}')

        info.properties['gid'] = result[0]['gid']

        info.id = result[0]['gid']

        return info

@router.get(
    path="/{scheme}.{table}/items/{id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                -88.8892,
                                36.201015
                            ]
                        },
                        "properties": {},
                        "id": 1,
                        "links": [
                            {
                                "type": "application/json",
                                "rel": "self",
                                "title": "This document as GeoJSON",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items/1"
                            },
                            {
                                "type": "application/json",
                                "title": "items as GeoJSON",
                                "rel": "items",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items"
                            },
                            {
                                "type": "application/json",
                                "title": "{scheme}.{table}",
                                "rel": "collection",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}"
                            }
                        ]
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
async def item(
    scheme: str,
    table: str,
    id: str,
    request: Request,
    properties: str="*",
    srid: int=4326,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Get geojson for one item of a collection.
    More information at https://docs.qwikgeo.com/collections/#item
    """

    url = str(request.base_url)

    await utilities.validate_table_access(
        table=table,
        user_name=user_name
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table}'
            AND column_name != 'geom';
        """

        db_fields = await con.fetch(sql_field_query)

        if properties == '*':
            properties = ""
            for field in db_fields:
                column = field['column_name']
                properties += f'"{column}",'
            properties = properties[:-1]

        results = await utilities.get_table_geojson(
            scheme=scheme,
            table=table,
            filter=f"gid = '{id}'",
            properties=properties,
            srid=srid,
            app=request.app
        )

        results['features'][0]['links'] = [
            {
                "type": "application/json",
                "rel": "self",
                "title": "This document as GeoJSON",
                "href": request.url._url
            },
            {
                "type": "application/json",
                "title": "items as GeoJSON",
                "rel": "items",
                "href": f"{url}api/v1/collections/{scheme}.{table}/items"
            },
            {
                "type": "application/json",
                "title": f"{scheme}.{table}",
                "rel": "collection",
                "href": f"{url}api/v1/collections/{scheme}.{table}"
            }
        ]

        return results['features'][0]

@router.put(
    path="/{scheme}.{table}/items/{id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                -88.8892,
                                36.201015
                            ]
                        },
                        "properties": {},
                        "id": 1
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
async def update_item(
    scheme: str,
    table: str,
    id: int,
    info: models.Geojson,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Update an item in a collection.
    More information at https://docs.qwikgeo.com/collections/#update-item
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table}'
        AND column_name != 'geom'
        AND column_name != 'gid';
        """

        db_fields = await con.fetch(sql_field_query)

        db_columns = []

        db_column_types = {}

        for field in db_fields:
            db_columns.append(field['column_name'])
            db_column_types[field['column_name']] = {
                "type": field['data_type'],
                "used": False,
            }

        string_columns = ",".join(db_columns)

        exist_query = f"""
        SELECT count(*)
        FROM user_data."{table}"
        WHERE gid = {id}
        """

        exists = await con.fetchrow(exist_query)

        if exists['count'] == 0:
            raise HTTPException(
                    status_code=400,
                    detail=f"""Item {info.id} does not exist."""
                )

        query = f"""
            UPDATE user_data."{table}"
            SET 
        """
        
        for column in info.properties:
            if column not in db_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"""Column: {column} is not a column for {table}.
                    Please use one of the following columns. {string_columns}"""
                )
            if db_column_types[column]['type'] in config.NUMERIC_FIELDS:
                query += f"{column} = {info.properties[column]},"
            else:
                query += f"{column} = '{info.properties[column]}',"
            
            db_column_types[column]['used'] = True
        
        for column in db_column_types:
            if db_column_types[column]['used'] == False:
                raise HTTPException(
                    status_code=400,
                    detail=f"""Column {column} was not used. Add {column} to your properties."""
                )

        query = query[:-1]

        query += f" WHERE gid = {info.id};"

        await con.fetch(query)

        geojson = {
            "type": info.geometry.type,
            "coordinates": json.loads(json.dumps(info.geometry.coordinates))
        }

        geom_query = f"""
            UPDATE user_data."{table}"
            SET geom = ST_GeomFromGeoJSON('{json.dumps(geojson)}')
            WHERE gid = {id};
        """

        await con.fetch(geom_query)

        if os.path.exists(f'{os.getcwd()}/cache/user_data_{table}'):
            shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table}')

        return info

@router.patch(
    path="/{scheme}.{table}/items/{id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                -88.8892,
                                36.201015
                            ]
                        },
                        "properties": {},
                        "id": 1
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
async def modify_item(
    scheme: str,
    table: str,
    id: int,
    info: models.Geojson,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Modify an item in a collection.
    More information at https://docs.qwikgeo.com/collections/#modify-item
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table}'
        AND column_name != 'geom'
        AND column_name != 'gid';
        """

        db_fields = await con.fetch(sql_field_query)

        db_columns = []

        db_column_types = {}

        for field in db_fields:
            db_columns.append(field['column_name'])
            db_column_types[field['column_name']] = {
                "type": field['data_type']
            }

        string_columns = ",".join(db_columns)

        exist_query = f"""
        SELECT count(*)
        FROM user_data."{table}"
        WHERE gid = {id}
        """

        exists = await con.fetchrow(exist_query)

        if exists['count'] == 0:
            raise HTTPException(
                    status_code=400,
                    detail=f"""Item {info.id} does not exist."""
                )

        query = f"""
            UPDATE user_data."{table}"
            SET 
        """
        
        for column in info.properties:
            if column not in db_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"""Column: {column} is not a column for {table}.
                    Please use one of the following columns. {string_columns}"""
                )
            if db_column_types[column]['type'] in config.NUMERIC_FIELDS:
                query += f"{column} = {info.properties[column]},"
            else:
                query += f"{column} = '{info.properties[column]}',"

        query = query[:-1]

        query += f" WHERE gid = {id};"

        await con.fetch(query)

        geojson = {
            "type": info.geometry.type,
            "coordinates": json.loads(json.dumps(info.geometry.coordinates))
        }

        geom_query = f"""
            UPDATE user_data."{table}"
            SET geom = ST_GeomFromGeoJSON('{json.dumps(geojson)}')
            WHERE gid = {id};
        """

        await con.fetch(geom_query)

        if os.path.exists(f'{os.getcwd()}/cache/user_data_{table}'):
            shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table}')

        return info

@router.delete(
    path="/{scheme}.{table}/items/{id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "status": True
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
async def delete_item(
    scheme: str,
    table: str,
    id: int,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Delete an item in a collection.
    More information at https://docs.qwikgeo.com/collections/#delete-item
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:
        query = f"""
            DELETE FROM user_data."{table}"
            WHERE gid = {id};
        """

        await con.fetch(query)

        if os.path.exists(f'{os.getcwd()}/cache/user_data_{table}'):
            shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table}')

        return {"status": True}

@router.get(
    path="/{scheme}.{table}/tiles",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "id": "{scheme}.{table}",
                        "title": "string",
                        "description": "string",
                        "links": [
                            {
                                "type": "application/json",
                                "rel": "self",
                                "title": "This document as JSON",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles"
                            },
                            {
                                "type": "application/vnd.mapbox-vector-tile",
                                "rel": "item",
                                "title": "This collection as Mapbox vector tiles",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}",
                                "templated": True
                            },
                            {
                                "type": "application/json",
                                "rel": "describedby",
                                "title": "Metadata for this collection in the TileJSON format",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/{tile_matrix_set_id}/metadata",
                                "templated": True
                            }
                        ],
                        "tileMatrixSetLinks": [
                            {
                                "tileMatrixSet": "WorldCRS84Quad",
                                "tileMatrixSetURI": "http://schemas.opengis.net/tms/1.0/json/examples/WorldCRS84Quad.json"
                            }
                        ]
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
async def tiles(
    scheme: str,
    table: str,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Get tile information about a collection.
    More information at https://docs.qwikgeo.com/collections/#tiles
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name
    )

    table_metadata = await db_models.Table_Pydantic.from_queryset_single(
        db_models.Table.get(table_id=table)
    )

    item_metadata = await db_models.Item_Pydantic.from_queryset_single(
        db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
    )

    url = str(request.base_url)

    mvt_path = "{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}"

    tile_info = {
        "id": f"{scheme}.{table}",
        "title": item_metadata.title,
        "description": item_metadata.description,
        "links": [
            {
                "type": "application/json",
                "rel": "self",
                "title": "This document as JSON",
                "href": f"{url}api/v1/collections/{scheme}.{table}/tiles",
            },
            {
                "type": "application/vnd.mapbox-vector-tile",
                "rel": "item",
                "title": "This collection as Mapbox vector tiles",
                "href": f"{url}api/v1/collections/{scheme}.{table}/tiles/{mvt_path}",
                "templated": True
            },
            {
                "type": "application/json",
                "rel": "describedby",
                "title": "Metadata for this collection in the TileJSON format",
                "href": f"{url}api/v1/collections/{scheme}.{table}/tiles/{{tile_matrix_set_id}}/metadata",
                "templated": True
            }
        ],
        "tileMatrixSetLinks": [
            {
                "tileMatrixSet": "WorldCRS84Quad",
                "tileMatrixSetURI": "http://schemas.opengis.net/tms/1.0/json/examples/WorldCRS84Quad.json"
            }
        ]
    }

    return tile_info

@router.get(
    path="/{scheme}.{table}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/vnd.mapbox-vector-tile": {}
            }
        },
        204: {
            "description": "No Content",
            "content": {
                "application/vnd.mapbox-vector-tile": {}
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
async def tile(
    scheme: str,
    table: str,
    tile_matrix_set_id: str,
    tile_matrix: int,
    tile_row: int,
    tile_col: int,
    request: Request,
    fields: Optional[str] = None,
    cql_filter: Optional[str] = None,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Get a vector tile for a given table.
    More information at https://docs.qwikgeo.com/collections/#tile
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name
    )

    pbf, tile_cache = await utilities.get_tile(
        scheme=scheme,
        table=table,
        tile_matrix_set_id=tile_matrix_set_id,
        z=tile_matrix,
        x=tile_row,
        y=tile_col,
        fields=fields,
        cql_filter=cql_filter,
        app=request.app
    )

    response_code = status.HTTP_200_OK

    max_cache_age = config.CACHE_AGE_IN_SECONDS

    if fields is not None and cql_filter is not None:
        max_cache_age = 0

    if tile_cache:
        return FileResponse(
            path=f'{os.getcwd()}/cache/{scheme}_{table}/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}',
            media_type="application/vnd.mapbox-vector-tile",
            status_code=response_code,
            headers = {
                "Cache-Control": f"max-age={max_cache_age}",
                "tile-cache": 'true'
            }
        )

    if pbf == b"":
        response_code = status.HTTP_204_NO_CONTENT

    return Response(
        content=bytes(pbf),
        media_type="application/vnd.mapbox-vector-tile",
        status_code=response_code,
        headers = {
            "Cache-Control": f"max-age={max_cache_age}",
            "tile-cache": 'false'
        }
    )

@router.get(
    path="/{scheme}.{table}/tiles/{tile_matrix_set_id}/metadata",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "tilejson": "3.0.0",
                        "name": "{scheme}.{table}",
                        "tiles": "http://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/WorldCRS84Quad/{tile_matrix}/{tile_row}/{tile_col}?f=mvt",
                        "minzoom": "0",
                        "maxzoom": "22",
                        "attribution": "string",
                        "description": "string",
                        "vector_layers": [
                            {
                                "id": "{scheme}.{table}",
                                "description": "string",
                                "minzoom": 0,
                                "maxzoom": 22,
                                "fields": {}
                            }
                        ]
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
async def tiles_metadata(
    scheme: str,
    table: str,
    tile_matrix_set_id: str,
    request: Request,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Get tile metadata for a given table.
    More information at https://docs.qwikgeo.com/collections/#tiles-metadata
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name
    )

    table_metadata = await db_models.Table_Pydantic.from_queryset_single(
        db_models.Table.get(table_id=table)
    )

    item_metadata = await db_models.Item_Pydantic.from_queryset_single(
        db_models.Item.get(portal_id=table_metadata.portal_id.portal_id)
    )

    url = str(request.base_url)

    mvt_path = f"{tile_matrix_set_id}/{{tile_matrix}}/{{tile_row}}/{{tile_col}}?f=mvt"

    metadata = {
        "tilejson": "3.0.0",
        "name": f"{scheme}.{table}",
        "tiles": f"{url}api/v1/collections/{scheme}.{table}/tiles/{mvt_path}",
        "minzoom": "0",
        "maxzoom": "22",
        # "bounds": "-124.953634,-16.536406,109.929807,66.969298",
        # "center": "-84.375000,44.951199,5",
        "attribution": None,
        "description": item_metadata.description,
        "vector_layers": [
            {
                "id": f"{scheme}.{table}",
                "description": item_metadata.description,
                "minzoom": 0,
                "maxzoom": 22,
                "fields": {}
            }
        ]
    }

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table}'
            AND column_name != 'geom';
        """

        db_fields = await con.fetch(sql_field_query)

        for field in db_fields:
            data_type = 'string'
            if field['data_type'] in config.NUMERIC_FIELDS:
                data_type = 'numeric'
            metadata['vector_layers'][0]['fields'][field['column_name']] = data_type

        return metadata

@router.get(
    path="/{scheme}.{table}/tiles/cache_size",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "size_in_gigabytes": 0
                    }
                }
            }
        }
    }
)
async def get_tile_cache_size(
    scheme: str,
    table: str,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Get size of cache for table.
    More information at https://docs.qwikgeo.com/collections/#cache-size
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name
    )

    table_metadata = await db_models.Table_Pydantic.from_queryset_single(
        db_models.Table.get(table_id=table)
    )

    size = 0

    cache_path = f'{os.getcwd()}/cache/user_data_{table_metadata.table_id}'

    if os.path.exists(cache_path):
        for path, dirs, files in os.walk(cache_path):
            for file in files:
                file_path = os.path.join(path, file)
                size += os.path.getsize(file_path)

    return {"size_in_gigabytes": size*.000000001}

@router.delete(
    path="/{scheme}.{table}/tiles/cache",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "status": "deleted"
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
async def delete_tile_cache(
    scheme: str,
    table: str,
    user_name: int=Depends(utilities.get_token_header)
):
    """
    Delete cache for a table.
    More information at https://docs.qwikgeo.com/collections/#delete-cache
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name
    )

    table_metadata = await db_models.Table_Pydantic.from_queryset_single(
        db_models.Table.get(table_id=table)
    )

    utilities.delete_user_tile_cache(table_metadata.table_id)

    return {"status": "deleted"}

