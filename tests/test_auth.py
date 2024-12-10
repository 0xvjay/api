import pytest
import pytest_asyncio
from httpx import AsyncClient

from api.auth.models import Group
from api.auth.security import get_password_hash
from api.database import AsyncSession
from api.user.models import User


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        password=get_password_hash("testpass123"),
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_inactive_user(db_session: AsyncSession):
    """Create inactive test user."""
    user = User(
        email="inactive@example.com",
        username="inactive",
        password=get_password_hash("testpass123"),
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_group(db_session: AsyncSession):
    """Create test group."""
    group = Group(name="test_group", description="Test group", is_active=True)
    db_session.add(group)
    await db_session.commit()
    await db_session.refresh(group)
    return group


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    """Test successful login."""
    response = await client.post(
        "/login", json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user: User):
    """Test login with invalid credentials."""
    response = await client.post(
        "/login", json={"email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User Not Found"


@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    """Test accessing protected route without token."""
    response = await client.get("/users/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_protected_route_with_token(client: AsyncClient, test_user: User):
    """Test accessing protected route with valid token."""
    login_response = await client.post(
        "/login", json={"email": "test@example.com", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]

    response = await client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_group_crud_operations(client: AsyncClient, test_user: User):
    """Test group CRUD operations."""
    login_response = await client.post(
        "/login", json={"email": "test@example.com", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/groups/",
        headers=headers,
        json={
            "name": "new_group",
            "description": "New test group",
            "is_active": True,
            "permissions": [],
        },
    )
    assert create_response.status_code == 201
    group_id = create_response.json()["id"]

    read_response = await client.get(f"/groups/{group_id}", headers=headers)
    assert read_response.status_code == 200
    assert read_response.json()["name"] == "new_group"

    update_response = await client.put(
        f"/groups/{group_id}",
        headers=headers,
        json={
            "id": group_id,
            "name": "updated_group",
            "description": "Updated test group",
            "is_active": True,
            "permissions": [],
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "updated_group"

    delete_response = await client.delete(f"/groups/{group_id}", headers=headers)
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_permission_list(client: AsyncClient, test_user: User):
    """Test listing permissions."""
    login_response = await client.post(
        "/login", json={"email": "test@example.com", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/permissions/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
