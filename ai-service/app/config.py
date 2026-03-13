from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # HuggingFace Models
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    NER_MODEL: str = "dslim/bert-base-NER"
    CLASSIFIER_MODEL: str = "facebook/bart-large-mnli"

    # FAISS
    FAISS_INDEX_DIR: str = "./data"
    EMBEDDING_DIM: int = 768  # all-mpnet-base-v2 output dim

    # MongoDB (shared with backend)
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "job_platform"

    model_config = {"env_file": ".env"}


settings = Settings()
