from datetime import timedelta, datetime, timezone
import uuid
from fastapi import status
from decimal import Decimal
from models.user import User
from models.service import Service
from models.booking import Booking
from models.review import Review
from security.auth import create_access_token, get_password_hash


def test_create_review_success(client, db_session):
    """Test creating a review successfully for a completed booking"""
    # Create admin user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    # Create regular user
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create service
    service = Service(
        id=str(uuid.uuid4()),
        title="House Cleaning",
        description="Professional house cleaning service",
        price=Decimal("99.99"),
        duration_minutes=120,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    # Create completed booking
    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=1),
        end_time=datetime.now(timezone.utc) - timedelta(hours=22),
        status="completed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    # Create user token
    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Review data
    review_data = {
        "booking_id": str(booking.id),
        "rating": 5,
        "comment": "Excellent service! Very professional and thorough.",
    }

    response = client.post("/api/reviews", json=review_data, headers=user_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["booking_id"] == str(booking.id)
    assert data["rating"] == 5
    assert data["comment"] == "Excellent service! Very professional and thorough."


def test_create_review_booking_not_completed(client, db_session):
    """Test creating a review fails for non-completed booking"""
    # Create admin and user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("50.00"),
        duration_minutes=60,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    # Create pending booking
    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) + timedelta(days=1),
        end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=1),
        status="pending",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    review_data = {
        "booking_id": str(booking.id),
        "rating": 4,
        "comment": "This should fail",
    }

    response = client.post("/api/reviews", json=review_data, headers=user_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_review_duplicate(client, db_session):
    """Test creating a duplicate review fails"""
    # Create admin and user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service and completed booking
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("75.00"),
        duration_minutes=90,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=1),
        end_time=datetime.now(timezone.utc) - timedelta(hours=22),
        status="completed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    # Create existing review
    existing_review = Review(
        id=str(uuid.uuid4()), booking_id=booking.id, rating=4, comment="Existing review"
    )
    db_session.add(existing_review)
    db_session.commit()

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    review_data = {
        "booking_id": str(booking.id),
        "rating": 5,
        "comment": "This should fail as duplicate",
    }

    response = client.post("/api/reviews", json=review_data, headers=user_headers)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_get_reviews_public(client, db_session):
    """Test getting reviews with public access"""
    # Create admin and user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service, booking, and review
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("60.00"),
        duration_minutes=60,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=1),
        end_time=datetime.now(timezone.utc) - timedelta(hours=23),
        status="completed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    review = Review(
        id=str(uuid.uuid4()), booking_id=booking.id, rating=5, comment="Great service!"
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    response = client.get(f"/api/services/{service.id}/reviews")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["id"] == str(review.id)
    assert data[0]["rating"] == 5


def test_get_reviews_with_filters(client, db_session):
    """Test getting reviews with filters"""
    # Create admin and user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service, bookings, and reviews with different ratings
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("80.00"),
        duration_minutes=90,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    # Create multiple bookings and reviews
    bookings_reviews = []
    for i, rating in enumerate([3, 5], 1):
        booking = Booking(
            id=str(uuid.uuid4()),
            user_id=user.id,
            service_id=service.id,
            start_time=datetime.now(timezone.utc) - timedelta(days=i),
            end_time=datetime.now(timezone.utc) - timedelta(days=i, hours=-1),
            status="completed",
        )
        db_session.add(booking)
        db_session.commit()
        db_session.refresh(booking)

        review = Review(
            id=str(uuid.uuid4()),
            booking_id=booking.id,
            rating=rating,
            comment=f"Review with rating {rating}",
        )
        db_session.add(review)
        bookings_reviews.append((booking, review))

    db_session.commit()

    # Test rating filter
    response = client.get(f"/api/services/{service.id}/reviews?min_rating=5")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert all(review["rating"] >= 5 for review in data)


