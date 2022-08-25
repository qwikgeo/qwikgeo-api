"""FastGeoportal App - Database Setup"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
import asyncpg


import bins_sql

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
CACHE_AGE_IN_SECONDS = int(os.getenv('CACHE_AGE_IN_SECONDS'))
MAX_FEATURES_PER_TILE = int(os.getenv('MAX_FEATURES_PER_TILE'))

async def connect_to_db(app: FastAPI) -> None:
    """
    Connect to all databases.
    """
    app.state.database = {}
    
    app.state.database = await asyncpg.create_pool(
        dsn=f"postgres://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}",
        min_size=1,
        max_size=10,
        max_queries=50000,
        max_inactive_connection_lifetime=300,
        timeout=180 # 3 Minutes
    )

    async with app.state.database.acquire() as con:

        await con.fetchrow(bins_sql.equal_interval_bins_sql)
        await con.fetchrow(bins_sql.head_tail_bins_sql)
        await con.fetchrow(bins_sql.quantile_bins_sql)
        await con.fetchrow(bins_sql.jenk_bins_sql_1)
        await con.fetchrow(bins_sql.jenk_bins_sql_2)

async def close_db_connection(app: FastAPI) -> None:
    """
    Close connection for database.
    """

    await app.state.database.close()
