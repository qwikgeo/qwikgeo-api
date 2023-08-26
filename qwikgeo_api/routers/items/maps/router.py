"""QwikGeo API - Maps"""

import json
from typing import List
from functools import reduce
from fastapi import APIRouter, Depends
from tortoise.expressions import Q

from qwikgeo_api import utilities
from qwikgeo_api import db_models
from qwikgeo_api import authentication_handler
import qwikgeo_api.routers.items.maps.models as models

router = APIRouter()

@router.get(
    path="/",
    response_model=List[db_models.MapOut_Pydantic],
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to item."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Item does not exist."}
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
async def get_maps(
    q: str=None,
    personal :bool=False,
    limit: int=10,
    offset : int=0,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get a map.
    More information at https://docs.qwikgeo.com/maps/#map
    """

    user_groups = await utilities.get_user_groups(username)

    # if q:
    #     if personal:
    #         items = await utilities.get_multiple_items_in_database(
    #             username=username,
    #             model_name="MapOut",
    #             limit=limit,
    #             offset=offset,
    #             query_filter=Q(reduce(lambda x, y: x | y, [Q(item__read_access_list__contains=[group]) for group in user_groups]),Q(description__icontains=q)|Q(title__icontains=q))
    #         )
    #     else:
    #         items = await utilities.get_multiple_items_in_database(
    #             username=username,
    #             model_name="MapOut",
    #             limit=limit,
    #             offset=offset,
    #             query_filter=Q(Q(description__icontains=q)|Q(title__icontains=q))
    #         )
    # else:
    #     if personal:
    #         items = await utilities.get_multiple_items_in_database(
    #             username=username,
    #             model_name="MapOut",
    #             limit=limit,
    #             offset=offset,
    #             query_filter=Q(reduce(lambda x, y: x | y, [Q(read_access_list__icontains=group) for group in user_groups]))
    #         )
    #     else:
    #         items = await utilities.get_multiple_items_in_database(
    #             username=username,
    #             model_name="MapOut",
    #             limit=limit,
    #             offset=offset,
    #             query_filter=Q(reduce(lambda x, y: x | y, [Q(item_read_access_list__contains=[group]) for group in user_groups]))
    #         )

    items = await utilities.get_multiple_items_in_database(
        username=username,
        model_name="MapOut"
    )

    return items

@router.get(
    path="/{map_id}",
    response_model=db_models.MapOut_Pydantic,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to item."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Item does not exist."}
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
async def get_map(
    map_id: str,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get a map.
    More information at https://docs.qwikgeo.com/maps/#map
    """

    item = await utilities.get_item_in_database(
        username=username,
        model_name="MapOut",
        query_filter=Q(map_id=map_id)
    )

    return item

@router.post(
    path="/",
    response_model=db_models.MapOut_Pydantic,
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
async def create_map(
    item: models.Map,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Create a new map.
    More information at https://docs.qwikgeo.com/maps/#create-map
    """

    json_item = json.loads(item.json())

    json_item['user_id'] = json_item['username']

    layers = json_item['layers']

    del json_item['layers']

    new_map = await utilities.create_single_item_in_database(
        item=json_item,
        model_name="Map"
    )

    for layer in layers:
        layer['map_id'] = new_map['map_id']
        await db_models.Layer.create(**layer)

    new_item = await utilities.get_item_in_database(
        username=username,
        model_name="MapOut",
        query_filter=Q(item_id=new_map.portal_id)
    )

    return new_item

@router.put(
    path="/{map_id}",
    response_model=db_models.Map_Pydantic,
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
async def update_map(
    map_id: str,
    item: db_models.Map_Pydantic,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Create a new map.
    More information at https://docs.qwikgeo.com/maps/#update-map
    """

    await utilities.validate_item_access(
        model_name="Map",
        query_filter=Q(map_id=map_id),
        username=username,
        write_access=True
    )

    # map_item = db_models.Map_Pydantic(**item)

    await utilities.update_single_item_in_database(
        item=item,
        query_filter=Q(map_id=map_id),
        model_name="Map"
    )
    
    await db_models.Layer.filter(map_id=map_id).delete()

    json_item = json.loads(item.json())

    layers = json_item['layers']

    for layer in layers:
        layer['map_id'] = map_id
        await db_models.Layer.create(**layer)

    new_item = await utilities.get_item_in_database(
        username=username,
        model_name="Map",
        query_filter=Q(map_id=map_id)
    )

    return new_item