def test_get_review_by_id(client, db_session):
    """Test getting a specific review by ID"""
    # Create admin and user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service, booking, and review
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("70.00"),
        duration_minutes=75,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=1),
        end_time=datetime.now(timezone.utc) - timedelta(hours=22),
        status="completed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    review = Review(
        id=str(uuid.uuid4()),
        booking_id=booking.id,
        rating=4,
        comment="Good service overall",
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(f"/api/reviews/{review.id}", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(review.id)
    assert data["rating"] == 4
    assert data["comment"] == "Good service overall"


def test_update_review_success(client, db_session):
    """Test updating a review successfully"""
    # Create admin and user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service, booking, and review
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("85.00"),
        duration_minutes=100,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=1),
        end_time=datetime.now(timezone.utc) - timedelta(hours=22),
        status="completed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    review = Review(
        id=str(uuid.uuid4()),
        booking_id=booking.id,
        rating=3,
        comment="Original comment",
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    update_data = {"rating": 5, "comment": "Updated comment - much better!"}

    response = client.patch(
        f"/api/reviews/{review.id}", json=update_data, headers=user_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Updated comment - much better!"


def test_update_review_unauthorized(client, db_session):
    """Test updating review by unauthorized user fails"""
    # Create admin and users
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user1 = User(
        id=str(uuid.uuid4()),
        name="User One",
        email="user1@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
        is_active=True,
        status="active",
    )
    user2 = User(
        id=str(uuid.uuid4()),
        name="User Two",
        email="user2@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user1, user2])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user1)
    db_session.refresh(user2)

    # Create service, booking, and review for user1
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("60.00"),
        duration_minutes=60,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user1.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=1),
        end_time=datetime.now(timezone.utc) - timedelta(hours=23),
        status="completed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    review = Review(
        id=str(uuid.uuid4()), booking_id=booking.id, rating=4, comment="User1's review"
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    # Try to update with user2's token
    user2_token, _ = create_access_token(
        data={"sub": str(user2.id)}, expires_delta=timedelta(minutes=30)
    )
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    update_data = {"rating": 1, "comment": "Unauthorized update"}

    response = client.patch(
        f"/api/reviews/{review.id}", json=update_data, headers=user2_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_review_success(client, db_session):
    """Test deleting a review successfully"""
    # Create admin and user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service, booking, and review
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("55.00"),
        duration_minutes=60,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=1),
        end_time=datetime.now(timezone.utc) - timedelta(hours=23),
        status="completed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    review = Review(
        id=str(uuid.uuid4()),
        booking_id=booking.id,
        rating=3,
        comment="Review to be deleted",
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    response = client.delete(f"/api/reviews/{review.id}", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK


def test_get_booking_review(client, db_session):
    """Test getting review for a specific booking"""
    # Create admin and user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service, booking, and review
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("90.00"),
        duration_minutes=120,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=1),
        end_time=datetime.now(timezone.utc) - timedelta(hours=22),
        status="completed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    review = Review(
        id=str(uuid.uuid4()),
        booking_id=booking.id,
        rating=5,
        comment="Excellent service for this booking",
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(f"/api/bookings/{booking.id}/review", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["booking_id"] == str(booking.id)
    assert data["rating"] == 5


def test_get_service_review_stats(client, db_session):
    """Test getting review statistics for a service"""
    # Create admin and users
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user1 = User(
        id=str(uuid.uuid4()),
        name="User One",
        email="user1@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
        is_active=True,
        status="active",
    )
    user2 = User(
        id=str(uuid.uuid4()),
        name="User Two",
        email="user2@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user1, user2])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user1)
    db_session.refresh(user2)

    # Create service
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service for stats",
        price=Decimal("100.00"),
        duration_minutes=120,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    # Create multiple bookings and reviews
    users = [user1, user2]
    ratings = [4, 5]

    for i, (user, rating) in enumerate(zip(users, ratings)):
        booking = Booking(
            id=str(uuid.uuid4()),
            user_id=user.id,
            service_id=service.id,
            start_time=datetime.now(timezone.utc) - timedelta(days=i + 1),
            end_time=datetime.now(timezone.utc) - timedelta(days=i + 1, hours=-2),
            status="completed",
        )
        db_session.add(booking)
        db_session.commit()
        db_session.refresh(booking)

        review = Review(
            id=str(uuid.uuid4()),
            booking_id=booking.id,
            rating=rating,
            comment=f"Review {i+1}",
        )
        db_session.add(review)

    db_session.commit()

    response = client.get(f"/api/services/{service.id}/reviews/stats")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_reviews"] == 2
    assert data["average_rating"] == 4.5
    assert data["min_rating"] == 4
    assert data["max_rating"] == 5


def test_admin_delete_any_review(client, db_session):
    """Test admin can delete any review"""
    # Create admin and user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service, booking, and review
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("75.00"),
        duration_minutes=90,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=1),
        end_time=datetime.now(timezone.utc) - timedelta(hours=22),
        status="completed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    review = Review(
        id=str(uuid.uuid4()),
        booking_id=booking.id,
        rating=2,
        comment="Admin will delete this",
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(f"/api/reviews/{review.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK


def test_get_user_reviews(client, db_session):
    """Test getting current user's reviews"""
    # Create admin and user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service, booking, and review
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("65.00"),
        duration_minutes=70,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=1),
        end_time=datetime.now(timezone.utc) - timedelta(hours=22),
        status="completed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    review = Review(
        id=str(uuid.uuid4()),
        booking_id=booking.id,
        rating=4,
        comment="User's own review",
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get("/api/users/me/reviews", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["id"] == str(review.id)


def test_admin_get_all_reviews(client, db_session):
    """Test admin can get all reviews"""
    # Create admin and user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service, booking, and review
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("80.00"),
        duration_minutes=95,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=1),
        end_time=datetime.now(timezone.utc) - timedelta(hours=22),
        status="completed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    review = Review(
        id=str(uuid.uuid4()),
        booking_id=booking.id,
        rating=3,
        comment="Admin can see this",
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get("/api/admin/reviews", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1


def test_create_review_invalid_rating(client, db_session):
    """Test creating review with invalid rating fails"""
    # Create admin and user
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service and booking
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("50.00"),
        duration_minutes=60,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=1),
        end_time=datetime.now(timezone.utc) - timedelta(hours=23),
        status="completed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Test invalid rating (out of range)
    invalid_review_data = {
        "booking_id": str(booking.id),
        "rating": 6,
        "comment": "This should fail",
    }

    response = client.post(
        "/api/reviews", json=invalid_review_data, headers=user_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_get_nonexistent_review(client, db_session):
    """Test getting a review that doesn't exist"""
    # Create user for auth
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    nonexistent_id = str(uuid.uuid4())
    response = client.get(f"/api/reviews/{nonexistent_id}", headers=user_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_unauthorized_access_to_protected_endpoints(client):
    """Test accessing protected endpoints without authentication"""
    review_id = str(uuid.uuid4())
    booking_id = str(uuid.uuid4())

    review_data = {"booking_id": booking_id, "rating": 5, "comment": "This should fail"}

    update_data = {"rating": 4}

    # Test endpoints without auth
    response = client.post("/api/reviews", json=review_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.patch(f"/api/reviews/{review_id}", json=update_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.delete(f"/api/reviews/{review_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get(f"/api/bookings/{booking_id}/review")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_regular_user_cannot_access_admin_endpoints(client, db_session):
    """Test regular users cannot access admin review endpoints"""
    # Create regular user
    user = User(
        id=str(uuid.uuid4()),
        name="Regular User",
        email="user@example.com",
        password_hash=get_password_hash("userpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    user_id = str(uuid.uuid4())

    # Test admin endpoints
    response = client.get("/api/admin/reviews", headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.get(f"/api/admin/users/{user_id}/reviews", headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_reviews_pagination(client, db_session):
    """Test review listing pagination"""
    # Create admin and users
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="admin",
        is_active=True,
        status="active",
    )
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_active=True,
        status="active",
    )
    db_session.add_all([admin, user])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user)

    # Create service
    service = Service(
        id=str(uuid.uuid4()),
        title="Test Service",
        description="Test service",
        price=Decimal("60.00"),
        duration_minutes=60,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    # Create multiple bookings and reviews
    for i in range(5):
        booking = Booking(
            id=str(uuid.uuid4()),
            user_id=user.id,
            service_id=service.id,
            start_time=datetime.now(timezone.utc) - timedelta(days=i + 1),
            end_time=datetime.now(timezone.utc) - timedelta(days=i + 1, hours=-1),
            status="completed",
        )
        db_session.add(booking)
        db_session.commit()
        db_session.refresh(booking)

        review = Review(
            id=str(uuid.uuid4()),
            booking_id=booking.id,
            rating=5,
            comment=f"Review {i+1}",
        )
        db_session.add(review)

    db_session.commit()

    # Test pagination
    response = client.get(f"/api/services/{service.id}/reviews?skip=0&limit=3")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3

    response = client.get(f"/api/services/{service.id}/reviews?skip=3&limit=3")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2
