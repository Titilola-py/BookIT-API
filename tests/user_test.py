from datetime import timedelta
import uuid
from fastapi import status
from models.user import User
from security.auth import create_access_token, get_password_hash


def test_user_registration_success(client):
    sample_user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    response = client.post("/api/auth/register", json=sample_user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == sample_user_data["email"]
    assert data["name"] == sample_user_data["name"]
    assert "password" not in data


def test_user_registration_duplicate_email(client):
    sample_user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    client.post("/api/auth/register", json=sample_user_data)
    response = client.post("/api/auth/register", json=sample_user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_user_login_success(client, db_session):
    sample_user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    # Manually create user in DB with proper UUID
    user = User(
        id=str(uuid.uuid4()),  # Generate proper UUID string
        name=sample_user_data["name"],
        email=sample_user_data["email"],
        password_hash=get_password_hash(sample_user_data["password"]),
        role=sample_user_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    login_data = {
        "email": sample_user_data["email"],
        "password": sample_user_data["password"],
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == sample_user_data["email"]


def test_user_login_invalid_credentials(client, db_session):
    sample_user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    user = User(
        id=str(uuid.uuid4()),
        name=sample_user_data["name"],
        email=sample_user_data["email"],
        password_hash=get_password_hash(sample_user_data["password"]),
        role=sample_user_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    login_data = {"email": "test@example.com", "password": "wrongpassword"}
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_login_nonexistent_user(client):
    login_data = {"email": "nonexistent@example.com", "password": "somepassword"}
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_endpoint_without_token(client):
    response = client.get("/api/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_endpoint_with_valid_token(client, db_session):
    sample_user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    user = User(
        id=str(uuid.uuid4()),
        name=sample_user_data["name"],
        email=sample_user_data["email"],
        password_hash=get_password_hash(sample_user_data["password"]),
        role=sample_user_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    access_token, _ = create_access_token(
        data={"sub": str(user.id)},  # Ensure UUID is converted to string for JWT
        expires_delta=timedelta(minutes=30),
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_protected_endpoint_with_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_token_refresh_success(client, db_session):
    sample_user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    user = User(
        id=str(uuid.uuid4()),
        name=sample_user_data["name"],
        email=sample_user_data["email"],
        password_hash=get_password_hash(sample_user_data["password"]),
        role=sample_user_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    login_data = {
        "email": sample_user_data["email"],
        "password": sample_user_data["password"],
    }
    login_response = client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == status.HTTP_200_OK

    refresh_token = login_response.json()["refresh_token"]
    refresh_data = {"refresh_token": refresh_token}
    response = client.post("/api/auth/refresh", json=refresh_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_token_refresh_invalid_token(client):
    refresh_data = {"refresh_token": "invalid_refresh_token"}
    response = client.post("/api/auth/refresh", json=refresh_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_profile(client, db_session):
    sample_user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    user = User(
        id=str(uuid.uuid4()),
        name=sample_user_data["name"],
        email=sample_user_data["email"],
        password_hash=get_password_hash(sample_user_data["password"]),
        role=sample_user_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    access_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user.email
    assert data["name"] == user.name


def test_update_user_profile(client, db_session):
    sample_user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    user = User(
        id=str(uuid.uuid4()),
        name=sample_user_data["name"],
        email=sample_user_data["email"],
        password_hash=get_password_hash(sample_user_data["password"]),
        role=sample_user_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    access_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    update_data = {"name": "Updated Test User"}
    response = client.patch("/api/me", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Test User"


def test_admin_get_all_users(client, db_session):
    # Create admin
    admin_data = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "role": "admin",
    }
    admin = User(
        id=str(uuid.uuid4()),
        name=admin_data["name"],
        email=admin_data["email"],
        password_hash=get_password_hash(admin_data["password"]),
        role=admin_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    # Create regular user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    user = User(
        id=str(uuid.uuid4()),
        name=user_data["name"],
        email=user_data["email"],
        password_hash=get_password_hash(user_data["password"]),
        role=user_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/users", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2


def test_regular_user_cannot_get_all_users(client, db_session):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    user = User(
        id=str(uuid.uuid4()),
        name=user_data["name"],
        email=user_data["email"],
        password_hash=get_password_hash(user_data["password"]),
        role=user_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user_token, _ = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
    )
    auth_headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/api/users", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_get_user_by_id(client, db_session):
    admin_data = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "role": "admin",
    }
    admin = User(
        id=str(uuid.uuid4()),
        name=admin_data["name"],
        email=admin_data["email"],
        password_hash=get_password_hash(admin_data["password"]),
        role=admin_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    user = User(
        id=str(uuid.uuid4()),
        name=user_data["name"],
        email=user_data["email"],
        password_hash=get_password_hash(user_data["password"]),
        role=user_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/api/users/{user.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(user.id)


def test_admin_update_user(client, db_session):
    admin_data = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "role": "admin",
    }
    admin = User(
        id=str(uuid.uuid4()),
        name=admin_data["name"],
        email=admin_data["email"],
        password_hash=get_password_hash(admin_data["password"]),
        role=admin_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    user = User(
        id=str(uuid.uuid4()),
        name=user_data["name"],
        email=user_data["email"],
        password_hash=get_password_hash(user_data["password"]),
        role=user_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    update_data = {"name": "Admin Updated Name"}
    response = client.patch(
        f"/api/users/{user.id}", json=update_data, headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Admin Updated Name"


def test_admin_delete_user(client, db_session):
    admin_data = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "role": "admin",
    }
    admin = User(
        id=str(uuid.uuid4()),
        name=admin_data["name"],
        email=admin_data["email"],
        password_hash=get_password_hash(admin_data["password"]),
        role=admin_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
    }
    user = User(
        id=str(uuid.uuid4()),
        name=user_data["name"],
        email=user_data["email"],
        password_hash=get_password_hash(user_data["password"]),
        role=user_data["role"],
        is_active=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    admin_token, _ = create_access_token(
        data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=30)
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/api/users/{user.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
