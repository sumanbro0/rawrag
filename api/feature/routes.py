import asyncio
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from loguru import logger

from core.db import DBDep
from .crud import create_chat,create_rawdoc,create_message,update_chat,talk_to_gemini,get_all_messages
from .schemas import BaseResponseSchema,UUIDResponse,MessageIn,MessageOut,MessageCreate,Role
from constants import ALLOWED_TYPES
from .rag import chunk_given_text,save_and_extract

router=APIRouter(prefix="/chat") 


@router.post(
    "/",
    operation_id="create_chat",
    response_model=BaseResponseSchema[UUIDResponse],
    status_code=201,responses={
    400:{"model":BaseResponseSchema}
    }
)
async def create_chat_session(db:DBDep):
    try:
        id=await create_chat(db)

        return BaseResponseSchema[UUIDResponse](
            data=UUIDResponse(id=id),
            message="Chat initiated successfully",
            success=True
        )

    except Exception as e:
        logger.error(f"❌ failed to initiate chat {e}")
        return JSONResponse(
            status_code=400,
            content=BaseResponseSchema(
                success=False,
                message="Failed to initiate chat"
                ).model_dump()
            )

@router.get(
        "/{chat_id}",
        response_model=BaseResponseSchema[list[MessageOut]],
        status_code=200,
        responses={
            400:{"model":BaseResponseSchema}
        }
)
async def get_messages(chat_id:UUID,db:DBDep):

    try:
        messages=await get_all_messages(chat_id,db)
        return BaseResponseSchema[list[MessageOut]](data=[MessageOut(**message) for message in messages],message="Messages fetched...",success=True)
    
    except Exception as e:
        logger.error(f"❌ failed to load all messages {e}")
        return JSONResponse(
            status_code=400,
            content=BaseResponseSchema(
                success=False,
                message="Failed to load all messages"
                ).model_dump()
            )






@router.post(
        "/{chat_id}/message",
        operation_id="send_chat_message",
        response_model=BaseResponseSchema[list[MessageOut]],
        status_code=201,
        responses={
            415:{"model":BaseResponseSchema}
        }
    )
async def message(
    chat_id:UUID,
    db:DBDep,
    content: str = Form(...),
    file:UploadFile | None = File(None),
    ):

    if file:
        if file.content_type not in ALLOWED_TYPES:
            return JSONResponse(status_code=415,content=BaseResponseSchema(message="Unsupported Media Types",success=False))
        
        text,file_path=save_and_extract(file,chat_id)
        if not text:
            return JSONResponse(status_code=422,content=BaseResponseSchema(message="Couldnot find text content",success=False))
        
        chunks=chunk_given_text(text)

        await create_rawdoc(chunks,chat_id,db)
        await update_chat(chat_id,str(file_path),db)


    question_obj=MessageCreate(chat_id=chat_id,content=content,file_name=file.filename if file else None,role=Role.USER)
    user_question=content 
    if file:
        user_question=content + " \n\n New File Uploaded:" + str(file.filename)
    reply=await talk_to_gemini(chat_id,user_question)

    if not reply:
        return JSONResponse(status_code=400,content=BaseResponseSchema(message="Gemini failed to reply",success=False).model_dump())

    reply_obj=MessageCreate(chat_id=chat_id,content=reply,file_name=None,role=Role.ASSISTANT)

    created_q,created_r=await asyncio.gather(create_message(question_obj,db),create_message(reply_obj,db))

    if not created_q or not created_r:
        return JSONResponse(status_code=400,content=BaseResponseSchema(message="Something went wrong...",success=False).model_dump())

    return BaseResponseSchema[list[MessageOut]](data=[created_q,created_r],success=True,message="Successful Reply")


    




