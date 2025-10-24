# BookIt API 📚

A production-ready REST API for a comprehensive booking platform built with FastAPI, PostgreSQL, and industry best practices.

**Live API**:   
**Documentation**:   
**GitHub**: https://github.com/Titilola-py/BookIT-API

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

##  Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)

---

## Overview

BookIt API is a feature-rich booking management system that enables users to discover services, create bookings, and share reviews. Administrators have comprehensive control over users, services, and booking operations. Built with modern backend technologies, the API emphasizes security, scalability, and maintainability.

### Why BookIt?

- **Enterprise-Ready**: Production-tested with comprehensive error handling
- **Secure by Default**: JWT authentication, bcrypt hashing, role-based access control
- **Developer-Friendly**: Auto-generated OpenAPI docs, extensive test coverage
- **Scalable Architecture**: Clean separation of concerns, modular design
- **Type-Safe**: Full Pydantic validation and SQLAlchemy ORM

---

## Features

### Core Functionality

| Feature | Description |
|---------|-------------|
| **User Management** | Registration, authentication, profile management with role-based access |
| **Service Catalog** | Browse, search, and filter available services with detailed information |
| **Booking System** | Complete lifecycle management from creation to completion |
| **Review System** | Rate and review services after booking completion |
| **Admin Dashboard** | Comprehensive administrative control over all resources |

### Technical Highlights

**JWT Authentication** - Secure token-based auth with access & refresh tokens  
**Role-Based Access Control** - Granular permissions for users and admins  
**Booking Conflict Detection** - Prevents double-bookings with 409 responses  
**Database Migrations** - Version-controlled schema with Alembic  
**Comprehensive Testing** - 30+ tests covering critical flows  
**Structured Logging** - Request tracking and performance monitoring  
**Auto-Generated Docs** - Interactive API documentation with Swagger UI  
**Data Validation** - Robust input validation with Pydantic schemas  
**Token Blacklisting** - Secure logout with token invalidation  

---

## Architecture

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Framework** | FastAPI 0.109.0 | High-performance async web framework |
| **Database** | PostgreSQL 14+ | Production-grade relational database |
| **ORM** | SQLAlchemy 2.0.25 | Python SQL toolkit and ORM |
| **Migrations** | Alembic 1.13.1 | Database schema versioning |
| **Validation** | Pydantic 2.5.3 | Data validation using Python type hints |
| **Authentication** | JWT (python-jose) | Secure token-based authentication |
| **Password Hashing** | bcrypt (passlib) | Industry-standard password hashing |
| **Testing** | pytest 7.4.4 | Comprehensive test framework |
| **Deployment** | PipeOps | Cloud platform for deployment |

### Why PostgreSQL?

BookIt uses PostgreSQL over MongoDB for several critical reasons:

1. **ACID Compliance**: Ensures booking transactions are atomic and consistent
2. **Relational Integrity**: Strong foreign key relationships between users, bookings, services, and reviews
3. **Data Validation**: Check constraints prevent invalid states (ratings 1-5, valid statuses)
4. **Conflict Detection**: Complex time-based queries efficiently detect booking overlaps
5. **Mature Ecosystem**: Battle-tested tooling (Alembic, pgAdmin, connection pooling)
6. **Query Performance**: SQL excels at joins and complex queries needed for booking operations

*MongoDB would be better suited for unstructured data, flexible schemas, or horizontal scaling requirements—none of which apply to this use case.*

### Project Structure
```
BookIt-API/
├── alembic/                 # Database migrations
├── crud/                    # CRUD operations
│   ├── booking.py
│   ├── review.py
│   ├── service.py
│   └── user.py
├── database/                # Database configuration
├── middleware/              # Custom middleware
├── models/                  # SQLAlchemy models
│   ├── booking.py
│   ├── review.py
│   ├── service.py
│   ├── token_blacklist.py
│   └── user.py
├── routers/                 # API route handlers
│   ├── booking.py
│   ├── review.py
│   ├── service.py
│   └── user.py
├── schemas/                 # Pydantic schemas
├── security/                # Authentication & authorization
├── services/                # Business logic services
├── tests/                   # Comprehensive test suite
└── main.py                  # Application entry point
```

### Design Patterns

**Layered Architecture**:
```
Router (Presentation) → Service (Business Logic) → CRUD (Data Access) → Models (Database)
```

