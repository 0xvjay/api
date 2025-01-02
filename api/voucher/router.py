import logging
from typing import List

from fastapi import APIRouter, Depends, Request, status
from pydantic import UUID4

from api.auth.permissions import VoucherPermissions
from api.database import DBSession
from api.exceptions import DetailedHTTPException

from .exceptions import VoucherNameOrCodeExists, VoucherNotFound
from .schemas import (
    VoucherCreateSchema,
    VoucherOutMinimalSchema,
    VoucherOutSchema,
    VoucherUpdateSchema,
)
from .service import voucher_crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vouchers", tags=["vouchers"])


@router.get(
    "/",
    response_model=List[VoucherOutMinimalSchema],
    dependencies=[Depends(VoucherPermissions.read)],
)
async def read_vouchers(request: Request, db_session: DBSession):
    try:
        result = await voucher_crud.list(request=request, db_session=db_session)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch vouchers: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/{voucher_id}",
    response_model=VoucherOutSchema,
    dependencies=[Depends(VoucherPermissions.read)],
)
async def read_voucher(request: Request, db_session: DBSession, voucher_id: UUID4):
    try:
        result = await voucher_crud.get(
            request=request, db_session=db_session, id=voucher_id
        )
        if result is None:
            raise VoucherNotFound()
        return result
    except VoucherNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch voucher {voucher_id}: {str(e)}")
        raise DetailedHTTPException()


@router.post(
    "/",
    response_model=VoucherOutMinimalSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(VoucherPermissions.create)],
)
async def add_voucher(
    request: Request, db_session: DBSession, voucher: VoucherCreateSchema
):
    try:
        db_voucher = await voucher_crud.get_by_name_or_code(
            db_session=db_session, name=voucher.name, code=voucher.code
        )
        if db_voucher is not None:
            raise VoucherNameOrCodeExists()
        result = await voucher_crud.create(
            request=request, db_session=db_session, schema=voucher
        )
        return result
    except VoucherNameOrCodeExists:
        raise
    except Exception as e:
        logger.exception(f"Failed to create voucher: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/{voucher_id}",
    response_model=VoucherOutMinimalSchema,
    dependencies=[Depends(VoucherPermissions.update)],
)
async def edit_voucher(
    request: Request,
    db_session: DBSession,
    voucher: VoucherUpdateSchema,
    voucher_id: UUID4,
):
    try:
        db_voucher = await voucher_crud.get(
            request=request, db_session=db_session, id=voucher_id
        )
        if db_voucher is None:
            raise VoucherNotFound()
        existing_voucher = await voucher_crud.get_by_name_or_code(
            db_session=db_session, name=voucher.name, code=voucher.code
        )
        if existing_voucher is not None:
            raise VoucherNameOrCodeExists()
        result = await voucher_crud.update(
            request=request, db_session=db_session, db_obj=db_voucher, schema=voucher
        )
        return result
    except (VoucherNameOrCodeExists, VoucherNotFound):
        raise
    except Exception as e:
        logger.exception(f"Failed to update voucher {voucher_id}: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/{voucher_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(VoucherPermissions.delete)],
)
async def remove_voucher(request: Request, db_session: DBSession, voucher_id: UUID4):
    try:
        db_voucher = await voucher_crud.get(
            request=request, db_session=db_session, id=voucher_id
        )
        if db_voucher is None:
            raise VoucherNotFound()
        await voucher_crud.delete(
            request=request, db_session=db_session, db_obj=db_voucher
        )
        return
    except VoucherNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete voucher {voucher_id}: {str(e)}")
        raise DetailedHTTPException()
