import sys
from pathlib import Path

# Define Project root to Python Search paths.
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from psycopg import OperationalError
from fastapi.responses import JSONResponse
from loguru import logger

from .feature.schemas import BaseResponseSchema
from .feature.routes import router 
from core.logger import setup_logger

setup_logger()

app=FastAPI(debug=True,title="Rawrag API",version="1.0.0")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.exception_handler(OperationalError)
async def db_exception_handler(request:Request,exc:OperationalError):
    logger.error(f"❌Error CREATE_CHAT {exc}",)
     
    return JSONResponse(
        status_code=503,
        content=BaseResponseSchema(message="Database Unavailable",success=False).model_dump()
    )


@app.get("/health",operation_id="health_check",response_model=BaseResponseSchema)
async def health():
    return BaseResponseSchema(message="OK",success=True)


