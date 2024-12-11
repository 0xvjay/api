import pytest
import pytest_asyncio
from httpx import AsyncClient

from api.auth.security import get_password_hash
from api.catalogue.models import Category, Product, SubCategory
from api.database import AsyncSession
from api.user.models import User


@pytest_asyncio.fixture
async def test_category(db_session: AsyncSession):
    """Create test category."""
    category = Category(name="Test Category", is_active=True)
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest_asyncio.fixture
async def test_sub_category(db_session: AsyncSession, test_category: Category):
    """Create test sub-category."""
    sub_category = SubCategory(
        name="Test SubCategory",
        category_id=test_category.id,
        is_active=True,
    )
    db_session.add(sub_category)
    await db_session.commit()
    await db_session.refresh(sub_category)
    return sub_category


@pytest_asyncio.fixture
async def test_product(db_session: AsyncSession, test_sub_category: SubCategory):
    """Create test product."""
    product = Product(
        name="Test Product",
        description="Test product description",
        price=99.99,
        is_active=True,
    )
    product.sub_categories.append(test_sub_category)
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
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
async def regular_user(db_session: AsyncSession):
    """Create regular test user."""
    user = User(
        email="user@example.com",
        username="regularuser",
        password=get_password_hash("userpass123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, admin_user: User):
    """Get admin authentication headers."""
    response = await client.post(
        "/login",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def user_headers(client: AsyncClient, regular_user: User):
    """Get regular user authentication headers."""
    response = await client.post(
        "/login",
        json={"email": "user@example.com", "password": "userpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_product(
    client: AsyncClient, admin_headers: dict, test_sub_category: SubCategory
):
    """Test product creation."""
    response = await client.post(
        "/products/",
        headers=admin_headers,
        json={
            "name": "Test Product",
            "price": "99.99",
            "is_active": True,
            "is_discountable": True,
            "description": "Test description",
            "short_description": "Short desc",
            "sub_categories": [
                {
                    "id": str(test_sub_category.id),
                    "name": test_sub_category.name,
                    "is_active": test_sub_category.is_active,
                    "slug": test_sub_category.slug,
                }
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"


@pytest.mark.asyncio
async def test_create_product_unauthorized(
    client: AsyncClient, user_headers: dict, test_sub_category: SubCategory
):
    """Test product creation without proper permissions."""
    response = await client.post(
        "/products/",
        headers=user_headers,
        json={
            "name": "New Product",
            "description": "New product description",
            "price": 199.99,
            "is_active": True,
            "sub_categories": [
                {
                    "id": str(test_sub_category.id),
                    "name": test_sub_category.name,
                    "is_active": test_sub_category.is_active,
                    "slug": test_sub_category.slug,
                }
            ],
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_product_duplicate_name(
    client: AsyncClient,
    admin_headers: dict,
    test_product: Product,
    test_sub_category: SubCategory,
):
    """Test product creation with duplicate name."""
    response = await client.post(
        "/products/",
        headers=admin_headers,
        json={
            "name": test_product.name,
            "description": "Different description",
            "price": 299.99,
            "is_active": True,
            "is_discountable": True,
            "sub_categories": [
                {
                    "id": str(test_sub_category.id),
                    "name": test_sub_category.name,
                    "is_active": test_sub_category.is_active,
                    "slug": test_sub_category.slug,
                }
            ],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Product name already exists"


@pytest.mark.asyncio
async def test_read_products(
    client: AsyncClient, admin_headers: dict, test_product: Product
):
    """Test reading product list."""
    response = await client.get("/products/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(product["name"] == test_product.name for product in data)


@pytest.mark.asyncio
async def test_read_product(
    client: AsyncClient, admin_headers: dict, test_product: Product
):
    """Test reading single product."""
    response = await client.get(f"/products/{test_product.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_product.name
    assert data["description"] == test_product.description


@pytest.mark.asyncio
async def test_update_product(
    client: AsyncClient,
    admin_headers: dict,
    test_product: Product,
    test_sub_category: SubCategory,
):
    """Test updating product."""
    response = await client.put(
        f"/products/{test_product.id}",
        headers=admin_headers,
        json={
            "id": str(test_product.id),
            "name": "Updated Product",
            "description": "Updated description",
            "price": 299.99,
            "is_active": True,
            "is_discountable": False,
            "sub_categories": [
                {
                    "id": str(test_sub_category.id),
                    "name": test_sub_category.name,
                    "is_active": test_sub_category.is_active,
                    "slug": test_sub_category.slug,
                }
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product"
    assert data["is_discountable"] is False


@pytest.mark.asyncio
async def test_update_product_unauthorized(
    client: AsyncClient, user_headers: dict, test_product: Product
):
    """Test updating product without proper permissions."""
    response = await client.put(
        f"/products/{test_product.id}",
        headers=user_headers,
        json={
            "id": str(test_product.id),
            "name": "Hacked Product",
            "description": "Hacked description",
            "price": 0.99,
            "is_active": True,
            "sub_categories": [],
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_product(
    client: AsyncClient, admin_headers: dict, test_product: Product
):
    """Test deleting product."""
    response = await client.delete(
        f"/products/{test_product.id}", headers=admin_headers
    )
    assert response.status_code == 204

    response = await client.get(f"/products/{test_product.id}", headers=admin_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_unauthorized(
    client: AsyncClient, user_headers: dict, test_product: Product
):
    """Test deleting product without proper permissions."""
    response = await client.delete(f"/products/{test_product.id}", headers=user_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test unauthorized access to product endpoints."""
    response = await client.get("/products/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
