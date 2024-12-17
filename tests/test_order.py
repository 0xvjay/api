from datetime import date
from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select  # noqa: F401

from api.auth.security import get_password_hash
from api.catalogue.models import Product
from api.database import AsyncSession
from api.order.constant import OrderStatus
from api.order.models import Order
from api.user.models import (  # noqa: F401
    Credit,
    ProductLimit,
    Project,
    Transaction,
    User,
)


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        password=get_password_hash("testpass123"),
        first_name="Test",
        last_name="User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin_user(db_session: AsyncSession):
    """Create admin test user."""
    user = User(
        email="admin@example.com",
        username="adminuser",
        password=get_password_hash("adminpass123"),
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


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
async def auth_headers(client: AsyncClient, test_admin_user: User):
    """Get authentication headers for admin user."""
    response = await client.post(
        "/login",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def user_auth_headers(client: AsyncClient, test_user: User):
    """Get authentication headers for regular user."""
    response = await client.post(
        "/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_order(db_session: AsyncSession, test_user: User, test_product: Product):
    """Create test order."""
    order = Order(
        user_id=test_user.id,
        total_incl_tax=99.99,
        total_excl_tax=90.99,
        status=OrderStatus.INIT,
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    return order


@pytest_asyncio.fixture
async def test_project_with_credit(db_session: AsyncSession, test_user: User):
    """Create test project with credit."""
    project = Project(
        name="Test Project",
        code="TEST001",
        description="Test project description",
        priority=1,
        start_date=date(2024, 12, 12),
        end_date=date(2024, 12, 31),
    )
    db_session.add(project)
    await db_session.flush()

    credit = Credit(
        user_id=test_user.id, project_id=project.id, amount=Decimal("1000.00")
    )
    db_session.add(credit)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def test_project_with_product_limit(
    db_session: AsyncSession, test_project_with_credit: Project, test_product: Product
):
    """Create product limit for test project."""
    product_limit = ProductLimit(
        project_id=test_project_with_credit.id,
        product_id=test_product.id,
        amount=Decimal("500.00"),
        absolute_limit=True,
    )
    db_session.add(product_limit)
    await db_session.commit()
    return product_limit


# @pytest.mark.asyncio
# async def test_create_order_with_sufficient_credit(
#     client: AsyncClient,
#     auth_headers: dict,
#     test_product: Product,
#     test_project_with_credit: Project,
# ):
#     """Test order creation with sufficient credit."""
#     payload = {
#         "guest_email": "guest@example.com",
#         "lines": [
#             {
#                 "quantity": 2,
#                 "product": {
#                     "id": str(test_product.id),
#                     "name": test_product.name,
#                     "price": float(test_product.price),
#                     "is_active": test_product.is_active,
#                     "is_discountable": test_product.is_discountable,
#                     "slug": test_product.slug,
#                     "rating": 0,
#                 },
#             }
#         ],
#     }

#     response = await client.post("/orders/", headers=auth_headers, json=payload)
#     assert response.status_code == 200
#     data = response.json()

#     assert data["guest_email"] == "guest@example.com"
#     assert Decimal(data["total_incl_tax"]) == test_product.price * 2

#     async with AsyncSession() as session:
#         result = await session.execute(
#             select(Transaction).where(Transaction.order_id == data["id"])
#         )
#         transaction = result.scalar_one()
#         assert transaction is not None
#         assert transaction.amount == test_product.price * 2


# @pytest.mark.asyncio
# async def test_create_order_with_product_limit(
#     client: AsyncClient,
#     auth_headers: dict,
#     test_product: Product,
#     test_project_with_product_limit: ProductLimit,
# ):
#     """Test order creation with product-specific limit."""
#     payload = {
#         "lines": [
#             {
#                 "quantity": 4,
#                 "product": {
#                     "id": str(test_product.id),
#                     "name": test_product.name,
#                     "price": float(test_product.price),
#                     "is_active": test_product.is_active,
#                     "is_discountable": test_product.is_discountable,
#                     "slug": test_product.slug,
#                     "rating": 0,
#                 },
#             }
#         ],
#     }

#     response = await client.post("/orders/", headers=auth_headers, json=payload)
#     assert response.status_code == 200
#     data = response.json()

#     assert Decimal(data["total_incl_tax"]) == test_product.price * 4

#     async with AsyncSession() as session:
#         result = await session.execute(
#             select(Transaction)
#             .where(Transaction.order_id == data["id"])
#             .order_by(Transaction.amount.desc())
#         )
#         transactions = result.scalars().all()
#         assert len(transactions) > 0
#         total_amount = sum(t.amount for t in transactions)
#         assert total_amount == test_product.price * 4


@pytest.mark.asyncio
async def test_create_order_insufficient_credit(
    client: AsyncClient,
    auth_headers: dict,
    test_product: Product,
    test_project_with_credit: Project,
):
    """Test order creation with insufficient credit."""
    test_product.price = Decimal("2000.00")

    payload = {
        "lines": [
            {
                "quantity": 1,
                "product": {
                    "id": str(test_product.id),
                    "name": test_product.name,
                    "price": float(test_product.price),
                    "is_active": test_product.is_active,
                    "is_discountable": test_product.is_discountable,
                    "slug": test_product.slug,
                    "rating": 0,
                },
            }
        ],
    }

    response = await client.post("/orders/", headers=auth_headers, json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient credit available for purchase"


@pytest.mark.asyncio
async def test_read_orders(
    client: AsyncClient,
    auth_headers: dict,
    test_order: Order,
):
    """Test reading order list."""
    response = await client.get("/orders/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_read_order(
    client: AsyncClient,
    auth_headers: dict,
    test_order: Order,
):
    """Test reading single order."""
    response = await client.get(f"/orders/{test_order.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert str(test_order.id) == data["id"]


@pytest.mark.asyncio
async def test_update_order(
    client: AsyncClient,
    auth_headers: dict,
    test_order: Order,
):
    """Test updating order status."""
    payload = {
        "id": str(test_order.id),
        "status": OrderStatus.CONFIRMED,
        "guest_email": None,
    }

    response = await client.put(
        f"/orders/{test_order.id}", headers=auth_headers, json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == OrderStatus.CONFIRMED


@pytest.mark.asyncio
async def test_unauthorized_access(
    client: AsyncClient,
    test_order: Order,
):
    """Test unauthorized access to orders."""
    response = await client.get("/orders/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_regular_user_permission(
    client: AsyncClient,
    user_auth_headers: dict,
    test_order: Order,
):
    """Test regular user permissions on orders."""
    response = await client.get("/orders/", headers=user_auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"


@pytest.mark.asyncio
async def test_invalid_order_id(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test accessing non-existent order."""
    import uuid

    fake_id = str(uuid.uuid4())
    response = await client.get(f"/orders/{fake_id}", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_invalid_order_status_update(
    client: AsyncClient,
    auth_headers: dict,
    test_order: Order,
):
    """Test updating order with invalid status."""
    payload = {
        "id": str(test_order.id),
        "status": "INVALID_STATUS",
        "guest_email": None,
    }

    response = await client.put(
        f"/orders/{test_order.id}", headers=auth_headers, json=payload
    )
    assert response.status_code == 422
