from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str

    @field_validator("database_url")
    def validate_db_url(cls,v):
        if not v:
            raise ValueError("Please set 'DATABASE_URL' in .env...")
        return v

    class Config:
        env_file=".env"

    
    




settings=Settings()  # type: ignore

