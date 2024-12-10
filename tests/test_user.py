import pytest
import pytest_asyncio
from httpx import AsyncClient

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
async def auth_headers(client: AsyncClient, test_admin_user: User):
    """Get authentication headers."""
    response = await client.post(
        "/login",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def other_user(db_session: AsyncSession):
    """Create another test user."""
    user = User(
        email="other@example.com",
        username="otheruser",
        password=get_password_hash("testpass123"),
        first_name="Other",
        last_name="User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def other_user_headers(client: AsyncClient, other_user: User):
    """Get authentication headers for other user."""
    response = await client.post(
        "/login",
        json={"email": "other@example.com", "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_user_address(client: AsyncClient, auth_headers: dict, test_user: User):
    """Create a test user address."""
    response = await client.post(
        f"/users/{test_user.id}/user_addresses/",
        headers=auth_headers,
        json={
            "first_name": "Test",
            "last_name": "User",
            "line1": "123 Test St",
            "line2": "Apt 4",
            "state": "Test State",
            "postcode": "12345",
            "country": "Test Country",
            "phone_number": "1234567890",
            "is_default_for_shipping": True,
            "is_default_for_billing": True,
        },
    )
    return response.json()


# User Tests
@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, auth_headers: dict):
    """Test user creation."""
    response = await client.post(
        "/users/",
        headers=auth_headers,
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "is_active": True,
            "groups": [],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "password" not in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(
    client: AsyncClient, auth_headers: dict, test_user: User
):
    """Test user creation with duplicate email."""
    response = await client.post(
        "/users/",
        headers=auth_headers,
        json={
            "email": "test@example.com",
            "username": "different",
            "password": "testpass123",
            "is_active": True,
            "groups": [],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User with email or username already exists"


@pytest.mark.asyncio
async def test_read_users(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test reading user list."""
    response = await client.get("/users/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(user["email"] == "test@example.com" for user in data)


@pytest.mark.asyncio
async def test_read_user(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test reading single user."""
    response = await client.get(f"/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test updating user."""
    response = await client.put(
        f"/users/{test_user.id}",
        headers=auth_headers,
        json={
            "id": str(test_user.id),
            "email": "updated@example.com",
            "username": "updated_user",
            "password": "newpass123",
            "first_name": "Updated",
            "last_name": "User",
            "is_active": True,
            "groups": [],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["username"] == "updated_user"


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test deleting user."""
    response = await client.delete(f"/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 204

    response = await client.get(f"/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 404


# User Address Tests
@pytest.mark.asyncio
async def test_create_user_address(
    client: AsyncClient, auth_headers: dict, test_user: User
):
    """Test creating user address."""
    response = await client.post(
        f"/users/{test_user.id}/user_addresses/",
        headers=auth_headers,
        json={
            "first_name": "Test",
            "last_name": "User",
            "line1": "123 Test St",
            "line2": "Apt 4",
            "state": "Test State",
            "postcode": "12345",
            "country": "Test Country",
            "phone_number": "1234567890",
            "is_default_for_shipping": True,
            "is_default_for_billing": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["line1"] == "123 Test St"


@pytest.mark.asyncio
async def test_create_user_address_validation(
    client: AsyncClient, auth_headers: dict, test_user: User
):
    """Test user address creation with invalid data."""
    response = await client.post(
        f"/users/{test_user.id}/user_addresses/",
        headers=auth_headers,
        json={
            "first_name": "Test",
            "last_name": "User",
            # Missing required field 'country'
            "line1": "123 Test St",
            "phone_number": "1234567890",
            "is_default_for_shipping": True,
            "is_default_for_billing": True,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_address(
    client: AsyncClient, auth_headers: dict, test_user: User, test_user_address: dict
):
    """Test updating user address."""
    response = await client.put(
        f"/users/{test_user.id}/user_addresses/{test_user_address['id']}",
        headers=auth_headers,
        json={
            "id": test_user_address["id"],
            "first_name": "Updated",
            "last_name": "Name",
            "line1": "456 Updated St",
            "line2": "Suite 8",
            "state": "Updated State",
            "postcode": "54321",
            "country": "Updated Country",
            "phone_number": "9876543210",
            "is_default_for_shipping": False,
            "is_default_for_billing": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["line1"] == "456 Updated St"
    assert data["first_name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_user_address(
    client: AsyncClient, auth_headers: dict, test_user: User, test_user_address: dict
):
    """Test deleting user address."""
    response = await client.delete(
        f"/users/{test_user.id}/user_addresses/{test_user_address['id']}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    response = await client.get(
        f"/users/{test_user.id}/user_addresses/{test_user_address['id']}",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_other_user_cannot_access_address(
    client: AsyncClient,
    other_user_headers: dict,
    test_user: User,
    test_user_address: dict,
):
    """Test that other users cannot access another user's address."""
    # read address
    response = await client.get(
        f"/users/{test_user.id}/user_addresses/{test_user_address['id']}",
        headers=other_user_headers,
    )
    assert response.status_code == 403

    # update address
    response = await client.put(
        f"/users/{test_user.id}/user_addresses/{test_user_address['id']}",
        headers=other_user_headers,
        json={
            "id": test_user_address["id"],
            "first_name": "Hacker",
            "last_name": "Attack",
            "line1": "Hack St",
            "country": "Hackland",
            "phone_number": "1234567890",
            "is_default_for_shipping": True,
            "is_default_for_billing": True,
        },
    )
    assert response.status_code == 403

    # delete address
    response = await client.delete(
        f"/users/{test_user.id}/user_addresses/{test_user_address['id']}",
        headers=other_user_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_user_addresses_permission(
    client: AsyncClient, other_user_headers: dict, test_user: User
):
    """Test that other users cannot list another user's addresses."""
    response = await client.get(
        f"/users/{test_user.id}/user_addresses/",
        headers=other_user_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_read_user_addresses(
    client: AsyncClient, auth_headers: dict, test_user: User
):
    """Test reading user addresses."""
    response = await client.get(
        f"/users/{test_user.id}/user_addresses/", headers=auth_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_read_user_orders(
    client: AsyncClient, auth_headers: dict, test_user: User
):
    """Test reading user orders."""
    response = await client.get(f"/users/{test_user.id}/orders/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test unauthorized access to user endpoints."""
    response = await client.get("/users/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
