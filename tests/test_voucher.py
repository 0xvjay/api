import pytest
import pytest_asyncio
from datetime import datetime
from httpx import AsyncClient

from api.auth.security import get_password_hash
from api.database import AsyncSession
from api.user.models import User
from api.voucher.constant import USAGE_CHOICES
from api.voucher.models import Voucher, VoucherApplication


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
async def test_voucher(db_session: AsyncSession):
    """Create a test voucher."""
    voucher = Voucher(
        name="Test Voucher",
        code="TESTVOUCHER",
        usage=USAGE_CHOICES.ONCE_PER_CUSTOMER,
        start_datetime=datetime(2024, 1, 1),
        end_datetime=datetime(2024, 12, 31),
    )
    db_session.add(voucher)
    await db_session.commit()
    await db_session.refresh(voucher)
    return voucher


@pytest_asyncio.fixture
async def test_voucher_application(
    db_session: AsyncSession, test_admin_user: User, test_voucher: Voucher
):
    """Create a test voucher application."""
    voucher_application = VoucherApplication(
        order_id="",
        user_id=test_admin_user.id,
        voucher_id=test_voucher.id,
    )
    db_session.add(voucher_application)
    await db_session.commit()
    await db_session.refresh(voucher_application)
    return voucher_application


@pytest.mark.asyncio
async def test_create_voucher(client: AsyncClient, auth_headers: dict):
    """Test voucher creation."""
    response = await client.post(
        "/vouchers/",
        headers=auth_headers,
        json={
            "name": "New Voucher",
            "code": "NEWVOUCHER",
            "usage": USAGE_CHOICES.MULTI_USE,
            "start_datetime": "2024-01-01",
            "end_datetime": "2024-12-31",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Voucher"
    assert data["code"] == "NEWVOUCHER"


@pytest.mark.asyncio
async def test_read_vouchers(
    client: AsyncClient, auth_headers: dict, test_voucher: Voucher
):
    """Test reading voucher list."""
    response = await client.get("/vouchers/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(voucher["name"] == "Test Voucher" for voucher in data)


@pytest.mark.asyncio
async def test_read_voucher(
    client: AsyncClient, auth_headers: dict, test_voucher: Voucher
):
    """Test reading single voucher."""
    response = await client.get(f"/vouchers/{test_voucher.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Voucher"
    assert data["code"] == "TESTVOUCHER"


@pytest.mark.asyncio
async def test_update_voucher(
    client: AsyncClient, auth_headers: dict, test_voucher: Voucher
):
    """Test updating voucher."""
    response = await client.put(
        f"/vouchers/{test_voucher.id}",
        headers=auth_headers,
        json={
            "id": str(test_voucher.id),
            "name": "Updated Voucher",
            "code": "UPDATEDVOUCHER",
            "usage": USAGE_CHOICES.SINGLE_USE,
            "start_datetime": "2024-01-01",
            "end_datetime": "2024-12-31",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Voucher"
    assert data["code"] == "UPDATEDVOUCHER"


@pytest.mark.asyncio
async def test_delete_voucher(
    client: AsyncClient, auth_headers: dict, test_voucher: Voucher
):
    """Test deleting voucher."""
    response = await client.delete(f"/vouchers/{test_voucher.id}", headers=auth_headers)
    assert response.status_code == 204

    response = await client.get(f"/vouchers/{test_voucher.id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test unauthorized access to voucher endpoints."""
    response = await client.get("/vouchers/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_duplicate_voucher_name(
    client: AsyncClient, auth_headers: dict, test_voucher: Voucher
):
    """Test creating voucher with duplicate name."""
    response = await client.post(
        "/vouchers/",
        headers=auth_headers,
        json={
            "name": "Test Voucher",
            "code": "UNIQUEVOUCHER",
            "usage": USAGE_CHOICES.MULTI_USE,
            "start_datetime": "2024-01-01",
            "end_datetime": "2024-12-31",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Voucher name or code exists"


@pytest.mark.asyncio
async def test_duplicate_voucher_code(
    client: AsyncClient, auth_headers: dict, test_voucher: Voucher
):
    """Test creating voucher with duplicate code."""
    response = await client.post(
        "/vouchers/",
        headers=auth_headers,
        json={
            "name": "Unique Voucher",
            "code": "TESTVOUCHER",
            "usage": USAGE_CHOICES.MULTI_USE,
            "start_datetime": "2024-01-01",
            "end_datetime": "2024-12-31",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Voucher name or code exists"
