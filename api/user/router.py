import logging
from typing import List

from fastapi import APIRouter, Depends, Request, status
from pydantic import UUID4

from api.auth.constant import PermissionAction, PermissionObject
from api.auth.permissions import (
    CompanyPermissions,
    ProjectPermissions,
    UserPermissions,
    allow_self_access,
)
from api.database import DBSession
from api.exceptions import DetailedHTTPException
from api.order.schemas import OrderOutMinimalSchema
from api.order.service import order_crud

from .exceptions import (
    CompanyNotFound,
    ProjectNotFound,
    UserAddressNotFound,
    UserEmailOrNameExists,
    UserNotFound,
)
from .schemas import (
    CompanyCreateSchema,
    CompanyOutMinimalSchema,
    CompanyOutSchema,
    CompanyUpdateSchema,
    ProjectCreateSchema,
    ProjectOutMinimalSchema,
    ProjectOutSchema,
    ProjectUpdateSchema,
    UserAddressCreateSchema,
    UserAddressOutSchema,
    UserAddressUpdateSchema,
    UserCreateSchema,
    UserOutMinimalSchema,
    UserOutSchema,
    UserUpdateSchema,
)
from .service import company_crud, project_crud, user_address_crud, user_crud

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post(
    "/users/",
    response_model=UserOutMinimalSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(UserPermissions.create)],
)
async def add_user(request: Request, db_session: DBSession, user: UserCreateSchema):
    try:
        db_obj = await user_crud.get_by_email_or_username(
            db_session=db_session, email=user.email, username=user.username
        )
        if db_obj is not None:
            raise UserEmailOrNameExists()
        result = await user_crud.create(
            request=request, db_session=db_session, user=user
        )
        return result
    except UserEmailOrNameExists:
        raise
    except Exception as e:
        logger.exception(f"Failed to create user: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/users/",
    response_model=List[UserOutMinimalSchema],
    dependencies=[Depends(UserPermissions.read)],
)
async def read_users(
    request: Request,
    db_session: DBSession,
    query_str: str | None = None,
    order_by: str | None = None,
):
    try:
        result = await user_crud.list(
            request=request,
            db_session=db_session,
            query_str=query_str,
            order_by=order_by,
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch users: {str(e)}")
        raise DetailedHTTPException()


@router.get("/users/{user_id}", response_model=UserOutSchema)
@allow_self_access("user_id", PermissionAction.READ, PermissionObject.USER)
async def read_user(request: Request, db_session: DBSession, user_id: UUID4):
    try:
        result = await user_crud.get(request=request, db_session=db_session, id=user_id)
        if result is None:
            raise UserNotFound()
        return result
    except UserNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch user {user_id}: {str(e)}")
        raise DetailedHTTPException()


@router.put("/users/{user_id}", response_model=UserOutMinimalSchema)
@allow_self_access("user_id", PermissionAction.UPDATE, PermissionObject.USER)
async def edit_user(
    request: Request, db_session: DBSession, user: UserUpdateSchema, user_id: UUID4
):
    try:
        db_user = await user_crud.get(
            request=request, db_session=db_session, id=user_id
        )
        if db_user is None:
            raise UserNotFound()
        if db_user.email != user.email or db_user.username != user.username:
            db_obj = await user_crud.get_by_email_or_username(
                db_session=db_session, email=user.email, username=user.username
            )
        if db_obj is not None and user.id != user_id:
            raise UserEmailOrNameExists()
        result = await user_crud.update(
            request=request, db_session=db_session, user=user, db_user=db_user
        )
        return result
    except (UserEmailOrNameExists, UserNotFound):
        raise
    except Exception as e:
        logger.exception(f"Failed to update user: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(UserPermissions.delete)],
)
async def remove_user(request: Request, db_session: DBSession, user_id: UUID4):
    try:
        db_user = await user_crud.get(
            request=request, db_session=db_session, id=user_id
        )
        if db_user is None:
            raise UserNotFound()
        await user_crud.delete(request=request, db_session=db_session, db_obj=db_user)
        return
    except UserNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete user {user_id}: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/users/{user_id}/user_addresses/", response_model=List[UserAddressOutSchema]
)
@allow_self_access("user_id", PermissionAction.READ, PermissionObject.USER_ADDRESS)
async def read_user_addresses(request: Request, db_session: DBSession, user_id: UUID4):
    try:
        result = await user_address_crud.list(
            request=request, db_session=db_session, user_id=user_id
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch user addresses of user {user_id}: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/users/{user_id}/user_addresses/{user_address_id}",
    response_model=UserAddressOutSchema,
)
@allow_self_access("user_id", PermissionAction.READ, PermissionObject.USER_ADDRESS)
async def read_user_address(
    request: Request, db_session: DBSession, user_id: UUID4, user_address_id: UUID4
):
    try:
        result = await user_address_crud.get(
            request=request, db_session=db_session, id=user_address_id, user_id=user_id
        )
        if result is None:
            raise UserAddressNotFound()
        return result
    except UserAddressNotFound:
        raise
    except Exception as e:
        logger.exception(
            f"Failed to fetch user address {user_address_id} of user {user_id}: {str(e)}"
        )
        raise DetailedHTTPException()