**Key Principles**:
- **Separation of Concerns**: Each layer has a single responsibility
- **Dependency Injection**: FastAPI's `Depends()` for clean dependency management
- **Repository Pattern**: CRUD modules abstract database operations
- **Schema Validation**: Pydantic ensures type safety and data integrity

---

## Getting Started

### Prerequisites

- **Python**: 3.13+ (3.11+ supported)
- **PostgreSQL**: 14+ for production
- **Git**: For version control
- **pip**: Python package manager

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/Titilola-py/bookit-api.git
cd bookit-api
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required Environment Variables**:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/bookit
SECRET_KEY=your-secure-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_EMAIL=admin@bookit.com
ADMIN_PASSWORD=SecureAdminPass123!
```

#### 5. Setup Database

```bash
# Create PostgreSQL database
createdb bookit

# Or using psql
psql -U postgres
CREATE DATABASE bookit;
\q
```

#### 6. Run Migrations

```bash
# Apply database migrations
alembic upgrade head

# Initialize with admin user (optional)
python init_db.py
```

#### 7. Start Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 8. Verify Installation

Open your browser and visit:

- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

##  API Documentation

### Base URL

**Local**: `http://localhost:8000`  
**Production**: `https://bookit-api.pipeops.com`

### Authentication

All protected endpoints require JWT authentication:

```bash
Authorization: Bearer <your-jwt-token>
```

### Endpoints Overview

#### Authentication & Users

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | ❌ |
| POST | `/api/auth/login` | Login and get JWT tokens | ❌ |
| POST | `/api/auth/logout` | Logout and blacklist token | ✅ |
| GET | `/api/users/me` | Get current user profile | ✅ |
| PATCH | `/api/users/me` | Update user profile | ✅ |
| GET | `/api/admin/users` | List all users (admin only) | ✅ Admin |

#### Services

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/services` | List all active services | ❌ |
| GET | `/api/services/{id}` | Get service details | ❌ |
| POST | `/api/services` | Create new service | ✅ Admin |
| PATCH | `/api/services/{id}` | Update service | ✅ Admin |
| DELETE | `/api/services/{id}` | Delete service | ✅ Admin |

#### Bookings

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/bookings` | Create new booking | ✅ |
| GET | `/api/bookings` | Get user's bookings | ✅ |
| GET | `/api/bookings/{id}` | Get booking details | ✅ |
| PATCH | `/api/bookings/{id}` | Update booking | ✅ |
| DELETE | `/api/bookings/{id}` | Cancel booking | ✅ |
| GET | `/api/admin/bookings` | List all bookings | ✅ Admin |

#### Reviews

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/reviews` | Create review | ✅ |
| GET | `/api/services/{id}/reviews` | Get service reviews | ❌ |
| GET | `/api/reviews/{id}` | Get review details | ❌ |
| PATCH | `/api/reviews/{id}` | Update review | ✅ |
| DELETE | `/api/reviews/{id}` | Delete review | ✅ |
| GET | `/api/services/{id}/reviews/stats` | Review statistics | ❌ |

### Request/Response Examples

#### Register User

```bash
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "status": "active",
  "created_at": "2025-10-24T10:00:00Z"
}
```

#### Login

```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Create Booking

```bash
POST /api/bookings
Authorization: Bearer <token>
Content-Type: application/json

{
  "service_id": "550e8400-e29b-41d4-a716-446655440001",
  "start_time": "2025-10-28T14:00:00Z"
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "service_id": "550e8400-e29b-41d4-a716-446655440001",
  "start_time": "2025-10-28T14:00:00Z",
  "end_time": "2025-10-28T20:00:00Z",
  "status": "pending",
  "created_at": "2025-10-24T10:05:00Z"
}
```

#### Create Review

```bash
POST /api/reviews
Authorization: Bearer <token>
Content-Type: application/json

{
  "booking_id": "550e8400-e29b-41d4-a716-446655440002",
  "rating": 5,
  "comment": "Excellent service! Highly recommended."
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "booking_id": "550e8400-e29b-41d4-a716-446655440002",
  "rating": 5,
  "comment": "Excellent service! Highly recommended.",
  "created_at": "2025-10-30T10:00:00Z"
}
```

### Test Credentials (Production)

**Admin Account**:
```json
{
  "email": "titilola@example.com",
  "password": "stringst"
}
```

