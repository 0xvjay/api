import logging
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status

from api.auth.permissions import ExportPermissions
from api.database import DBSession
from api.exceptions import DetailedHTTPException

from .schemas import ExportCreateSchema, ExportOutSchema
from .service import export_crud

router = APIRouter(prefix="/exports", tags=["export"])

logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=List[ExportOutSchema],
    dependencies=[Depends(ExportPermissions.read)],
)
async def read_exports(db_session: DBSession):
    try:
        result = await export_crud.list(db_session=db_session)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch exports: {str(e)}")
        raise DetailedHTTPException()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ExportPermissions.create)],
)
async def add_export(
    request: Request,
    db_session: DBSession,
    export: ExportCreateSchema,
    background_tasks: BackgroundTasks,
):
    try:
        export.created_by = request.state.user.id
        result = await export_crud.create(
            db_session=db_session, schema=export, background_tasks=background_tasks
        )
        return {
            "message": "Export started successfully",
            "id": result.id,
            "status": result.status,
        }
    except Exception as e:
        logger.exception(f"Failed to create export: {str(e)}")
        raise DetailedHTTPException()