@router.post(
    "/users/{user_id}/user_addresses/",
    response_model=UserAddressOutSchema,
    status_code=status.HTTP_201_CREATED,
)
@allow_self_access("user_id", PermissionAction.CREATE, PermissionObject.USER_ADDRESS)
async def add_user_address(
    request: Request,
    db_session: DBSession,
    user_address: UserAddressCreateSchema,
    user_id: UUID4,
):
    try:
        result = await user_address_crud.create(
            request=request, db_session=db_session, schema=user_address, user_id=user_id
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to create user address of user {user_id}: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/users/{user_id}/user_addresses/{user_address_id}",
    response_model=UserAddressOutSchema,
)
@allow_self_access("user_id", PermissionAction.UPDATE, PermissionObject.USER_ADDRESS)
async def edit_user_address(
    request: Request,
    db_session: DBSession,
    user_address: UserAddressUpdateSchema,
    user_id: UUID4,
    user_address_id: UUID4,
):
    try:
        db_user_address = await user_address_crud.get(
            request=request, db_session=db_session, id=user_address_id, user_id=user_id
        )
        if db_user_address is None:
            raise UserAddressNotFound()
        updated_user_address = await user_address_crud.update(
            request=request,
            db_session=db_session,
            db_obj=db_user_address,
            schema=user_address,
        )
        return updated_user_address
    except UserAddressNotFound:
        raise
    except Exception as e:
        logger.exception(
            f"Failed to update user address {user_address_id} of user {user_id}: {str(e)}"
        )
        raise DetailedHTTPException()


