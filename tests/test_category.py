import pytest
import pytest_asyncio
from httpx import AsyncClient

from api.auth.security import get_password_hash
from api.catalogue.models import Category
from api.database import AsyncSession
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
async def test_normal_user(db_session: AsyncSession):
    """Create normal test user without admin privileges."""
    user = User(
        email="user@example.com",
        username="normaluser",
        password=get_password_hash("userpass123"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_admin_headers(client: AsyncClient, test_admin_user: User):
    """Get authentication headers for admin user."""
    response = await client.post(
        "/login",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_user_headers(client: AsyncClient, test_normal_user: User):
    """Get authentication headers for normal user."""
    response = await client.post(
        "/login",
        json={"email": "user@example.com", "password": "userpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_category(db_session: AsyncSession):
    """Create test category."""
    category = Category(
        name="Test Category",
        is_active=True,
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.mark.asyncio
async def test_create_category(client: AsyncClient, auth_admin_headers: dict):
    """Test category creation."""
    response = await client.post(
        "/categories/",
        headers=auth_admin_headers,
        json={"name": "New Category", "is_active": True, "sub_categories": []},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Category"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_duplicate_category(
    client: AsyncClient, auth_admin_headers: dict, test_category: Category
):
    """Test creating category with duplicate name."""
    response = await client.post(
        "/categories/",
        headers=auth_admin_headers,
        json={"name": "Test Category", "is_active": True, "sub_categories": []},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Category name already exists"


@pytest.mark.asyncio
async def test_get_categories(
    client: AsyncClient, auth_admin_headers: dict, test_category: Category
):
    """Test getting list of categories."""
    response = await client.get("/categories/", headers=auth_admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(category["name"] == "Test Category" for category in data)


@pytest.mark.asyncio
async def test_get_single_category(
    client: AsyncClient, auth_admin_headers: dict, test_category: Category
):
    """Test getting a single category."""
    response = await client.get(
        f"/categories/{test_category.id}", headers=auth_admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Category"


@pytest.mark.asyncio
async def test_update_category(
    client: AsyncClient, auth_admin_headers: dict, test_category: Category
):
    """Test updating a category."""
    response = await client.put(
        f"/categories/{test_category.id}",
        headers=auth_admin_headers,
        json={
            "id": str(test_category.id),
            "name": "Updated Category",
            "is_active": True,
            "sub_categories": [],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"


@pytest.mark.asyncio
async def test_delete_category(
    client: AsyncClient, auth_admin_headers: dict, test_category: Category
):
    """Test deleting a category."""
    response = await client.delete(
        f"/categories/{test_category.id}", headers=auth_admin_headers
    )
    assert response.status_code == 204

    response = await client.get(
        f"/categories/{test_category.id}", headers=auth_admin_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient, auth_user_headers: dict):
    """Test unauthorized access to category endpoints."""
    response = await client.post(
        "/categories/",
        headers=auth_user_headers,
        json={"name": "Unauthorized Category", "is_active": True, "sub_categories": []},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_access(client: AsyncClient):
    """Test unauthenticated access to category endpoints."""
    response = await client.get("/categories/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
