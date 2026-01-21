# For the initial setup to a new database, to create required tables 
# and pgvector extension...

import sys
import os
from psycopg.connection_async import AsyncConnection
from psycopg.rows import dict_row
import asyncio

from dotenv import load_dotenv


load_dotenv()


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

DB_URL=os.getenv("DATABASE_URL")

async def migrate():
    if not DB_URL:
        raise ValueError("DATABASE_URL not available")
        
    async with await AsyncConnection.connect(
        DB_URL,
        row_factory=dict_row #type:ignore
    ) as conn:
        async with conn.cursor() as cur:
            await cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await cur.execute("DROP TABLE IF EXISTS message CASCADE")

            await cur.execute(
                            """
                            CREATE TABLE IF NOT EXISTS chat(
                                id UUID PRIMARY KEY,
                                files TEXT[],
                                created_at TIMESTAMP DEFAULT NOW()
                            )
                            """
                            )
            
            await cur.execute(
                            """
                            CREATE TABLE IF NOT EXISTS message(
                                id SERIAL PRIMARY KEY,
                                chat_id UUID REFERENCES chat(id) ON DELETE CASCADE,
                                role VARCHAR(20),
                                content TEXT,
                                file_name TEXT,
                                created_at TIMESTAMP DEFAULT NOW()
                            )
                            """
                            )
            
            await cur.execute(
                            """
                            CREATE TABLE IF NOT EXISTS rawdoc(
                                id SERIAL PRIMARY KEY,
                                embedding vector(384),
                                content TEXT,
                                idx INTEGER,    
                                chat_id UUID REFERENCES chat(id) ON DELETE CASCADE,
                                created_at TIMESTAMP DEFAULT NOW()
                            )
                            """
                            )
            
            await cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_embed
                    ON rawdoc USING hnsw (embedding vector_cosine_ops)
                    """)

            await conn.commit()

    print("Migration Ran Successfully...")


if __name__=="__main__":
    print("RUNNING Migrations.")
    asyncio.run(migrate())