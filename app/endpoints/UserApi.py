from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
)
from app.core.logging import LoggerConfig
from app.dependencies import get_info_db_service
from app.models.user import InfoModel
from app.services.JwtAuthService import JWTBearer
from app.services.crud import InfoCrudService

router = APIRouter(tags=["User Support"])
logger = LoggerConfig(__name__).get_logger()


@router.post("/info", status_code=status.HTTP_201_CREATED)
async def create_info_data(
    request: InfoModel = Body(...),
    _=Depends(JWTBearer()),
    service: InfoCrudService = Depends(get_info_db_service),
) -> dict:
    try:
        await service.create_info_data(**request)
        return {"message": "Diet Plan Created"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/info/{id}", status_code=status.HTTP_200_OK)
async def get_info_data(
    id: int,
    _=Depends(JWTBearer()),
    service: InfoCrudService = Depends(get_info_db_service),
) -> dict:
    try:
        data = await service.get_info_data(id)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/info/{id}", status_code=status.HTTP_200_OK)
async def update_info_data(
    id: int,
    request: InfoModel = Body(...),
    _=Depends(JWTBearer()),
    service: InfoCrudService = Depends(get_info_db_service),
) -> dict:
    try:
        await service.update_info_data(id, request)
        return {"message": "info data Updated"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# @router.get("/dashboard", status_code=status.HTTP_200_OK)
# async def get_dashboard_data(
#     _=Depends(JWTBearer()),
#     dash_service: DashboardCrudService = Depends(get_dashboard_db_service),
#     info_service: InfoCrudService = Depends(get_info_db_service),
# ) -> dict:
#     try:
#         info_data = await info_service.get_info_data()
#         dashboard_data = await dash_service.get_dashboard_data()
#         return {
#             "message": "success",
#             "data": {"info_data": info_data, "dashboard_data": dashboard_data},
#         }
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# def get_allergies_service(db=Depends(get_db)) -> AllergiesService:
#     return PrivateAllergiesService(db)


# @router.get(
#     "",
#     status_code=200,
#     response_model=BaseResponse,
#     tags=["Allergies"],
#     summary="Allergies",
#     description="Get the list of all allergies",
# )
# async def get_allergies(
#     request: Request, service: AllergiesService = Depends(get_allergies_service)
# ):
#     logger.info(f"{request.url.path} - Get Allergies List")
#     try:
#         return await service.get_allergies()
#     except Exception as e:
#         logger.error(f"Error in Diet Improvements: {e}")
#         raise HTTPException(status_code=404, detail=str(e))


# @router.get(
#     "/{category_id}",
#     status_code=200,
#     response_model=Allergies,
#     tags=["Allergies"],
#     description="Get a allergies by id",
# )
# async def get_allergies_by_category_id(
#     request: Request,
#     category_id: str,
#     service: AllergiesService = Depends(get_allergies_service),
# ):
#     logger.info(f"{request.url.path} - Get allergy By Id")
#     try:
#         result = await service.get_allergies_by_category_id(category_id)
#         return result
#     except Exception as e:
#         logger.error(f"Error in getting allergy by id: {e}")
#         raise HTTPException(status_code=404, detail=str(e))


# @router.post(
#     "",
#     status_code=201,
#     response_model=Allergies,
#     tags=["Allergies"],
#     description="Create a allergy",
# )
# async def create_allergies(
#     allergy: AllergiesCreate,
#     request=Body(...),
#     service: AllergiesService = Depends(get_allergies_service),
# ):
#     logger.info(f"{request.url.path} - Create allergy")
#     try:
#         result = await service.create_allergy(allergy)
#         return result
#     except Exception as e:
#         logger.error(f"Error in creating allergy: {str(e)}")
#         raise HTTPException(status_code=404, detail=str(e))


# @router.put(
#     "/{category_id}",
#     status_code=200,
#     response_model=Allergies,
#     tags=["Allergies"],
#     description="Update a allergy",
# )
# async def update_allergy(
#     category_id: str,
#     allergy: AllergiesUpdate,
#     request=Body(...),
#     service: AllergiesService = Depends(get_allergies_service),
# ):
#     logger.info(f"{request.url.path} - Update allergy")
#     try:
#         result = await service.update_allergy(category_id, allergy)
#         return result
#     except Exception as e:
#         logger.error(f"Error in updating allergy: {str(e)}")
#         raise HTTPException(status_code=404, detail=str(e))


# @router.delete(
#     "/{category_id}",
#     status_code=204,
#     tags=["Allergies"],
#     description="Delete a allergy",
# )
# async def delete_allergy(
#     category_id: str,
#     request=Body(...),
#     service: AllergiesService = Depends(get_allergies_service),
# ):
#     logger.info(f"{request.url.path} - Delete allergy")
#     try:
#         await service.delete_allergy(category_id)
#     except Exception as e:
#         logger.error(f"Error in deleting allergies: {str(e)}")
#         raise HTTPException(status_code=404, detail=str(e))
