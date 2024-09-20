from logging import error, info
from fastapi import FastAPI
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from langchain_huggingface import HuggingFaceEmbeddings
from openai import AsyncOpenAI
from langchain_community.vectorstores import OpenSearchVectorSearch
from app.models.settings import Settings
from app.logger import initialize_csv
from app.constants import embedding_model_dimension, IndexesEnum

# logger initialization for dev
initialize_csv()


# INITIATE SETTING, DB AND EMBEDDING MODEL WHEN APP START
@asynccontextmanager
async def lifespan(app: FastAPI):

    app.settings_instance = Settings()
    app.mongodb_client = MongoClient(
        app.settings_instance.MONGO_URL, server_api=ServerApi("1")
    )
    app.db_instance = app.mongodb_client[app.settings_instance.MONGO_DATABASENAME]
    app.embedding_model_instance = HuggingFaceEmbeddings(
        model_name=app.settings_instance.EMBEDDING_MODEL_NAME
    )
    app.llm = AsyncOpenAI(
        max_retries=2,
        api_key=app.settings_instance.LLM_API_KEY,
    )

    # vector store
    app.openseach_client = OpenSearchVectorSearch(
        app.settings_instance.DEV_OPENSEARCH_URL,
        embedding_function=app.embedding_model_instance,
        http_auth=(
            app.settings_instance.OPENSEARCH_INITIAL_ADMIN_USERNAME,
            app.settings_instance.OPENSEARCH_INITIAL_ADMIN_PASSWORD,
        ),
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        index_name=IndexesEnum.INDEX_OF_MENUS.value,
    )

    # create index
    for index in [
        IndexesEnum.INDEX_OF_MENUS.value,
        IndexesEnum.INDEX_OF_FAQ.value,
    ]:
        if not app.openseach_client.index_exists(index_name=index):
            try:
                app.openseach_client.create_index(
                    index_name=index,
                    dimension=embedding_model_dimension,
                )
            except Exception:
                error("Index not found! please check with administrator")

    # Check if database is connected
    try:
        app.db_instance.command("ping")
        info("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    yield
    app.mongodb_client.close()


app = FastAPI(lifespan=lifespan)

from app.endpoints import OpensearchApi  # noqa: E402


@app.get("/")
async def root():
    content = """
        <head>
            <meta http-equiv="refresh" content="0; url=/docs" />
        </head>
        <body>
            <p>For the API documentation, please follow this <a href="/docs">link to the documentation</a>.</p>
        </body>
    """
    return HTMLResponse(content=content)


app.include_router(OpensearchApi.router)
