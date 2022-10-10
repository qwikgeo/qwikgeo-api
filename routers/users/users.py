"""QwikGeo API - Users"""

from passlib.hash import bcrypt
from fastapi import APIRouter, HTTPException, Depends
from tortoise import exceptions

import db_models
import routers.users.models as models
import utilities

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
    """Create a new user."""

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
    "/user/{username}",
    response_model=models.User_Pydantic,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "You do not have access to this user."}
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
async def get_user(
    username:str,
    user_name: int=Depends(utilities.get_token_header)
):
    """Retrieve information about user."""

    if username != user_name:
        raise HTTPException(status_code=403, detail="You do not have access to this user.")
    try:
        user = await models.User_Pydantic.from_queryset_single(
            db_models.User.get(username=user_name)
        )
        return user
    except exceptions.DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="User not found.") from exc

@router.put(
    path="/user/{username}",
    response_model=models.User_Pydantic,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "You do not have access to this user."}
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
async def update_user(
    username:str,
    user: models.UserIn_Pydantic,
    user_name: int=Depends(utilities.get_token_header)
):
    """Update information about user."""

    if username != user_name:
        raise HTTPException(status_code=403, detail="You do not have access to this user.")
    try:
        await db_models.User.filter(username=user_name).update(**user.dict(exclude_unset=True))
        return await models.User_Pydantic.from_queryset_single(
            db_models.User.get(username=user_name)
        )
    except exceptions.DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="User not found.") from exc

@router.delete(
    path="/user/{username}",
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
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "You do not have access to this user."}
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
    username:str,
    user_name: int=Depends(utilities.get_token_header)
):
    """Delete a user."""

    if username != user_name:
        raise HTTPException(status_code=403, detail="You do not have access to this user.")
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
    user_name: int=Depends(utilities.get_token_header)
):
    """Return a list of users based off of searching via username."""

    print(username)

    users= (
        await db_models.User.filter(username__icontains=username)
    )

    return {"users": users}
