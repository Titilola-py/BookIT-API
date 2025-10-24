from datetime import timedelta, datetime, timezone
import uuid
from fastapi import status
from decimal import Decimal

from models.user import User
from models.service import Service
from models.booking import Booking
from security.auth import create_access_token, get_password_hash


def test_create_booking_success(client, db_session):
    """Test creating a booking successfully"""
    # Create admin user for service ownership
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

    # Create regular user for booking
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

    # Create user token
    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Booking data - future times
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    booking_data = {
        "service_id": str(service.id),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response = client.post("/api/bookings", json=booking_data, headers=user_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["service_id"] == str(service.id)
    assert data["user_id"] == str(user.id)
    assert data["status"] == "pending"


def test_create_booking_inactive_service(client, db_session):
    """Test booking creation fails for inactive service"""
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

    # Create inactive service
    service = Service(
        id=str(uuid.uuid4()),
        title="Inactive Service",
        description="This service is inactive",
        price=Decimal("100.00"),
        duration_minutes=60,
        is_active=False,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    booking_data = {
        "service_id": str(service.id),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response = client.post("/api/bookings", json=booking_data, headers=user_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_booking_time_conflict(client, db_session):
    """Test booking creation fails due to time conflict"""
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

    # Create users
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
    db_session.add_all([user1, user2])
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)

    # Create service
    service = Service(
        id=str(uuid.uuid4()),
        title="Cleaning Service",
        description="Professional cleaning",
        price=Decimal("80.00"),
        duration_minutes=120,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    # Create first booking
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    existing_booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user1.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
        status="confirmed",
    )
    db_session.add(existing_booking)
    db_session.commit()

    # Try to create conflicting booking
    user2_token, _ = create_access_token(
        data={"sub": str(user2.id)}, expires_delta=timedelta(minutes=30)
    )
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # Overlapping time
    conflict_start = start_time + timedelta(minutes=30)
    conflict_end = end_time + timedelta(minutes=30)

    booking_data = {
        "service_id": str(service.id),
        "start_time": conflict_start.isoformat(),
        "end_time": conflict_end.isoformat(),
    }

    response = client.post("/api/bookings", json=booking_data, headers=user2_headers)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_booking_invalid_time(client, db_session):
    """Test booking creation with invalid time (past time)"""
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

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Past time
    start_time = datetime.now(timezone.utc) - timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)

    booking_data = {
        "service_id": str(service.id),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response = client.post("/api/bookings", json=booking_data, headers=user_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_get_user_bookings(client, db_session):
    """Test getting user's own bookings"""
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
        price=Decimal("75.00"),
        duration_minutes=90,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    # Create booking
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1, minutes=30)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
        status="pending",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get("/api/bookings", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["id"] == str(booking.id)
    assert data[0]["user_id"] == str(user.id)


def test_get_booking_by_id(client, db_session):
    """Test getting booking by ID (owner access)"""
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
        price=Decimal("60.00"),
        duration_minutes=60,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
        status="confirmed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(f"/api/bookings/{booking.id}", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(booking.id)
    assert data["status"] == "confirmed"


def test_get_booking_unauthorized_access(client, db_session):
    """Test that users cannot access other users' bookings"""
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

    # Create service and booking for user1
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

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user1.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
        status="pending",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    # Try to access with user2's token
    user2_token, _ = create_access_token(
        data={"sub": str(user2.id)}, expires_delta=timedelta(minutes=30)
    )
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    response = client.get(f"/api/bookings/{booking.id}", headers=user2_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_booking_reschedule(client, db_session):
    """Test rescheduling a booking (user can reschedule their own pending/confirmed bookings)"""
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
        price=Decimal("70.00"),
        duration_minutes=90,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1, minutes=30)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
        status="pending",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Reschedule to different time
    new_start_time = datetime.now(timezone.utc) + timedelta(days=2)
    new_end_time = new_start_time + timedelta(hours=1, minutes=30)

    update_data = {
        "start_time": new_start_time.isoformat(),
        "end_time": new_end_time.isoformat(),
    }

    response = client.patch(
        f"/api/bookings/{booking.id}", json=update_data, headers=user_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(booking.id)
    # Check that times were updated (comparing the date part)
    assert new_start_time.date().isoformat() in data["start_time"]


def test_update_booking_cancel(client, db_session):
    """Test cancelling a booking"""
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
        price=Decimal("65.00"),
        duration_minutes=75,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1, minutes=15)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
        status="confirmed",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    update_data = {"status": "cancelled"}

    response = client.patch(
        f"/api/bookings/{booking.id}", json=update_data, headers=user_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "cancelled"


def test_delete_booking(client, db_session):
    """Test deleting a booking (before start time)"""
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
        price=Decimal("55.00"),
        duration_minutes=60,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
        status="pending",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    response = client.delete(f"/api/bookings/{booking.id}", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK


def test_admin_get_all_bookings(client, db_session):
    """Test admin can get all bookings"""
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
        description="Test service",
        price=Decimal("85.00"),
        duration_minutes=105,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    # Create bookings for both users
    start_time1 = datetime.now(timezone.utc) + timedelta(days=1)
    end_time1 = start_time1 + timedelta(hours=1, minutes=45)

    start_time2 = datetime.now(timezone.utc) + timedelta(days=2)
    end_time2 = start_time2 + timedelta(hours=1, minutes=45)

    booking1 = Booking(
        id=str(uuid.uuid4()),
        user_id=user1.id,
        service_id=service.id,
        start_time=start_time1,
        end_time=end_time1,
        status="pending",
    )
    booking2 = Booking(
        id=str(uuid.uuid4()),
        user_id=user2.id,
        service_id=service.id,
        start_time=start_time2,
        end_time=end_time2,
        status="confirmed",
    )
    db_session.add_all([booking1, booking2])
    db_session.commit()

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get("/api/admin/bookings", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2


def test_admin_update_booking_status(client, db_session):
    """Test admin can update booking status"""
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
        price=Decimal("90.00"),
        duration_minutes=120,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
        status="pending",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.patch(
        f"/api/admin/bookings/{booking.id}/status?status=confirmed",
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "confirmed"


def test_admin_get_service_bookings(client, db_session):
    """Test admin can get all bookings for a specific service"""
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

    # Create services
    service1 = Service(
        id=str(uuid.uuid4()),
        title="Service One",
        description="First service",
        price=Decimal("60.00"),
        duration_minutes=60,
        is_active=True,
        owner_id=admin.id,
    )
    service2 = Service(
        id=str(uuid.uuid4()),
        title="Service Two",
        description="Second service",
        price=Decimal("80.00"),
        duration_minutes=90,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add_all([service1, service2])
    db_session.commit()
    db_session.refresh(service1)
    db_session.refresh(service2)

    # Create bookings for service1
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    booking1 = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service1.id,
        start_time=start_time,
        end_time=end_time,
        status="pending",
    )
    booking2 = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service2.id,  # Different service
        start_time=start_time + timedelta(hours=2),
        end_time=end_time + timedelta(hours=3),
        status="confirmed",
    )
    db_session.add_all([booking1, booking2])
    db_session.commit()

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(
        f"/api/services/{service1.id}/bookings", headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["service_id"] == str(service1.id)


def test_regular_user_cannot_access_admin_endpoints(client, db_session):
    """Test regular users cannot access admin booking endpoints"""
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

    booking_id = str(uuid.uuid4())
    service_id = str(uuid.uuid4())

    # Test admin endpoints
    response = client.get("/api/admin/bookings", headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.patch(
        f"/api/admin/bookings/{booking_id}/status?status=confirmed",
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.get(f"/api/services/{service_id}/bookings", headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_booking_with_filters(client, db_session):
    """Test getting bookings with status and date filters"""
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
        price=Decimal("70.00"),
        duration_minutes=90,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    # Create bookings with different statuses
    start_time1 = datetime.now(timezone.utc) + timedelta(days=1)
    end_time1 = start_time1 + timedelta(hours=1, minutes=30)

    start_time2 = datetime.now(timezone.utc) + timedelta(days=2)
    end_time2 = start_time2 + timedelta(hours=1, minutes=30)

    booking1 = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=start_time1,
        end_time=end_time1,
        status="pending",
    )
    booking2 = Booking(
        id=str(uuid.uuid4()),
        user_id=user.id,
        service_id=service.id,
        start_time=start_time2,
        end_time=end_time2,
        status="confirmed",
    )
    db_session.add_all([booking1, booking2])
    db_session.commit()

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Test status filter
    response = client.get("/api/bookings?status=pending", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1


def test_booking_pagination(client, db_session):
    """Test booking listing pagination"""
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

    # Create multiple bookings
    bookings = []
    for i in range(5):
        start_time = datetime.now(timezone.utc) + timedelta(days=i + 1)
        end_time = start_time + timedelta(hours=1)

        booking = Booking(
            id=str(uuid.uuid4()),
            user_id=user.id,
            service_id=service.id,
            start_time=start_time,
            end_time=end_time,
            status="pending",
        )
        bookings.append(booking)

    db_session.add_all(bookings)
    db_session.commit()

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Test pagination
    response = client.get("/api/bookings?skip=0&limit=3", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3

    response = client.get("/api/bookings?skip=3&limit=3", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2


def test_unauthorized_access_to_booking_endpoints(client):
    """Test accessing booking endpoints without authentication"""
    booking_id = str(uuid.uuid4())

    booking_data = {
        "service_id": str(uuid.uuid4()),
        "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "end_time": (
            datetime.now(timezone.utc) + timedelta(days=1, hours=1)
        ).isoformat(),
    }

    update_data = {"status": "confirmed"}

    # Test endpoints without auth
    response = client.post("/api/bookings", json=booking_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get("/api/bookings")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get(f"/api/bookings/{booking_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.patch(f"/api/bookings/{booking_id}", json=update_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.delete(f"/api/bookings/{booking_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get("/api/admin/bookings")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_nonexistent_booking(client, db_session):
    """Test getting a booking that doesn't exist"""
    # Create user
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
    response = client.get(f"/api/bookings/{nonexistent_id}", headers=user_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_nonexistent_booking(client, db_session):
    """Test updating a booking that doesn't exist"""
    # Create user
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
    update_data = {"status": "cancelled"}

    response = client.patch(
        f"/api/bookings/{nonexistent_id}", json=update_data, headers=user_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_booking(client, db_session):
    """Test deleting a booking that doesn't exist"""
    # Create user
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
    response = client.delete(f"/api/bookings/{nonexistent_id}", headers=user_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
