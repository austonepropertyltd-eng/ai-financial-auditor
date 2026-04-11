from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Financial Auditor"
    PROJECT_VERSION: str = "0.1.0"
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    MODEL_NAME: str = Field("gpt-4o-mini", env="MODEL_NAME")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    DATABASE_URL: str = Field("postgresql+asyncpg://user:password@localhost/financial_auditor", env="DATABASE_URL")
    DEBUG: bool = Field(False, env="DEBUG")

    class Config:
        env_file = ".env"


settings = Settings()
