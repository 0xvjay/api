from uuid import UUID

import pytest
import pytest_asyncio
from httpx import AsyncClient

from api.auth.security import get_password_hash
from api.catalogue.models import Category, SubCategory
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
    """Create normal test user."""
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


@pytest_asyncio.fixture
async def test_subcategory(db_session: AsyncSession, test_category: Category):
    """Create test subcategory."""
    subcategory = SubCategory(
        name="Test SubCategory", is_active=True, category_id=test_category.id
    )
    db_session.add(subcategory)
    await db_session.commit()
    await db_session.refresh(subcategory)
    return subcategory


@pytest.mark.asyncio
async def test_create_subcategory(
    client: AsyncClient,
    auth_admin_headers: dict,
    test_category: Category,
    db_session: AsyncSession,
):
    """Test subcategory creation."""
    response = await client.post(
        "/sub_categories/",
        headers=auth_admin_headers,
        json={
            "name": "New SubCategory",
            "is_active": True,
            "category_id": str(test_category.id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New SubCategory"
    assert data["is_active"] is True
    assert "slug" in data

    result = await db_session.get(SubCategory, UUID(data["id"]))
    assert result is not None
    assert result.name == "New SubCategory"


@pytest.mark.asyncio
async def test_create_duplicate_subcategory(
    client: AsyncClient, auth_admin_headers: dict, test_subcategory: SubCategory
):
    """Test creating subcategory with duplicate name."""
    response = await client.post(
        "/sub_categories/",
        headers=auth_admin_headers,
        json={
            "name": "Test SubCategory",
            "is_active": True,
            "category_id": str(test_subcategory.category_id),
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "SubCategory name already exists"


@pytest.mark.asyncio
async def test_get_subcategories(
    client: AsyncClient, auth_admin_headers: dict, test_subcategory: SubCategory
):
    """Test getting list of subcategories."""
    response = await client.get("/sub_categories/", headers=auth_admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(subcat["name"] == "Test SubCategory" for subcat in data)


@pytest.mark.asyncio
async def test_get_single_subcategory(
    client: AsyncClient, auth_admin_headers: dict, test_subcategory: SubCategory
):
    """Test getting a single subcategory."""
    response = await client.get(
        f"/sub_categories/{test_subcategory.id}", headers=auth_admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test SubCategory"
    assert "products" in data


@pytest.mark.asyncio
async def test_update_subcategory(
    client: AsyncClient, auth_admin_headers: dict, test_subcategory: SubCategory
):
    """Test updating a subcategory."""
    response = await client.put(
        f"/sub_categories/{test_subcategory.id}",
        headers=auth_admin_headers,
        json={
            "id": str(test_subcategory.id),
            "name": "Updated SubCategory",
            "is_active": True,
            "category_id": str(test_subcategory.category_id),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated SubCategory"
    assert "slug" in data


@pytest.mark.asyncio
async def test_delete_subcategory(
    client: AsyncClient, auth_admin_headers: dict, test_subcategory: SubCategory
):
    """Test deleting a subcategory."""
    response = await client.delete(
        f"/sub_categories/{test_subcategory.id}", headers=auth_admin_headers
    )
    assert response.status_code == 204

    response = await client.get(
        f"/sub_categories/{test_subcategory.id}", headers=auth_admin_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(
    client: AsyncClient, auth_user_headers: dict, test_category: Category
):
    """Test unauthorized access to subcategory endpoints."""
    response = await client.post(
        "/sub_categories/",
        headers=auth_user_headers,
        json={
            "name": "Unauthorized SubCategory",
            "is_active": True,
            "category_id": str(test_category.id),
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_access(client: AsyncClient):
    """Test unauthenticated access to subcategory endpoints."""
    response = await client.get("/sub_categories/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
