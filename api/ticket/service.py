import asyncio
from typing import Dict, List

from fastapi import Request, WebSocket
from fastapi.websockets import WebSocketDisconnect
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.core.crud import CRUDBase

from .models import Message, Ticket
from .schemas import MessageOutSchema, TicketCreateSchema, TicketUpdateSchema


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID4, List[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, ticket_id: UUID4):
        await websocket.accept()
        async with self._lock:
            if ticket_id not in self.active_connections:
                self.active_connections[ticket_id] = []
            self.active_connections[ticket_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, ticket_id: UUID4):
        async with self._lock:
            if ticket_id in self.active_connections:
                self.active_connections[ticket_id].remove(websocket)
                if not self.active_connections[ticket_id]:
                    del self.active_connections[ticket_id]

    async def broadcast_message(self, message: MessageOutSchema, ticket_id: UUID4):
        async with self._lock:
            if ticket_id in self.active_connections:
                dead_connections = []
                for connection in self.active_connections[ticket_id]:
                    try:
                        await connection.send_json(message)
                    except WebSocketDisconnect:
                        dead_connections.append(connection)

                for dead_conn in dead_connections:
                    await self.disconnect(dead_conn, ticket_id)


class CRUDTicket(CRUDBase[Ticket, TicketCreateSchema, TicketUpdateSchema]):
    async def get(
        self, db_session: AsyncSession, id: UUID4, request: Request | None = None
    ) -> Ticket | None:
        if request:
            await self._create_get_log(request=request, db_session=db_session, id=id)
        result = await db_session.execute(
            select(Ticket)
            .options(joinedload(Ticket.users), joinedload(Ticket.messages))
            .where(Ticket.id == id)
        )
        return result.unique().scalar_one_or_none()

    async def create(
        self, request: Request, db_session: AsyncSession, schema: TicketCreateSchema
    ) -> Ticket:
        await self._create_add_log(request=request, db_session=db_session)

        db_ticket = Ticket(
            subject=schema.subject,
            description=schema.description,
        )
        db_ticket.users.append(request.state.user)

        db_session.add(db_ticket)
        await db_session.commit()
        await db_session.refresh(db_ticket)
        return db_ticket

    async def update(
        self,
        request: Request,
        db_session: AsyncSession,
        db_obj: Ticket,
        schema: TicketUpdateSchema,
    ) -> Ticket:
        await self._create_update_log(request=request, db_session=db_session)

        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(db_obj, key, value)

        if request.state.user not in db_obj.users:
            db_obj.users.append(request.state.user)

        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def create_message(
        self,
        db_session: AsyncSession,
        content: str,
        ticket_id: UUID4,
        user_id: UUID4,
    ) -> Message:
        db_message = Message(content=content, ticket_id=ticket_id, user_id=user_id)

        db_session.add(db_message)
        await db_session.commit()
        await db_session.refresh(db_message)
        return db_message


ticket_crud = CRUDTicket(Ticket, "Ticket")
