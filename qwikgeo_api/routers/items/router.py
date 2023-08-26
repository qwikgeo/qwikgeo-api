"""QwikGeo API - Items"""

from typing import List
from fastapi import APIRouter, Depends
from tortoise.expressions import Q

from qwikgeo_api import utilities
from qwikgeo_api import db_models
from qwikgeo_api import authentication_handler

router = APIRouter()

@router.get(
    path="/",
    response_model=List[db_models.ItemOut_Pydantic],
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
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    List all items.
    More information at https://docs.qwikgeo.com/items/#items
    """

    db_items = await utilities.get_multiple_items_in_database(
        username=username,
        model_name="ItemOut"
    )

    return db_items

@router.get(
    path="/{item_id}",
    response_model=db_models.ItemOut_Pydantic,
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
async def item(
    item_id: str,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get an item.
    More information at https://docs.qwikgeo.com/items/#item
    """

    db_item = await utilities.get_item_in_database(
        username=username,
        model_name="ItemOut",
        query_filter=Q(portal_id=item_id)
    )

    return db_item