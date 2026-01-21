from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import TypeVar,Generic,Optional
from enum import Enum

T=TypeVar("T")

class UUIDResponse(BaseModel):
    id:UUID

class IdResponse(BaseModel):
    id:int

class Role(str,Enum):
    USER="user"
    ASSISTANT="assistant"
    system="system"

class BaseResponseSchema(BaseModel,Generic[T]):
    data:Optional[T] = None
    message:str
    success:bool

class MessageIn(BaseModel):
    content:str
    role:Role

class MessageCreate(MessageIn):
    file_name:Optional[str]
    chat_id:UUID

class MessageOut(MessageCreate):
    id:int
    created_at:datetime

class AIQuerySchema(BaseModel):
    questions:list[str]