**Regular User**:
```json
{
  "email": "titi@example.com",
  "password": "stringst"
}
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    User     │────────>│   Booking    │<────────│   Service   │
│             │  1:N    │              │   N:1   │             │
│ - id (UUID) │         │ - id (UUID)  │         │ - id (UUID) │
│ - name      │         │ - user_id    │         │ - title     │
│ - email     │         │ - service_id │         │ - price     │
│ - role      │         │ - start_time │         │ - duration  │
└─────────────┘         │ - end_time   │         └─────────────┘
                        │ - status     │
                        └──────────────┘
                               │
                               │ 1:1
                               ▼
                        ┌──────────────┐
                        │    Review    │
                        │              │
                        │ - id (UUID)  │
                        │ - booking_id │
                        │ - rating     │
                        │ - comment    │
                        └──────────────┘
```

### Key Models

#### User Model
```python
- id: UUID (Primary Key)
- name: String(100)
- email: String(255) (Unique)
- password_hash: String
- role: Enum(user, admin)
- is_active: Boolean
- status: Enum(active, inactive)
- created_at: DateTime
```

#### Service Model
```python
- id: UUID (Primary Key)
- title: String(200)
- description: Text
- price: Decimal(10, 2)
- duration_minutes: Integer
- is_active: Boolean
- owner_id: UUID (Foreign Key → User)
- created_at: DateTime
```

#### Booking Model
```python
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key → User)
- service_id: UUID (Foreign Key → Service)
- start_time: DateTime
- end_time: DateTime
- status: Enum(pending, confirmed, cancelled, completed)
- created_at: DateTime
```

#### Review Model
```python
- id: UUID (Primary Key)
- booking_id: UUID (Foreign Key → Booking, Unique)
- rating: Integer (1-5)
- comment: Text
- created_at: DateTime
```

### Database Constraints

- **Foreign Keys**: All relationships enforced with CASCADE delete
- **Check Constraints**: 
  - Rating between 1-5
  - Valid status values
  - Price ≥ 0
  - Duration > 0
- **Unique Constraints**:
  - User email
  - One review per booking
- **Indexes**: On frequently queried fields (email, status, timestamps)

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage report
pytest --cov=. --cov-report=html --cov-report=term

# Run in verbose mode
pytest -v

# Run specific test
pytest tests/test_bookings.py::test_create_booking_success
```

### Test Coverage

The project includes 30+ comprehensive tests covering:

| Test Suite | Coverage |
|------------|----------|
| **Authentication** | Registration, login, logout, token refresh, permissions |
| **User Management** | Profile operations, admin user management |
| **Services** | CRUD operations, filtering, admin authorization |
| **Bookings** | Creation, conflict detection, status transitions, cancellation |
| **Reviews** | Creation, validation, ownership, statistics |
| **Edge Cases** | Invalid inputs, authorization failures, boundary conditions |

### Test Results

```bash
======================== test session starts =========================
collected 32 items

tests/test_auth.py ..................                         [ 56%]
tests/test_bookings.py .........                             [ 84%]
tests/test_services.py .....                                 [ 100%]

======================== 32 passed in 5.23s ==========================

---------- coverage: platform linux, python 3.13.0 -----------
Name                          Stmts   Miss  Cover
-------------------------------------------------
crud/booking.py                  45      2    96%
crud/review.py                   32      1    97%
crud/service.py                  38      0   100%
crud/user.py                     42      1    98%
models/booking.py                15      0   100%
models/review.py                 12      0   100%
models/service.py                14      0   100%
models/user.py                   18      0   100%
routers/booking.py               67      3    96%
routers/review.py                54      2    96%
routers/service.py               48      1    98%
routers/user.py                  58      2    97%
-------------------------------------------------
TOTAL                           443      12    97%
```

---

## Deployment

### Environment Configuration

Create a `.env` file with the following variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/bookit

# Security
SECRET_KEY=your-secure-random-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Account
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=SecureAdminPassword123!

# Application
ENVIRONMENT=production
DEBUG=False

# CORS (if needed for frontend)
CORS_ORIGINS=["https://yourdomain.com"]
```

### Production Deployment 

#### 1. Prerequisites

- PipeOps account
- GitHub repository
- PostgreSQL database provisioned

#### 2. Database Setup

