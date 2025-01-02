import pytest
import pytest_asyncio
from httpx import AsyncClient

from api.auth.security import get_password_hash
from api.catalogue.models import Product
from api.database import AsyncSession
from api.review.constant import VoteEnum
from api.review.models import ProductReview, Vote
from api.user.models import User  # noqa: F401


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
async def test_review(db_session: AsyncSession, test_user: User, test_product: Product):
    """Create test review."""
    review = ProductReview(
        user_id=test_user.id,
        product_id=test_product.id,
        rating=4,
        title="Test Review",
        body="This is a test review.",
    )
    db_session.add(review)
    await db_session.commit()
    await db_session.refresh(review)
    return review


@pytest_asyncio.fixture
async def test_vote(
    db_session: AsyncSession, test_user: User, test_review: ProductReview
):
    """Create test vote."""
    vote = Vote(vote=VoteEnum.upvote, review_id=test_review.id, user_id=test_user.id)
    db_session.add(vote)
    await db_session.commit()
    await db_session.refresh(vote)
    return vote


@pytest.mark.asyncio
async def test_create_review(
    client: AsyncClient,
    auth_headers: dict,
    test_admin_user: User,
    test_product: Product,
):
    """Test review creation."""
    payload = {
        "rating": 5,
        "title": "Great Product!",
        "body": "I love this product! It's amazing.",
        "product_id": str(test_product.id),
    }

    response = await client.post("/reviews/", headers=auth_headers, json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["rating"] == 5
    assert data["title"] == "Great Product!"
    assert data["body"] == "I love this product! It's amazing."
    assert data["product_id"] == str(test_product.id)
    assert data["user_id"] == str(test_admin_user.id)


@pytest.mark.asyncio
async def test_read_reviews(
    client: AsyncClient,
    auth_headers: dict,
    test_review: ProductReview,
):
    """Test reading review list."""
    response = await client.get("/reviews/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_read_review(
    client: AsyncClient,
    auth_headers: dict,
    test_review: ProductReview,
):
    """Test reading single review."""
    response = await client.get(f"/reviews/{test_review.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert str(test_review.id) == data["id"]


@pytest.mark.asyncio
async def test_update_review(
    client: AsyncClient,
    auth_headers: dict,
    test_review: ProductReview,
    test_product: Product,
):
    """Test updating review."""
    payload = {
        "id": str(test_review.id),
        "rating": 3,
        "title": "Updated Review",
        "body": "This review has been updated.",
        "product_id": str(test_product.id),
    }

    response = await client.put(
        f"/reviews/{test_review.id}", headers=auth_headers, json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 3
    assert data["title"] == "Updated Review"
    assert data["body"] == "This review has been updated."


@pytest.mark.asyncio
async def test_delete_review(
    client: AsyncClient,
    auth_headers: dict,
    test_review: ProductReview,
):
    """Test deleting review."""
    response = await client.delete(f"/reviews/{test_review.id}", headers=auth_headers)
    assert response.status_code == 204

    response = await client.get(f"/reviews/{test_review.id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(
    client: AsyncClient,
    test_review: ProductReview,
):
    """Test unauthorized access to reviews."""
    response = await client.get("/reviews/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_regular_user_permission(
    client: AsyncClient,
    user_auth_headers: dict,
    test_review: ProductReview,
):
    """Test regular user permissions on reviews."""
    response = await client.get("/reviews/", headers=user_auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"


@pytest.mark.asyncio
async def test_invalid_review_id(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test accessing non-existent review."""
    import uuid

    fake_id = str(uuid.uuid4())
    response = await client.get(f"/reviews/{fake_id}", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Product Review not found"


@pytest.mark.asyncio
async def test_create_vote(
    client: AsyncClient,
    auth_headers: dict,
    test_user: User,
    test_review: ProductReview,
):
    """Test vote creation."""
    payload = {
        "vote": VoteEnum.upvote,
    }

    response = await client.post(
        f"/reviews/{test_review.id}/votes/", headers=auth_headers, json=payload
    )
    assert response.status_code == 201
    data = response.json()

    assert data["vote"] == 1

    # async with AsyncSession() as session:
    #     updated_review = await session.get(ProductReview, test_review.id)
    #     assert updated_review.total_votes == 1


@pytest.mark.asyncio
async def test_update_vote(
    client: AsyncClient,
    auth_headers: dict,
    test_user: User,
    test_review: ProductReview,
    test_vote: Vote,
):
    """Test vote updation."""
    payload = {
        "id": str(test_vote.id),
        "vote": VoteEnum.downvote,
    }

    response = await client.put(
        f"/reviews/{test_review.id}/votes/{test_vote.id}",
        headers=auth_headers,
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()

    assert data["vote"] == -1

    # async with AsyncSession() as session:
    #     updated_review = await session.get(ProductReview, test_review.id)
    #     assert updated_review.total_votes == -1


@pytest.mark.asyncio
async def test_delete_vote(
    client: AsyncClient,
    auth_headers: dict,
    test_user: User,
    test_review: ProductReview,
    test_vote: Vote,
):
    """Test vote deletion."""
    response = await client.delete(
        f"/reviews/{test_review.id}/votes/{test_vote.id}", headers=auth_headers
    )
    assert response.status_code == 204

    # async with AsyncSession() as session:
    #     deleted_vote = await session.get(Vote, vote.id)
    #     assert deleted_vote is None

    # async with AsyncSession() as session:
    #     updated_review = await session.get(ProductReview, test_review.id)
    #     assert updated_review.total_votes == 0
