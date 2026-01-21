from pathlib import Path
from uuid import UUID
from fastapi import UploadFile
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from google.genai import types


_model=None

def get_embedding_model():
    global _model
    if not _model:
        _model=SentenceTransformer("all-MiniLM-L6-v2")
    return _model

UPLOAD_DIR=Path("files")
UPLOAD_DIR.mkdir(exist_ok=True)

def save_and_extract(file:UploadFile,chat_id:UUID):
    chat_dir=UPLOAD_DIR / str(chat_id)
    chat_dir.mkdir(exist_ok=True)
    file_name=str(file.filename)
    file_path=chat_dir / file_name

    try:

        content=file.file.read()
        print(content)
        with open(file_path,"wb") as f:
            f.write(content)

        ext=file_path.suffix.lower()
        text=None
        
        if ext in [".txt",".md"]:
            with open(file_path,"r",encoding="utf-8") as f:
                text=f.read()

        elif ext == ".pdf":
            reader=PdfReader(file_path)
            text=""

            for page in reader.pages:
                page_text=page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    

        return text , file_path

    finally:
        file.file.close()

        
def chunk_given_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    text_size = len(text)
    while start < text_size:
        end = min(start + chunk_size,text_size)
        chunk = text[start:end]

        if end < text_size:
            last_stop = chunk.rfind(". ")
            last_break = chunk.rfind("\n")
            split_point = max(last_break, last_stop)

            if split_point > chunk_size / 2:
                chunk = chunk[:split_point + 1]

        chunks.append(chunk.strip())
        start += (chunk_size - overlap)

    return chunks

def generate_embeddings(chunks:list[str], batch_size : int = 20 ):
    
    model=get_embedding_model()

    embeddings=model.encode(chunks,batch_size=batch_size)

    return embeddings