```bash
# On Render, create PostgreSQL database
# Note the connection string
```

#### 3. Deploy Application

**Build Command**:
```bash
pip install -r requirements.txt
```

**Start Command**:
```bash
alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
```

**Environment Variables**: Set all variables from `.env` in PipeOps dashboard

#### 4. Post-Deployment

```bash
# Verify deployment
curl https://bookit-api.pipeops.com/health

# Test API
curl https://bookit-api.pipeops.com/docs
```

### Production Checklist

- [ ] PostgreSQL database created and migrated
- [ ] Environment variables configured
- [ ] SECRET_KEY is strong and unique
- [ ] ADMIN_PASSWORD changed from default
- [ ] CORS configured for your domain
- [ ] HTTPS enabled (automatic on PipeOps)
- [ ] Health check endpoint responding
- [ ] Logs are accessible
- [ ] Monitoring configured

---

## Security

### Authentication & Authorization

- **JWT Tokens**: Stateless authentication with access and refresh tokens
- **Token Blacklisting**: Secure logout with Redis-backed blacklist
- **Password Hashing**: bcrypt with 12 rounds (industry standard)
- **Role-Based Access**: Granular permissions for users and administrators

### Data Protection

- **Input Validation**: All inputs validated with Pydantic schemas
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
- **UUID Primary Keys**: UUIDs instead of sequential IDs enhance security
- **HTTPS Enforcement**: All production traffic encrypted

### Business Logic Security

| Security Control | Implementation |
|------------------|----------------|
| **Ownership Verification** | Users can only access their own resources |
| **Review Authorization** | Only booking creators can leave reviews |
| **Time Validation** | Bookings must be in the future |
| **Status Validation** | Proper state machine for booking transitions |
| **Admin Checks** | Sensitive operations require admin role |

---

## API Response Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., duplicate booking time) |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

---

## Contributing

Contributions are welcome! Please follow these guidelines:

### Development Workflow

1. **Fork the repository**
```bash
git clone https://github.com/Titilola-py/bookit-api.git
cd bookit-api
```

2. **Create a feature branch**
```bash
git checkout -b feature/amazing-feature
```

3. **Make your changes**
```bash
# Write code and tests
# Ensure all tests pass
pytest -v
```

4. **Commit your changes**
```bash
git commit -m 'feat: Add amazing feature'
```

5. **Push to your fork**
```bash
git push origin feature/amazing-feature
```

6. **Open a Pull Request**

### Coding Standards

- Follow **PEP 8** style guidelines
- Write **tests** for new features
- Update **documentation** for API changes
- Use **meaningful commit messages** (Conventional Commits)
- Add **type hints** to all functions
- Ensure **test coverage** doesn't decrease

### Commit Message Format

```
type(scope): subject

body

footer
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Example**:
```
feat(booking): Add conflict detection for overlapping bookings

Implemented algorithm to check for booking time conflicts
before creating new bookings. Returns 409 Conflict status
when overlap is detected.

Closes #123
```

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Guide](https://docs.sqlalchemy.org/en/20/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [JWT.io](https://jwt.io/) - JWT debugger
- [pytest Documentation](https://docs.pytest.org/)

---

## Author

**Fatimah Olaitan**

- **GitHub**: [@Titilola-py](https://github.com/Titilola-py)
- **Email**: olaitantitilola2@gmail.com
- **LinkedIn**: [Connect with me](https://www.linkedin.com/in/fatimah-olaitan-4bb6602a4/)

---

## License

This project is licensed under the **MIT License** 

---

## Acknowledgments

- **AltSchool Africa** - Backend Engineering Program
- **FastAPI Community** - Excellent framework and documentation
- **SQLAlchemy Team** - Powerful and flexible ORM
- **Pydantic Team** - Robust data validation library
- **Python Community** - Amazing ecosystem and libraries

---

## Support

For questions, issues, or suggestions:

- **Email**: olaitantitilola2@gmail.com
- **GitHub Issues**: [Report a bug](https://github.com/Titilola-py/bookit-api/issues)
- **Documentation**: https://bookit-api.pipeops.com/docs

---

<div align="center">

**BookIt API** - Professional booking platform REST API

Built with ❤️ using FastAPI, SQLAlchemy, and PostgreSQL

⭐ Star this repo if you find it helpful!

</div>