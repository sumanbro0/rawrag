from typing import Annotated, AsyncGenerator
from psycopg import AsyncCursor,Connection,connect
from psycopg.connection_async import AsyncConnection
from psycopg.rows import dict_row,DictRow
from fastapi import Depends
from contextlib import contextmanager


from core.settings import settings

type AsyncSession=AsyncCursor[DictRow]
type DB=AsyncGenerator[AsyncSession]

async def get_db() -> DB:
    """
    Returns control of the POSTGRESQL cursor.
    """
    async with await AsyncConnection.connect(
        settings.database_url,
        autocommit=True,
        row_factory=dict_row #type:ignore
    ) as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            yield cur
    
DBDep= Annotated[AsyncSession,Depends(get_db)]

@contextmanager
def get_db_sync():
    conn=connect(
        settings.database_url,
        autocommit=True,
        )
    
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            yield cur
    finally:
        conn.close()


    return conn