@router.delete(
    "/users/{user_id}/user_addresses/{user_address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@allow_self_access("user_id", PermissionAction.DELETE, PermissionObject.USER_ADDRESS)
async def remove_user_address(
    request: Request, db_session: DBSession, user_id: UUID4, user_address_id: UUID4
):
    try:
        db_user_address = await user_address_crud.get(
            request=request, db_session=db_session, id=user_address_id, user_id=user_id
        )
        if db_user_address is None:
            raise UserAddressNotFound()
        await user_address_crud.delete(
            request=request, db_session=db_session, db_obj=db_user_address
        )
        return
    except Exception as e:
        logger.exception(
            f"Failed to delete user address {user_address_id} of user {user_id}: {str(e)}"
        )
        raise DetailedHTTPException()


@router.get("/users/{user_id}/orders/", response_model=List[OrderOutMinimalSchema])
@allow_self_access("user_id", PermissionAction.READ, PermissionObject.ORDER)
async def read_user_orders(request: Request, db_session: DBSession, user_id: UUID4):
    try:
        result = await order_crud.get_user_orders(
            request=request, db_session=db_session, user_id=user_id
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch user {user_id} orders: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/companies/",
    response_model=List[CompanyOutMinimalSchema],
    dependencies=[Depends(CompanyPermissions.read)],
)
async def read_companies(
    request: Request,
    db_session: DBSession,
    query_str: str | None = None,
    order_by: str | None = None,
):
    try:
        result = await company_crud.list(
            request=request,
            db_session=db_session,
            query_str=query_str,
            order_by=order_by,
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch companies: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/companies/{company_id}",
    response_model=CompanyOutSchema,
    dependencies=[Depends(CompanyPermissions.read)],
)
async def read_company(request: Request, db_session: DBSession, company_id: UUID4):
    try:
        result = await company_crud.get(
            request=request, db_session=db_session, id=company_id
        )
        if result is None:
            raise CompanyNotFound()
        return result
    except CompanyNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch company {company_id}: {str(e)}")
        raise DetailedHTTPException()


@router.post(
    "/companies/",
    response_model=CompanyOutMinimalSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(CompanyPermissions.create)],
)
async def add_company(
    request: Request, db_session: DBSession, company: CompanyCreateSchema
):
    try:
        result = await company_crud.create(
            request=request, db_session=db_session, schema=company
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to create company: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/companies/{company_id}",
    response_model=CompanyOutSchema,
    dependencies=[Depends(CompanyPermissions.update)],
)
async def edit_company(
    request: Request,
    db_session: DBSession,
    company: CompanyUpdateSchema,
    company_id: UUID4,
):
    try:
        db_company = await company_crud.get(
            request=request, db_session=db_session, id=company_id
        )
        if db_company is None:
            raise CompanyNotFound()
        result = await company_crud.update(
            request=request,
            db_session=db_session,
            schema=company,
            db_obj=db_company,
        )
        return result
    except CompanyNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to update company {company_id}: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/companies/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(CompanyPermissions.delete)],
)
async def remove_company(request: Request, db_session: DBSession, company_id: UUID4):
    try:
        db_company = await company_crud.get(
            request=request, db_session=db_session, id=company_id
        )
        if db_company is None:
            raise CompanyNotFound()
        await company_crud.delete(
            request=request, db_session=db_session, db_obj=db_company
        )
        return
    except CompanyNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete company {company_id}: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/projects/",
    response_model=List[ProjectOutMinimalSchema],
    dependencies=[Depends(ProjectPermissions.read)],
)
async def read_projects(
    request: Request,
    db_session: DBSession,
    query_str: str | None = None,
    order_by: str | None = None,
):
    try:
        result = await project_crud.list(
            request=request,
            db_session=db_session,
            query_str=query_str,
            order_by=order_by,
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch projects: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/projects/{project_id}",
    response_model=ProjectOutSchema,
    dependencies=[Depends(ProjectPermissions.read)],
)
async def read_project(request: Request, db_session: DBSession, project_id: UUID4):
    try:
        result = await project_crud.get(
            request=request, db_session=db_session, id=project_id
        )
        if result is None:
            raise ProjectNotFound()
        return result
    except ProjectNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch project {project_id}: {str(e)}")
        raise DetailedHTTPException()


@router.post(
    "/projects/",
    response_model=ProjectOutMinimalSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ProjectPermissions.create)],
)
async def add_project(
    request: Request, db_session: DBSession, project: ProjectCreateSchema
):
    try:
        result = await project_crud.create(
            request=request, db_session=db_session, schema=project
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to create project: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/projects/{project_id}",
    response_model=ProjectOutMinimalSchema,
    dependencies=[Depends(ProjectPermissions.update)],
)
async def edit_project(
    request: Request,
    db_session: DBSession,
    project: ProjectUpdateSchema,
    project_id: UUID4,
):
    try:
        db_project = await project_crud.get(
            request=request, db_session=db_session, id=project_id
        )
        if db_project is None:
            raise ProjectNotFound()
        result = await project_crud.update(
            request=request,
            db_session=db_session,
            schema=project,
            db_obj=db_project,
        )
        return result
    except ProjectNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to update project {project_id}: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(ProjectPermissions.delete)],
)
async def remove_project(request: Request, db_session: DBSession, project_id: UUID4):
    try:
        db_project = await project_crud.get(
            request=request, db_session=db_session, id=project_id
        )
        if db_project is None:
            raise ProjectNotFound()
        await project_crud.delete(
            request=request, db_session=db_session, db_obj=db_project
        )
        return
    except ProjectNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete project {project_id}: {str(e)}")
        raise DetailedHTTPException()
