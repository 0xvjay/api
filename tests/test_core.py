import pytest
import pytest_asyncio
from httpx import AsyncClient

from api.auth.security import get_password_hash
from api.core.models import SiteSetting
from api.database import AsyncSession
from api.user.models import User


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
async def auth_headers(client: AsyncClient, test_admin_user: User):
    """Get authentication headers."""
    response = await client.post(
        "/login",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_site_settings(db_session: AsyncSession):
    """Create test site settings."""
    settings = SiteSetting(
        platform_is_active=True,
        platform_message="Test Platform Message",
        admin_panel_is_active=True,
        admin_panel_message="Test Admin Message",
    )
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(settings)
    return settings


# Admin Log Tests
@pytest.mark.asyncio
async def test_read_admin_logs(
    client: AsyncClient, auth_headers: dict, db_session: AsyncSession
):
    """Test reading admin logs."""
    async with db_session:
        response = await client.get("/logs/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_read_admin_logs_unauthorized(client: AsyncClient):
    """Test unauthorized access to admin logs."""
    response = await client.get("/logs/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# Site Settings Tests
@pytest.mark.asyncio
async def test_read_site_settings(
    client: AsyncClient, auth_headers: dict, test_site_settings: SiteSetting
):
    """Test reading site settings."""
    response = await client.get("/site_settings/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["platform_is_active"] is True
    assert data["platform_message"] == "Test Platform Message"
    assert data["admin_panel_is_active"] is True
    assert data["admin_panel_message"] == "Test Admin Message"


@pytest.mark.asyncio
async def test_update_site_settings(
    client: AsyncClient, auth_headers: dict, test_site_settings: SiteSetting
):
    """Test updating site settings."""
    response = await client.get("/site_settings/", headers=auth_headers)
    current_settings = response.json()

    update_response = await client.put(
        "/site_settings/",
        headers=auth_headers,
        json={
            "id": current_settings["id"],
            "platform_is_active": False,
            "platform_message": "Platform is under maintenance",
            "admin_panel_is_active": True,
            "admin_panel_message": "Admin panel is active",
        },
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["platform_is_active"] is False
    assert updated_data["platform_message"] == "Platform is under maintenance"


@pytest.mark.asyncio
async def test_site_settings_unauthorized(client: AsyncClient):
    """Test unauthorized access to site settings."""
    response = await client.get("/site_settings/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# CORS Tests
@pytest.mark.asyncio
async def test_cors_security(client: AsyncClient):
    """Test CORS security configurations"""
    headers = {
        "Origin": "http://malicious-site.com",
        "Access-Control-Request-Method": "POST",
    }
    response = await client.options("/orders/", headers=headers)
    assert response.status_code == 400
