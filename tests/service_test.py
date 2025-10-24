from datetime import timedelta
import uuid
from fastapi import status
from decimal import Decimal

from models.user import User
from models.service import Service
from security.auth import create_access_token, get_password_hash


def test_get_services_public(client, db_session):
    """Test public endpoint to get all active services"""
    # Create admin user to create services
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

    # Create active service
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

    response = client.get("/api/services")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "House Cleaning"
    assert data[0]["is_active"] == True


def test_get_services_with_filters(client, db_session):
    """Test public endpoint with price and search filters"""
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

    # Create services with different prices
    service1 = Service(
        id=str(uuid.uuid4()),
        title="Basic Cleaning",
        description="Basic house cleaning",
        price=Decimal("50.00"),
        duration_minutes=60,
        is_active=True,
        owner_id=admin.id,
    )
    service2 = Service(
        id=str(uuid.uuid4()),
        title="Premium Cleaning",
        description="Premium house cleaning service",
        price=Decimal("150.00"),
        duration_minutes=180,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add_all([service1, service2])
    db_session.commit()

    # Test price filter
    response = client.get("/api/services?price_min=100")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Premium Cleaning"

    # Test search filter
    response = client.get("/api/services?q=Basic")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Basic Cleaning"


def test_get_service_by_id_public(client, db_session):
    """Test public endpoint to get service by ID"""
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

    # Create service
    service = Service(
        id=str(uuid.uuid4()),
        title="Garden Maintenance",
        description="Professional garden maintenance",
        price=Decimal("75.50"),
        duration_minutes=90,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    response = client.get(f"/api/services/{service.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(service.id)
    assert data["title"] == "Garden Maintenance"
    assert float(data["price"]) == 75.50


def test_get_inactive_service_public_fails(client, db_session):
    """Test that inactive services are not accessible via public endpoint"""
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

    response = client.get(f"/api/services/{service.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_admin_create_service(client, db_session):
    """Test admin can create services"""
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

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    service_data = {
        "title": "New Service",
        "description": "A brand new service",
        "price": 125.00,
        "duration_minutes": 150,
    }

    response = client.post("/api/services", json=service_data, headers=admin_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "New Service"
    assert float(data["price"]) == 125.00
    assert data["owner_id"] == str(admin.id)
    assert data["is_active"] == True


def test_regular_user_cannot_create_service(client, db_session):
    """Test regular users cannot create services"""
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

    service_data = {
        "title": "Unauthorized Service",
        "description": "This should fail",
        "price": 100.00,
        "duration_minutes": 60,
    }

    response = client.post("/api/services", json=service_data, headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_update_service(client, db_session):
    """Test admin can update services"""
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

    # Create service
    service = Service(
        id=str(uuid.uuid4()),
        title="Original Service",
        description="Original description",
        price=Decimal("100.00"),
        duration_minutes=60,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    update_data = {"title": "Updated Service", "price": 120.00}

    response = client.patch(
        f"/api/services/{service.id}", json=update_data, headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Service"
    assert float(data["price"]) == 120.00
    assert data["description"] == "Original description"  # Unchanged


def test_admin_delete_service(client, db_session):
    """Test admin can soft delete services"""
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

    # Create service
    service = Service(
        id=str(uuid.uuid4()),
        title="Service to Delete",
        description="This will be deleted",
        price=Decimal("80.00"),
        duration_minutes=45,
        is_active=True,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(f"/api/services/{service.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_active"] == False  # Soft deleted


def test_admin_get_all_services(client, db_session):
    """Test admin can get all services including inactive ones"""
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

    # Create active and inactive services
    active_service = Service(
        id=str(uuid.uuid4()),
        title="Active Service",
        description="This is active",
        price=Decimal("100.00"),
        duration_minutes=60,
        is_active=True,
        owner_id=admin.id,
    )
    inactive_service = Service(
        id=str(uuid.uuid4()),
        title="Inactive Service",
        description="This is inactive",
        price=Decimal("200.00"),
        duration_minutes=120,
        is_active=False,
        owner_id=admin.id,
    )
    db_session.add_all([active_service, inactive_service])
    db_session.commit()

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get("/api/admin/services", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2

    # Check that both active and inactive services are returned
    titles = [service["title"] for service in data]
    assert "Active Service" in titles
    assert "Inactive Service" in titles


def test_admin_get_service_by_id(client, db_session):
    """Test admin can get any service including inactive ones"""
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

    # Create inactive service
    service = Service(
        id=str(uuid.uuid4()),
        title="Admin Only Service",
        description="Only admin can see this",
        price=Decimal("150.00"),
        duration_minutes=90,
        is_active=False,
        owner_id=admin.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(f"/api/admin/services/{service.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(service.id)
    assert data["is_active"] == False


def test_regular_user_cannot_access_admin_endpoints(client, db_session):
    """Test regular users cannot access admin service endpoints"""
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

    # Test admin endpoints
    response = client.get("/api/admin/services", headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    service_id = str(uuid.uuid4())
    response = client.get(f"/api/admin/services/{service_id}", headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_service_invalid_data(client, db_session):
    """Test service creation with invalid data"""
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

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Test with incomplete data
    invalid_service_data = {
        "title": "Invalid Service",
        "description": "This has invalid price",
        "duration_minutes": 60,
    }

    response = client.post(
        "/api/services", json=invalid_service_data, headers=admin_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_nonexistent_service(client, db_session):
    """Test updating a service that doesn't exist"""
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

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    nonexistent_id = str(uuid.uuid4())
    update_data = {"title": "Updated Title"}

    response = client.patch(
        f"/api/services/{nonexistent_id}", json=update_data, headers=admin_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_service(client, db_session):
    """Test deleting a service that doesn't exist"""
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

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    nonexistent_id = str(uuid.uuid4())
    response = client.delete(f"/api/services/{nonexistent_id}", headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_nonexistent_service_public(client):
    """Test getting a service that doesn't exist via public endpoint"""
    nonexistent_id = str(uuid.uuid4())
    response = client.get(f"/api/services/{nonexistent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_services_pagination(client, db_session):
    """Test service listing pagination"""
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

    # Create multiple services
    services = []
    for i in range(5):
        service = Service(
            id=str(uuid.uuid4()),
            title=f"Service {i+1}",
            description=f"Description for service {i+1}",
            price=Decimal(f"{100 + i*10}.00"),
            duration_minutes=60,
            is_active=True,
            owner_id=admin.id,
        )
        services.append(service)

    db_session.add_all(services)
    db_session.commit()

    # Test pagination
    response = client.get("/api/services?skip=0&limit=3")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3

    response = client.get("/api/services?skip=3&limit=3")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2  # Should get at least the remaining 2 services


def test_unauthorized_access_to_protected_endpoints(client):
    """Test accessing protected endpoints without authentication"""
    service_data = {
        "title": "Unauthorized Service",
        "description": "This should fail",
        "price": 100.00,
        "duration_minutes": 60,
    }

    service_id = str(uuid.uuid4())
    update_data = {"title": "Updated Title"}

    # Test create service without auth
    response = client.post("/api/services", json=service_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test update service without auth
    response = client.patch(f"/api/services/{service_id}", json=update_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test delete service without auth
    response = client.delete(f"/api/services/{service_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test admin endpoints without auth
    response = client.get("/api/admin/services")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get(f"/api/admin/services/{service_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
