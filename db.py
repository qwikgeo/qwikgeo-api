"""QwikGeo API - Database Setup"""
from fastapi import FastAPI
import asyncpg

import config
import bins_sql

async def connect_to_db(app: FastAPI) -> None:
    """
    Connect to all databases.
    """
    app.state.database = {}
    
    app.state.database = await asyncpg.create_pool(
        dsn=f"postgres://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_DATABASE}",
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
