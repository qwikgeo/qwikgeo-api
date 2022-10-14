"""QwikGeo API - Users"""

from passlib.hash import bcrypt
from fastapi import APIRouter, HTTPException, Depends
from tortoise import exceptions

import db_models
import routers.users.models as models
import utilities
import authentication_handler

router = APIRouter()

@router.post(
    path="/user",
    response_model=models.User_Pydantic,
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
        return await models.User_Pydantic.from_tortoise_orm(user_obj)
    except exceptions.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Username already exist.") from exc

@router.get(
    "/user",
    response_model=models.User_Pydantic,
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
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Retrieve information about user.
    More information at https://docs.qwikgeo.com/users/#user
    """

    try:
        user = await models.User_Pydantic.from_queryset_single(
            db_models.User.get(username=user_name)
        )
        return user
    except exceptions.DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="User not found.") from exc

@router.put(
    path="/user",
    response_model=models.User_Pydantic,
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
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Update information about user.
    More information at https://docs.qwikgeo.com/users/#update-user
    """

    try:
        await db_models.User.filter(username=user_name).update(**user.dict(exclude_unset=True))
        return await models.User_Pydantic.from_queryset_single(
            db_models.User.get(username=user_name)
        )
    except exceptions.DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="User not found.") from exc

@router.delete(
    path="/user",
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
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Delete a user.
    More information at https://docs.qwikgeo.com/users/#delete-user
    """

    deleted_count = await db_models.User.filter(username=user_name).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail="User not found.")
    return models.Status(message="Deleted user.")

@router.get(
    path="/search",
    response_model=models.Users,
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
async def user_search(
    username: str,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Return a list of users based off of searching via username.
    More information at https://docs.qwikgeo.com/users/#user-search
    """

    users= (
        await db_models.User.filter(username__icontains=username)
    )

    return {"users": users}
