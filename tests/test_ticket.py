import pytest
import pytest_asyncio
from httpx import AsyncClient

from api.auth.security import get_password_hash
from api.database import AsyncSession
from api.ticket.constant import TicketStatus
from api.ticket.models import Ticket
from api.user.models import User


@pytest_asyncio.fixture
async def test_admin_user(db_session: AsyncSession):
    """Create admin test user."""
    user = User(
        email="admin@example.com",
        username="adminuser",
        password=get_password_hash("adminpass123"),
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_admin_user: User):
    """Get authentication headers."""
    response = await client.post(
        "/login",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_ticket(db_session: AsyncSession, test_admin_user: User):
    """Create test ticket."""
    ticket = Ticket(
        subject="Test Ticket",
        description="Test ticket description",
        status=TicketStatus.INIT,
    )
    ticket.users.append(test_admin_user)
    db_session.add(ticket)
    await db_session.commit()
    await db_session.refresh(ticket)
    return ticket


@pytest.mark.asyncio
async def test_create_ticket(client: AsyncClient, auth_headers: dict):
    """Test ticket creation."""
    response = await client.post(
        "/tickets/",
        headers=auth_headers,
        json={
            "subject": "New Ticket",
            "description": "New ticket description",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["subject"] == "New Ticket"
    assert data["status"] == TicketStatus.INIT


@pytest.mark.asyncio
async def test_read_tickets(
    client: AsyncClient,
    auth_headers: dict,
    test_ticket: Ticket,
):
    """Test reading ticket list."""
    response = await client.get("/tickets/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(ticket["subject"] == "Test Ticket" for ticket in data)


@pytest.mark.asyncio
async def test_read_ticket(
    client: AsyncClient,
    auth_headers: dict,
    test_ticket: Ticket,
):
    """Test reading single ticket."""
    response = await client.get(f"/tickets/{test_ticket.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "Test Ticket"
    assert data["status"] == TicketStatus.INIT


@pytest.mark.asyncio
async def test_update_ticket(
    client: AsyncClient,
    auth_headers: dict,
    test_ticket: Ticket,
):
    """Test updating ticket."""
    response = await client.put(
        f"/tickets/{test_ticket.id}",
        headers=auth_headers,
        json={
            "id": str(test_ticket.id),
            "subject": test_ticket.subject,
            "status": TicketStatus.IN_PROGRESS,
        },
    )
    print(response.json(), "HERE")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == TicketStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_delete_ticket(
    client: AsyncClient,
    auth_headers: dict,
    test_ticket: Ticket,
):
    """Test deleting ticket."""
    response = await client.delete(f"/tickets/{test_ticket.id}", headers=auth_headers)
    assert response.status_code == 204

    response = await client.get(f"/tickets/{test_ticket.id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test unauthorized access to ticket endpoints."""
    response = await client.get("/tickets/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
