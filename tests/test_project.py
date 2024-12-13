import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import date

from api.auth.security import get_password_hash
from api.database import AsyncSession
from api.user.models import User, Company, Project
from api.catalogue.models import Product


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
async def test_product(db_session: AsyncSession):
    """Create test product."""
    product = Product(
        name="Test Product",
        price=99.99,
        is_active=True,
        is_discountable=True,
        description="Test description",
        slug="test-product",
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession, test_company: Company):
    """Create test project."""
    project = Project(
        name="Test Project",
        code="TEST001",
        description="Test project description",
        priority=1,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        company_id=test_company.id,
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


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
async def test_create_project(
    client: AsyncClient,
    auth_headers: dict,
    test_company: Company,
    test_product: Product,
):
    """Test project creation."""
    response = await client.post(
        "/projects/",
        headers=auth_headers,
        json={
            "name": "New Project",
            "code": "PRJ001",
            "description": "New project description",
            "priority": 1,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "company_id": str(test_company.id),
            "products": [
                {
                    "product": {
                        "id": str(test_product.id),
                        "name": test_product.name,
                        "price": float(test_product.price),
                        "is_active": test_product.is_active,
                        "is_discountable": test_product.is_discountable,
                        "slug": test_product.slug,
                        "rating": 0,
                    },
                    "amount": 1000.00,
                    "absolute_limit": True,
                }
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Project"
    assert data["code"] == "PRJ001"


@pytest.mark.asyncio
async def test_read_projects(
    client: AsyncClient,
    auth_headers: dict,
    test_project: Project,
):
    """Test reading project list."""
    response = await client.get("/projects/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(project["name"] == "Test Project" for project in data)


@pytest.mark.asyncio
async def test_read_project(
    client: AsyncClient,
    auth_headers: dict,
    test_project: Project,
):
    """Test reading single project."""
    response = await client.get(f"/projects/{test_project.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["code"] == "TEST001"


@pytest.mark.asyncio
async def test_update_project(
    client: AsyncClient,
    auth_headers: dict,
    test_project: Project,
    test_product: Product,
):
    """Test updating project."""
    response = await client.put(
        f"/projects/{test_project.id}",
        headers=auth_headers,
        json={
            "id": str(test_project.id),
            "name": "Updated Project",
            "code": "PRJ002",
            "description": "Updated description",
            "priority": 2,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "company_id": str(test_project.company_id),
            "products": [],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project"
    assert data["code"] == "PRJ002"


@pytest.mark.asyncio
async def test_delete_project(
    client: AsyncClient,
    auth_headers: dict,
    test_project: Project,
):
    """Test deleting project."""
    response = await client.delete(f"/projects/{test_project.id}", headers=auth_headers)
    assert response.status_code == 204

    response = await client.get(f"/projects/{test_project.id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test unauthorized access to project endpoints."""
    response = await client.get("/projects/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
