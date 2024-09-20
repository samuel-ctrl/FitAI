import shutil
import time
from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    UploadFile,
    status,
)
from typing import List
from app.constants import USER_CUSTOM_QUERY_PROMPT
from app.dependencies import (
    get_feedback_db_service,
    get_opensearch_service,
)
from app.models.openSeachModel import (
    AIFeedbackRequest,
    SearchRequest,
    SearchResponse,
)
from app.services.JwtAuthService import JWTBearer
from app.services.crud import AIFeedBackCrudService
from app.services.openSearch import OpenSearchService

router = APIRouter(tags=["OpenSearch Support"])


@router.post(
    "/upload_files",
    description="To upload files to OpenSearch or append to existing index. allowed file formate are (*.txt , *.*.md, *.pdf, *.docx, *.doc, *.html, *.xhtml, *.csv",
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    files: List[UploadFile],
    index_name: str = Body(...),
    service: OpenSearchService = Depends(get_opensearch_service),
):
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded.")

        folder_path, filename = await service.save_uploaded_file(files)
        await service.upload_to_opensearch(
            f"{folder_path}/{filename}", index_name=index_name
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred.{e}")
    finally:
        if folder_path:
            shutil.rmtree(folder_path)
    return {"message": "Files uploaded and processed successfully."}


@router.post("/search", description="search docs for prompt.")
async def search(
    request: SearchRequest = Body(...),
    service: OpenSearchService = Depends(get_opensearch_service),
) -> SearchResponse:
    try:
        start_time = time.time()

        prompt = (
            USER_CUSTOM_QUERY_PROMPT.format(
                ALLERGIES=", ".join(request.allergies),
                HEIGHT=request.current_height,
                WEIGHT=request.current_weight,
                GOAL_WEIGHT=request.goal_weight,
                DIET_IMPROVEMENT=", ".join(request.diet_improvement),
                DIET_TYPE=", ".join(request.meal_restriction),
                FOOD_OPTIONS=", ".join(request.food_arround_me),
            )
            if not request.prompt
            else request.text
        )

        res = await service.search(request, prompt)
        duration = time.time() - start_time
        return SearchResponse(result=res, time_taken_in_seconds=f"{duration:.4f}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the request. {e}",
        )


@router.get("/ping", description="Ping: Checks if the OpenSearch cluster is alive.")
async def ping(
    _=Depends(JWTBearer()), service: OpenSearchService = Depends(get_opensearch_service)
):
    try:
        aService = service.get_aOpenSearch_client()
        status = await aService.ping()
        return {"message": "Cluster is alive" if status else "Cluster is down"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to ping OpenSearch cluster: {str(e)}"
        )


@router.post(
    "/ai_search_feedback",
    description="To provide feedback to AI search results.",
)
async def ai_search_feedbaack(
    request: AIFeedbackRequest = Body(...),
    service: AIFeedBackCrudService = Depends(get_feedback_db_service),
):
    """
    To provide feedback to AI search results.

    The request body should contain the following:
    - `text`: The text that was searched for.
    - `rating`: The rating given to the AI search results.
    - `user_id`: The ID of the user who provided the feedback.
    - `ai_response`: The response from the AI model.

    The response will contain a message indicating whether the feedback was
    provided successfully or not.
    """
    try:
        status = await service.create_feedback(request)
        if status:
            return {"message": "Feedback provided successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to provide feedback: {str(e)}"
        )


# @router.post(
#     "/bulk_chunks",
#     description="To create chunch into particular index.",
#     status_code=status.HTTP_201_CREATED,
# )
# async def add_texts(
#     request: AddTextsRequest = Body(...),
#     _=Depends(JWTBearer()),
#     service: OpenSearchService = Depends(get_opensearch),
# ) -> AddTextsResponce:
#     metadatas = []
#     if len(request.metadatas):
#         if len(request.texts) != len(request.metadatas):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Must text length and metadatas length is equal.",
#             )
#         metadatas = request.metadatas
#     else:
#         metadatas = [{}] * len(request.text)
#     try:
#         return_ids = await service.LVectorSearch.aadd_texts(
#             index_name=service.index_name,
#             texts=request.texts,
#             metadatas=metadatas,
#             bulk_size=len(request.texts),
#             max_chunk_bytes=100 * 1024 * 1024,  # 100 megabytes
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to add texts: {str(e)}")

#     return {"ids": return_ids}


# @router.delete("/bulk_chunks/")
# async def delete_chunks(
#     ids: List[str] = Body(...),
#     _=Depends(JWTBearer()),
#     service: OpenSearchService = Depends(get_opensearch),
# ):
#     if not ids:
#         raise HTTPException(status_code=400, detail="The 'ids' list cannot be empty.")

#     try:
#         await service.LVectorSearch.adelete(ids=ids)
#         return {"message": "Chunks deleted successfully."}
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Failed to delete chunks: {str(e)}"
#         )


# @router.delete(
#     "/chunk/{doc_id}",
#     description="Delete chunk: Deletes a chunk by ID.",
# )
# async def delete_chunk(
#     doc_id: str,
#     _=Depends(JWTBearer()),
#     service: OpenSearchService = Depends(get_opensearch),
# ):
#     try:
#         aService = service.get_aOpenSearch_client()
#         response = await aService.delete(index=service.index_name, id=doc_id)
#         return {"message": "Chunk deleted successfully", "result": response["result"]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to delete chunk: {str(e)}")


# @router.get("/chunk_exists/{doc_id}", description="Exists: Checks if a chunk exists.")
# async def chunk_exists(
#     doc_id: str,
#     _=Depends(JWTBearer()),
#     service: OpenSearchService = Depends(get_opensearch),
# ):
#     try:
#         aService = service.get_aOpenSearch_client()
#         exists = await aService.exists(index=service.index_name, id=doc_id)
#         return {"exists": exists}
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Failed to check if chunk exists: {str(e)}"
#         )


# @router.get(
#     "/chunk/{doc_id}",
#     description="Get chunk: Retrieves a chunk by ID.",
# )
# async def get_chunk(
#     doc_id: str,
#     _=Depends(JWTBearer()),
#     service: OpenSearchService = Depends(get_opensearch),
# ):
#     try:
#         aService = service.get_aOpenSearch_client()
#         response = await aService.get(index=service.index_name, id=doc_id)
#         return {"chunk": response["_source"]}
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Failed to retrieve chunk: {str(e)}"
#         )


# @router.put(
#     "/update_chunk/{doc_id}",
#     description="Update chunk: Partially updates a chunk by ID.",
# )
# async def update_chunk(
#     doc_id: str,
#     _=Depends(JWTBearer()),
#     doc: Any = Body(...),
#     service: OpenSearchService = Depends(get_opensearch),
# ):
#     try:
#         if not doc:
#             raise HTTPException(
#                 status_code=400, detail="The update document cannot be empty."
#             )

#         aService = service.get_aOpenSearch_client()
#         response = await aService.update(
#             index=service.index_name, id=doc_id, body={"doc": doc}
#         )
#         return {"message": "Chunk updated successfully", "result": response["result"]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to update chunk: {str(e)}")


# Below APIs are some adsitional stuff's, may be will implement later.

# @router.post(
#     "/count",
#     description="Count: Returns the number of chunks matching the query.",
# )
# async def count(
#     request: CountRequest = Body(...),
#     service: OpenSearchService = Depends(get_opensearch),
# ):
#     try:
#         aService = service.get_aOpenSearch_client()
#         action = {"text":request.prompt} # changes need
#         response = await aService.count(index=service.index_name, body=action)
#         return {"count": response["count"]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to count chunks: {str(e)}")

# @router.post(
#     "/create_index",
#     description="Create Index: Creates a new index with the specified name.",
# )
# async def create_index(
#
#     service: OpenSearchService = Depends(get_opensearch),
# ):
#     response = service.get_async_client.indices.create(
#         service.index_name, ignore=400
#     )
#     return response

# @router.post("/index/", description="To create index.")
# async def create_index(service: OpenSearchService = Depends(get_opensearch)):
#     service.LVectorSearch.create_index(
#         index_name=service.index_name,
#         dimension=embedding_model_dimension,
#     )
#     return {"message": "Index created successfully."}


# @router.post(
#     "/close",
#     description="Close Index: Closes an index, making it unavailable for search.",
# )
# async def close_index(
#
#     service: OpenSearchService = Depends(get_opensearch),
# ):
#     response = service.indices.close(service.index_name)
#     return response


# @router.post(
#     "/bulk",
#     description="Bulk: Performs multiple index, create, update, or delete operations in a single API call.",
# )
# async def bulk_operations(
#     body: Dict,
#     service: OpenSearchService = Depends(get_opensearch),
# ):
#     response = service.bulk(body=body)
#     return response


# @router.post(
#     "/clear_scroll",
#     description="Clear Scroll: Clears search contexts that are holding resources in the cluster.",
# )
# async def clear_scroll(
#     scroll_id: str,
#     service: OpenSearchService = Depends(get_opensearch),
# ):
#     response = service.clear_scroll(scroll_id=scroll_id)
#     return response


# @router.delete("/index/")
# async def delete_index(service: OpenSearchService = Depends(get_opensearch)):
#     service.LVectorSearch.delete_index(index_name=service.index_name)
#     return {"message": "Index deleted successfully."}
