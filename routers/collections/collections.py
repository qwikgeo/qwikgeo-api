import os
import shutil
from typing import Optional
from functools import reduce
from fastapi import Request, APIRouter, Depends, status, Response
from starlette.responses import FileResponse
from pygeofilter.backends.sql import to_sql_where
from pygeofilter.parsers.ecql import parse
from tortoise.expressions import Q
from tortoise.query_utils import Prefetch

import utilities
import db_models
import config

router = APIRouter()

@router.get("/", tags=["Collections"])
async def collections(request: Request, user_name: int=Depends(utilities.get_token_header)):
    """
    Get a list of tables available to query.

    """

    url = str(request.base_url)

    db_tables = []

    user_groups = await utilities.get_user_groups(user_name)

    table_items = await db_models.Item.filter(item_type='table').prefetch_related(Prefetch("item_read_access_list", queryset=db_models.ItemReadAccessList.filter(reduce(lambda x, y: x | y, [Q(name=group) for group in user_groups]))))

    tables = await db_models.Table_Pydantic.from_queryset(db_models.Table.filter(reduce(lambda x, y: x | y, [Q(portal_id_id=table.portal_id) for table in table_items])))

    for table in tables:
        table_metadata = await db_models.Item_Pydantic.from_queryset_single(db_models.Item.get(portal_id=table.portal_id.portal_id))
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

@router.get("/{scheme}.{table}", tags=["Collections"])
async def collection(scheme: str, table: str, request: Request, user_name: int=Depends(utilities.get_token_header)):
    """
    Get return information about a collection.

    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app
    )

    table_metadata = await db_models.Table_Pydantic.from_queryset_single(db_models.Table.get(table_id=table))

    item_metadata = await db_models.Item_Pydantic.from_queryset_single(db_models.Item.get(portal_id=table_metadata.portal_id.portal_id))

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

@router.get("/{scheme}.{table}/queryables", tags=["Collections"])
async def queryables(scheme: str, table: str, request: Request,
    user_name: int=Depends(utilities.get_token_header)):
    """
    Get queryable information about a collection.

    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app
    )

    table_metadata = await db_models.Table_Pydantic.from_queryset_single(db_models.Table.get(table_id=table))

    item_metadata = await db_models.Item_Pydantic.from_queryset_single(db_models.Item.get(portal_id=table_metadata.portal_id.portal_id))

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

@router.get("/{scheme}.{table}/items", tags=["Collections"])
async def items(scheme: str, table: str, request: Request,
    bbox: str=None, limit: int=100, offset: int=0, properties: str="*",
    sortby :str="gid", filter :str=None, srid: int=4326, user_name: int=Depends(utilities.get_token_header)):
    """
    Get geojson from a collection.

    """

    url = str(request.base_url)

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app
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

        if new_query_parameters != []:

            for field in db_fields:
                if field['column_name'] in new_query_parameters:
                    if len(column_where_parameters) != 0:
                        column_where_parameters += " AND "
                    column_where_parameters += f" {field['column_name']} = '{request.query_params[field['column_name']]}' "

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

@router.get("/{scheme}.{table}/items/{id}", tags=["Collections"])
async def item(scheme: str, table: str, id:str, request: Request,
    properties: str="*", srid: int=4326, user_name: int=Depends(utilities.get_token_header)):
    """
    Get geojson for one item of a collection.

    """

    url = str(request.base_url)

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app
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

@router.get("/{scheme}.{table}/tiles", tags=["Collections"])
async def tiles(scheme: str, table: str, request: Request,
    user_name: int=Depends(utilities.get_token_header)):
    """
    Get queryable information about a collection.

    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app
    )

    table_metadata = await db_models.Table_Pydantic.from_queryset_single(db_models.Table.get(table_id=table))

    item_metadata = await db_models.Item_Pydantic.from_queryset_single(db_models.Item.get(portal_id=table_metadata.portal_id.portal_id))

    url = str(request.base_url)

    mvt_path = "{tileMatrixSetId}/{tileMatrix}/{tileRow}/{tileCol}"

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
                "href": f"{url}api/v1/collections/{scheme}.{table}/tiles/{{tileMatrixSetId}}/metadata",
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
    "/{scheme}.{table}/tiles/{tileMatrixSetId}/{tileMatrix}/{tileRow}/{tileCol}",
    tags=["Collections"],
    summary="Endpoint to return a vector of tiles for a given table"
)
async def tile(scheme: str, table: str, tileMatrixSetId: str, tileMatrix: int, tileRow: int,
    tileCol: int, request: Request,fields: Optional[str] = None, cql_filter: Optional[str] = None,
    user_name: int=Depends(utilities.get_token_header)):
    """
    Get a vector of tiles for a given table.
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app
    )

    pbf, tile_cache = await utilities.get_tile(
        scheme=scheme,
        table=table,
        tileMatrixSetId=tileMatrixSetId,
        z=tileMatrix,
        x=tileRow,
        y=tileCol,
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
            path=f'{os.getcwd()}/cache/{scheme}_{table}/{tileMatrixSetId}/{tileMatrix}/{tileRow}/{tileCol}',
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

@router.get("/{scheme}.{table}/tiles/{tileMatrixSetId}/metadata", tags=["Collections"])
async def tiles_metadata(scheme: str, table: str, tileMatrixSetId: str, request: Request, user_name: int=Depends(utilities.get_token_header)):
    """
    Get a tile metadata for a given table.
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app
    )

    table_metadata = await db_models.Table_Pydantic.from_queryset_single(db_models.Table.get(table_id=table))

    item_metadata = await db_models.Item_Pydantic.from_queryset_single(db_models.Item.get(portal_id=table_metadata.portal_id.portal_id))

    url = str(request.base_url)

    mvt_path = f"{tileMatrixSetId}/{{tileMatrix}}/{{tileRow}}/{{tileCol}}?f=mvt"

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

@router.get("/{scheme}.{table}/tiles/cache_size", tags=["Collections"])
async def get_tile_cache_size(scheme: str, table: str, request: Request, user_name: int=Depends(utilities.get_token_header)):
    """
    Method used to a list size of cache for table.
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app
    )

    size = 0

    cache_path = f'{os.getcwd()}/cache/{scheme}_{table}'

    if os.path.exists(cache_path):     
        for path, dirs, files in os.walk(cache_path):
            for f in files:
                fp = os.path.join(path, f)
                size += os.path.getsize(fp)

    return {'size_in_gigabytes': size*.000000001}

@router.delete("/{scheme}.{table}/tiles/cache", tags=["Collections"])
async def delete_tile_cache(scheme: str, table: str, request: Request, user_name: int=Depends(utilities.get_token_header)):
    """
    Method used to delete cache for a table.
    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app
    )

    if os.path.exists(f'{os.getcwd()}/cache/{scheme}_{table}'):
        shutil.rmtree(f'{os.getcwd()}/cache/{scheme}_{table}')
        return {"status": "deleted"}
    else:
        return {"error": f"No cache at {os.getcwd()}/cache/{scheme}_{table}"}
