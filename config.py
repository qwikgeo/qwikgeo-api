import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import Request, Response
from fastapi_cache import FastAPICache

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
CACHE_AGE_IN_SECONDS = int(os.getenv('CACHE_AGE_IN_SECONDS'))
MAX_FEATURES_PER_TILE = int(os.getenv('MAX_FEATURES_PER_TILE'))
SECRET_KEY = os.getenv('SECRET_KEY')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
JWT_TOKEN_EXPIRE_IN_MINUTES = os.getenv('JWT_TOKEN_EXPIRE_IN_MINUTES')

NUMERIC_FIELDS = ['bigint','bigserial','double precision','integer','smallint','real','smallserial','serial','numeric','money']


def key_builder(
    func,
    namespace: Optional[str] = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
):
    prefix = FastAPICache.get_prefix()
    cache_key = f"{prefix}:{namespace}:{request.headers['authorization']}:{func.__module__}:{func.__name__}:{args}:{kwargs}"
    return cache_key