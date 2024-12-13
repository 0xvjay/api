import pytest
import pytest_asyncio
from httpx import AsyncClient

from api.auth.models import Group
from api.auth.security import get_password_hash
from api.database import AsyncSession
from api.user.models import Company, User


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
async def test_company(db_session: AsyncSession):
    """Create test company."""
    company = Company(
        email="company@example.com",
        password=get_password_hash("companypass123"),
        billing_code="TEST123",
        is_active=True,
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)
    return company


@pytest_asyncio.fixture
async def test_group(db_session: AsyncSession):
    """Create test group."""
    group = Group(
        name="test_company_group", description="Test company group", is_active=True
    )
    db_session.add(group)
    await db_session.commit()
    await db_session.refresh(group)
    return group


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_admin_user: User):
    """Get authentication headers."""
    response = await client.post(
        "/login",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_company(
    client: AsyncClient, auth_headers: dict, test_group: Group
):
    """Test company creation."""
    response = await client.post(
        "/companies/",
        headers=auth_headers,
        json={
            "email": "newcompany@example.com",
            "password": "companypass123",
            "billing_code": "NEW123",
            "is_active": True,
            "groups": [
                {
                    "id": str(test_group.id),
                    "name": test_group.name,
                    "description": test_group.description,
                    "is_active": test_group.is_active,
                }
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newcompany@example.com"
    assert data["billing_code"] == "NEW123"
    assert "password" not in data


@pytest.mark.asyncio
async def test_read_companies(
    client: AsyncClient,
    auth_headers: dict,
    test_company: Company,
):
    """Test reading company list."""
    response = await client.get("/companies/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(company["email"] == "company@example.com" for company in data)


@pytest.mark.asyncio
async def test_read_company(
    client: AsyncClient,
    auth_headers: dict,
    test_company: Company,
):
    """Test reading single company."""
    response = await client.get(f"/companies/{test_company.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "company@example.com"
    assert data["billing_code"] == "TEST123"


@pytest.mark.asyncio
async def test_update_company(
    client: AsyncClient,
    auth_headers: dict,
    test_company: Company,
    test_group: Group,
):
    """Test updating company."""
    response = await client.put(
        f"/companies/{test_company.id}",
        headers=auth_headers,
        json={
            "id": str(test_company.id),
            "email": "updated@example.com",
            "billing_code": "UPD123",
            "is_active": True,
            "groups": [],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["billing_code"] == "UPD123"


@pytest.mark.asyncio
async def test_delete_company(
    client: AsyncClient,
    auth_headers: dict,
    test_company: Company,
):
    """Test deleting company."""
    response = await client.delete(
        f"/companies/{test_company.id}", headers=auth_headers
    )
    assert response.status_code == 204

    response = await client.get(f"/companies/{test_company.id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_company_login(
    client: AsyncClient,
    test_company: Company,
):
    """Test company login."""
    response = await client.post(
        "/login", json={"email": "company@example.com", "password": "companypass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test unauthorized access to company endpoints."""
    response = await client.get("/companies/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
