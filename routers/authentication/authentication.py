from passlib.hash import bcrypt
from tortoise.contrib.fastapi import HTTPNotFoundError
from fastapi import APIRouter, HTTPException, Depends, status
from tortoise import exceptions
import jwt
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport import requests

import db_models
import routers.authentication.models as models
import utilities
import config

router = APIRouter()

@router.post('/token', response_model=models.TokenResponse, description="Create a JWT token to authenticate with api via a valid username and password.", responses={
    401: {
        "description": "Invalid username or password",
        "content": {
            "application/json": {
                "example": {"detail": "Invalid username or password."}
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
})
async def create_token(form_data: models.Login):
    user = await utilities.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password.'
        )
    user_obj = await models.User_Pydantic.from_tortoise_orm(user)

    expire = datetime.utcnow() + timedelta(minutes=int(config.JWT_TOKEN_EXPIRE_IN_MINUTES))
    token = jwt.encode(
        {
            "username": user_obj.username,
            "exp": expire
        }, 
        config.SECRET_KEY
    )

    return {'access_token' : token, 'token_type' : 'Bearer'}

@router.post('/google_token_authenticate', response_model=models.TokenResponse, description="Create a JWT token to authenticate with api via a valid Google JWT.", responses={
    400: {
        "description": "Invalid JWT Token",
        "content": {
            "application/json": {
                "example": {"detail": "error here"}
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
})
async def google_token_authenticate(info: models.GoogleTokenAuthenticate):
    try:
        user = id_token.verify_oauth2_token(info.token, requests.Request(), config.GOOGLE_CLIENT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        user_obj = db_models.User(
            username=user['email'].split("@")[0],
            first_name=user['given_name'],
            last_name=user['family_name'],
            photo_url=user['picture'],
            email=user['email']
        )
        await user_obj.save()

    except exceptions.IntegrityError:
        pass

    expire = datetime.utcnow() + timedelta(minutes=int(config.JWT_TOKEN_EXPIRE_IN_MINUTES))
    token = jwt.encode({
        "username": user['email'].split("@")[0],
        "exp": expire
        }, config.SECRET_KEY
    )

    return {'access_token' : token, 'token_type' : 'Bearer'}

@router.post("/user", response_model=models.User_Pydantic, description="Create a new user.", responses={
    400: {
        "description": "Username already exist",
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
})
async def create_user(user: models.UserIn_Pydantic):
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
    except exceptions.IntegrityError:
        raise HTTPException(status_code=400, detail=f"Username already exist.")

@router.get("/user/{username}", response_model=models.User_Pydantic, description="Retrieve information about user.", responses={
    403: {
        "description": "No access",
        "content": {
            "application/json": {
                "example": {"detail": "You do not have access to this user."}
            }
        }
    },
    404: {
        "description": "User not found",
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
})
async def get_user(username:str, user_name: int=Depends(utilities.get_token_header)):
    if username != user_name:
        raise HTTPException(status_code=403, detail=f"You do not have access to this user.")
    try:
        user = await models.User_Pydantic.from_queryset_single(db_models.User.get(username=user_name))
        return user
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User not found.")

@router.put("/user/{username}", response_model=models.User_Pydantic, description="Update information about user.", responses={
    403: {
        "description": "No access",
        "content": {
            "application/json": {
                "example": {"detail": "You do not have access to this user."}
            }
        }
    },
    404: {
        "description": "User not found",
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
})
async def update_user(username:str, user: models.UserIn_Pydantic, user_name: int=Depends(utilities.get_token_header)):
    if username != user_name:
        raise HTTPException(status_code=403, detail=f"You do not have access to this user.")
    try:
        await db_models.User.filter(username=user_name).update(**user.dict(exclude_unset=True))
        return await models.User_Pydantic.from_queryset_single(db_models.User.get(username=user_name))
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User not found.")

@router.delete("/user/{username}", response_model=models.Status, description="Delete a user.", responses={
    200: {
        "description": "User deleted",
        "content": {
            "application/json": {
                "example": {"Deleted user."}
            }
        }
    },
    403: {
        "description": "No access",
        "content": {
            "application/json": {
                "example": {"detail": "You do not have access to this user."}
            }
        }
    },
    404: {
        "description": "User not found",
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
})
async def delete_user(username:str, user_name: int=Depends(utilities.get_token_header)):
    if username != user_name:
        raise HTTPException(status_code=403, detail=f"You do not have access to this user.")
    deleted_count = await db_models.User.filter(username=user_name).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User not found.")
    return models.Status(message=f"Deleted user.")
