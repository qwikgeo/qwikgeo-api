"""FastGeoTable App - Database Setup"""
from fastapi import FastAPI
import asyncpg

import config
import bins_sql

async def connect_to_db(app: FastAPI) -> None:
    """
    Connect to all databases.
    """
    app.state.databases = {}
    for database in config.DATABASES.items():
        app.state.databases[f'{database[0]}_pool'] = await asyncpg.create_pool(
            dsn=f"postgres://{database[1]['username']}:{database[1]['password']}@{database[1]['host']}:{database[1]['port']}/{database[0]}",
            min_size=1,
            max_size=10,
            max_queries=50000,
            max_inactive_connection_lifetime=300,
            timeout=180 # 3 Minutes
        )

        async with app.state.databases[f'{database[0]}_pool'].acquire() as con:

            await con.fetchrow(bins_sql.equal_interval_bins_sql)
            await con.fetchrow(bins_sql.head_tail_bins_sql)
            await con.fetchrow(bins_sql.quantile_bins_sql)
            await con.fetchrow(bins_sql.jenk_bins_sql_1)
            await con.fetchrow(bins_sql.jenk_bins_sql_2)

async def close_db_connection(app: FastAPI) -> None:
    """
    Close connection for all databases.
    """
    for database in config.DATABASES:
        await app.state.databases[f'{database}_pool'].close()
