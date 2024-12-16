import logging
from typing import List

from fastapi import APIRouter, Depends, Request, WebSocket, status
from fastapi.websockets import WebSocketDisconnect
from pydantic import UUID4

from api.auth.permissions import TicketPermissions
from api.auth.utils import authenticate_websocket
from api.database import DBSession
from api.exceptions import DetailedHTTPException
from api.user.models import User

from .exceptions import TicketNotFound
from .schemas import (
    MessageOutSchema,
    TicketCreateSchema,
    TicketOutMinimalSchema,
    TicketOutSchema,
    TicketUpdateSchema,
)
from .service import ConnectionManager, ticket_crud

router = APIRouter(prefix="/tickets", tags=["tickets"])
ws_router = APIRouter(prefix="/tickets", tags=["tickets"])
logger = logging.getLogger(__name__)
manager = ConnectionManager()


@router.get(
    "/",
    response_model=List[TicketOutMinimalSchema],
    dependencies=[Depends(TicketPermissions.read)],
)
async def read_tickets(
    request: Request,
    db_session: DBSession,
    query_str: str | None = None,
    order_by: str | None = None,
):
    try:
        result = await ticket_crud.list(
            request=request,
            db_session=db_session,
            query_str=query_str,
            order_by=order_by,
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch tickets: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/{ticket_id}",
    response_model=TicketOutSchema,
    dependencies=[Depends(TicketPermissions.read)],
)
async def read_ticket(request: Request, db_session: DBSession, ticket_id: UUID4):
    try:
        result = await ticket_crud.get(
            request=request, db_session=db_session, id=ticket_id
        )
        if result is None:
            raise TicketNotFound()
        return result
    except TicketNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch ticket {ticket_id}: {str(e)}")
        raise DetailedHTTPException()


@router.post(
    "/",
    response_model=TicketOutMinimalSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(TicketPermissions.create)],
)
async def add_ticket(
    request: Request, db_session: DBSession, ticket: TicketCreateSchema
):
    try:
        result = await ticket_crud.create(
            request=request, db_session=db_session, schema=ticket
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to create ticket: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/{ticket_id}",
    response_model=TicketOutMinimalSchema,
    dependencies=[Depends(TicketPermissions.update)],
)
async def edit_ticket(
    request: Request,
    db_session: DBSession,
    ticket: TicketUpdateSchema,
    ticket_id: UUID4,
):
    try:
        db_ticket = await ticket_crud.get(
            request=request, db_session=db_session, id=ticket_id
        )
        if db_ticket is None:
            raise TicketNotFound()
        result = await ticket_crud.update(
            request=request, db_obj=db_ticket, db_session=db_session, schema=ticket
        )
        return result
    except TicketNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to update ticket: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(TicketPermissions.delete)],
)
async def delete_ticket(request: Request, db_session: DBSession, ticket_id: UUID4):
    try:
        db_ticket = await ticket_crud.get(
            request=request, db_session=db_session, id=ticket_id
        )
        if db_ticket is None:
            raise TicketNotFound()
        await ticket_crud.delete(
            request=request, db_session=db_session, db_obj=db_ticket
        )
    except TicketNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete ticket: {str(e)}")
        raise DetailedHTTPException()


@ws_router.websocket("/{ticket_id}/messages")
async def add_message(
    websocket: WebSocket,
    db_session: DBSession,
    ticket_id: UUID4,
    user: User = Depends(authenticate_websocket),
):
    try:
        await manager.connect(websocket, ticket_id)

        db_ticket = await ticket_crud.get(db_session=db_session, id=ticket_id)
        if db_ticket is None:
            raise TicketNotFound()

        async for data in websocket.iter_json():
            db_message = await ticket_crud.create_message(
                db_session=db_session,
                content=data,
                user_id=user.id,
                ticket_id=ticket_id,
            )

            message = MessageOutSchema.model_validate(db_message)
            await manager.broadcast_message(message.model_dump(mode="json"), ticket_id)
    except TicketNotFound:
        raise
    except WebSocketDisconnect:
        await manager.disconnect(websocket=websocket, ticket_id=ticket_id)
    except Exception as e:
        logger.exception(f"Failed to add message {ticket_id}: {str(e)}")
