from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    BACKEND_URL: str = "http://localhost:8000"

    model_config = {"env_file": ".env"}


settings = Settings()
