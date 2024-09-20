from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = False
    CLUSTER_NAME: str
    NODE_NAME: str
    DISCOVERY_SEED_HOSTS: str
    CLUSTER_INITIAL_CLUSTER_MANAGER_NODES: str
    BOOTSTRAP_MEMORY_LOCK: str
    OPENSEARCH_JAVA_OPTS: str
    OPENSEARCH_INITIAL_ADMIN_PASSWORD: str
    OPENSEARCH_INITIAL_ADMIN_USERNAME: str
    EMBEDDING_MODEL_NAME: str
    DEV_OPENSEARCH_URL: str
    LLM_API_KEY: str
    LLM_MODEL_NAME: str
    MAX_CHUNK_SIZE: int
    MAX_CHUNK_OVERLAP: int
    MONGO_DATABASENAME: str
    MONGO_URL: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_AUDIENCE: str = "fitAi"
    JWT_ISSUER: str = "fitAi"
    model_config = SettingsConfigDict(env_file=".env")
