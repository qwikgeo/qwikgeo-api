"""QwikGeo API - Authentication"""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from tortoise import exceptions
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests

from qwikgeo_api import db_models
import qwikgeo_api.routers.authentication.models as models
from qwikgeo_api import utilities
from qwikgeo_api import config

router = APIRouter()

@router.post(
    path='/token',
    response_model=models.TokenResponse,
    responses={
        401: {
            "description": "Unauthorized",
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
    }
)
async def create_token(
    form_data: models.Login
):
    """
    Create a JWT token to authenticate with api via a valid username and password.
    More information at https://docs.qwikgeo.com/authentication/#token
    """

    user = await utilities.authenticate_user(form_data.username, form_data.password)

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

@router.post(
    path='/google_token_authenticate',
    response_model=models.TokenResponse,
    responses={
        400: {
            "description": "Bad Request",
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
    }
)
async def google_token_authenticate(
    info: models.GoogleTokenAuthenticate
):
    """
    Create a JWT token to authenticate with api via a valid Google JWT.
    More information at https://docs.qwikgeo.com/authentication/#google-token-authenticate
    """

    try:
        user = id_token.verify_oauth2_token(info.token, requests.Request(), config.GOOGLE_CLIENT_ID)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

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
