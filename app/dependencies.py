from fastapi import HTTPException
from fastapi.security import HTTPBearer
from app.main import app
from app.services.crud import (
    AIFeedBackCrudService,
    UserCrudService,
)
from app.services.openSearch import OpenSearchService


oauth2_bearer = HTTPBearer()


def raise_db_connection_error(e):
    raise HTTPException(
        status_code=500, detail=f"OpenSearch connection failed with error: {e}"
    )


def get_opensearch_service():
    try:
        return OpenSearchService(openseach_client=app.openseach_client)
    except Exception as e:
        raise_db_connection_error(e)


def get_user_db_service():
    try:
        collection = app.db_instance["user"]
        table = UserCrudService(collection)
        return table
    except Exception as e:
        raise_db_connection_error(e)


def get_feedback_db_service():
    try:
        collection = app.db_instance["ai-search-feetback"]
        table = AIFeedBackCrudService(collection)
        return table
    except Exception as e:
        raise_db_connection_error(e)


def get_log_db_service():
    try:
        collection = app.db_instance["prompt_logger"]
        table = AIFeedBackCrudService(collection)
        return table
    except Exception as e:
        raise_db_connection_error(e)
