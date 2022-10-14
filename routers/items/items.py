"""QwikGeo API - Items"""


from typing import List
from functools import reduce
from fastapi import APIRouter, HTTPException, Depends, status
from tortoise.expressions import Q
from tortoise.query_utils import Prefetch
import tortoise

import utilities
import db_models
import authentication_handler

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
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    List all items.
    More information at https://docs.qwikgeo.com/items/#items
    """


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
    path="/{portal_id}",
    response_model=db_models.Item_Pydantic,
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
    portal_id: str,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get an item.
    More information at https://docs.qwikgeo.com/items/#item
    """


    user_groups = await utilities.get_user_groups(user_name)

    try:
        portal_item = await db_models.Item_Pydantic.from_queryset_single(
            db_models.Item.get(portal_id=portal_id)
        )

        access_list = await db_models.ItemReadAccessList.filter(
            reduce(lambda x, y: x | y, [Q(name=group) for group in user_groups])
        )

        if access_list == []:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='No access to item.'
            )

        return portal_item

    except (tortoise.exceptions.DoesNotExist, tortoise.exceptions.OperationalError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Item does not exist.'
        ) from exc
