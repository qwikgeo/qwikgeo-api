"""QwikGeo API - Users"""

from typing import List
from passlib.hash import bcrypt
from fastapi import APIRouter, HTTPException, Depends
from tortoise import exceptions

from qwikgeo_api import db_models
import qwikgeo_api.routers.items.users.models as models
from qwikgeo_api import authentication_handler

router = APIRouter()

@router.post(
    path="/",
    response_model=models.UserOut_Pydantic,
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Username already exist."}
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
async def create_user(
    user: models.UserIn_Pydantic
):
    """
    Create a new user.
    More information at https://docs.qwikgeo.com/users/#create-user
    """

    try:
        user_obj = db_models.User(
            username=user.username,
            password_hash=bcrypt.hash(user.password_hash),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )
        await user_obj.save()
        return await models.UserOut_Pydantic.from_tortoise_orm(user_obj)
    except exceptions.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Username already exist.") from exc

@router.get(
    "/me",
    response_model=models.UserOut_Pydantic,
    responses={
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found."}
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
async def get_user(
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Retrieve information about user.
    More information at https://docs.qwikgeo.com/users/#user
    """

    try:
        user = await models.UserOut_Pydantic.from_queryset_single(
            db_models.User.get(username=username)
        )
        return user
    except exceptions.DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="User not found.") from exc

@router.put(
    path="/me",
    response_model=models.UserOut_Pydantic,
    responses={
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found."}
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
async def update_user(
    user: models.UserIn_Pydantic,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Update information about user.
    More information at https://docs.qwikgeo.com/users/#update-user
    """

    try:
        await db_models.User.filter(username=username).update(**user.dict(exclude_unset=True))
        return await models.UserOut_Pydantic.from_queryset_single(
            db_models.User.get(username=username)
        )
    except exceptions.DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="User not found.") from exc

@router.delete(
    path="/me",
    response_model=models.Status,
    responses={
        200: {
            "description": "User deleted",
            "content": {
                "application/json": {
                    "example": {"Deleted user."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found."}
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
async def delete_user(
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Delete a user.
    More information at https://docs.qwikgeo.com/users/#delete-user
    """

    deleted_count = await db_models.User.filter(username=username).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail="User not found.")
    return models.Status(message="Deleted user.")

@router.get(
    path="/",
    response_model=List[models.User],
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
async def get_users(
    q: str,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Return a list of users based off of searching via username.
    More information at https://docs.qwikgeo.com/users/#user-search
    """

    users= (
        await db_models.User.filter(username__icontains=q)
    )

    return users
