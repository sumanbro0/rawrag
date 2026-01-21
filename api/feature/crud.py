from typing import LiteralString, Optional
from uuid import UUID,uuid4
from google.genai import types,Client
from loguru import logger


from core.db import AsyncSession,get_db_sync
from core.settings import settings
from .schemas import MessageCreate,MessageOut, Role
from .rag import generate_embeddings,get_embedding_model

THRESHOLD=0.5
client=Client(api_key=settings.gemini_api_key)

async def create_chat(db:AsyncSession)->UUID:
    uid=uuid4()

    await db.execute(
    "INSERT INTO chat(id) VALUES(%s)",
    (uid,) 
    )
    
    return uid

async def update_chat(id:UUID,new_file:str,db:AsyncSession)->UUID:

    await db.execute(
    "UPDATE chat SET files = array_append(files, %s) WHERE id = %s",
    (new_file,id)
    )

    return id

async def create_message(data:MessageCreate,db:AsyncSession) -> Optional[MessageOut]:

    await db.execute(
    "INSERT INTO message (chat_id, role, content, file_name)" \
    "values (%s, %s, %s, %s)" \
    "RETURNING *",
    (data.chat_id,data.role, data.content, data.file_name),
    )
    row =await db.fetchone()



    return MessageOut(**row) if row else None


def remove_null_bytes(text: str) -> str:
    """Remove null bytes from text"""
    return text.replace('\x00', '')

async def create_rawdoc(chunks:list[str],chat_id:UUID,db:AsyncSession)->bool:
    embeddings=generate_embeddings(chunks)

    cleaned_chunks=[remove_null_bytes(chunk) for chunk in chunks]

    values=[(embedding.tolist(), chunk, i, chat_id) for i,(chunk,embedding) in enumerate(zip(cleaned_chunks,embeddings))]

    await db.executemany(
        "INSERT INTO rawdoc (embedding,content,idx,chat_id)" \
        "VALUES (%s::vector, %s, %s, %s) RETURNING id",
        values
    )
    
    return True



async def get_all_messages(chat_id:UUID,db:AsyncSession):

    await db.execute(
        "SELECT * FROM message WHERE chat_id = %s ORDER BY created_at",
        (chat_id,)
    )
    results=await db.fetchall()
    return results



def get_similar_content_sync(queries:list[str],chat_id:UUID):
    res=[]
    batch_size=4
    try:
        model=get_embedding_model()
        
        for i in range(0,len(queries),batch_size):
            queries_batch=queries[i:i+batch_size]
            
            with get_db_sync() as db:
                for q in queries_batch:
                    encoded_query=model.encode(q)
                    encoded_list=encoded_query.tolist()

                    db.execute(
                        """SELECT content, 1- (embedding <=> %s::vector) as similarity
                        FROM rawdoc WHERE chat_id = %s 
                        ORDER BY similarity DESC 
                        LIMIT 5""",
                        (encoded_list, chat_id)
                        )
                    
                    results = db.fetchall()
                    res.extend(results)

                seen=set()
                unique_res=[]

                for row in sorted(res,key=lambda x:x.get("similarity",0),reverse=True):
                    if row["content"] not in seen:
                        seen.add(row["content"])
                        unique_res.append(row["content"])
                    
                return "\n".join(unique_res[:5])
            
    except Exception as e:
        logger.error(f"❌ Failed to get similar content {e}")

def make_read_files_tool(chat_id:UUID):
    # Function/Tool used by gemini to read files
    # Called by gemini automatically...

    def read_files(queries:list[str])->LiteralString:
        """Returns the merged content similar to the queries provided.
        Args:
            queries (list[str]): The queries to search for based upon users latest question.
            for eg:
                Question: What software projects are mentioned in the file?
                queries: ["Projects done by me","Projects I am working on","Projects I have worked on"...]
        
        Returns:
            LiteralString: The merged content of the files.
        """
        with open("files/test.txt","w",encoding="utf-8") as f:
            f.write("\n".join(queries))
        content=get_similar_content_sync(queries,chat_id)
        
        print("************** READ FILES ***************")
        print(content)

        return content or "Failed to read file"
    return read_files

async def talk_to_gemini(
    chat_id:UUID,
    new_question:str,
):
    config=types.GenerateContentConfig(
        tools=[make_read_files_tool(chat_id)],
        system_instruction=""""
        You are an AI assistant with RAG capabilities.
        
        - Be authentic while answering users questions, and provide relevant information from the files only.
        - While using read file tool, please make sure to include all relevent keywords/phrases as query to the tool.
        - At least use 3 queries with important keywords to the read file.

        <CRITICAL>
        - ONLY REPLY AS A PLAIN TEXT, DO NOT USE MARKDOWN FORMATTING.
        </CRITICAL>

        """
    )
  
    contents=types.Content(
            role=Role.USER,
            parts=[types.Part(text=new_question 
            )],
        )
    
    try:
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=config,
        )

        print("************** GEMINI RESPONSE ***************")
        print(response.text)

        return response.text
    except Exception as e:
        logger.error(f"❌ Failed to talk to gemini {e}")
        return "Gemini failed to reply."

