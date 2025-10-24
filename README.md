# BookIT API

BookIT API is a backend system built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy** for managing a simple booking platform.
It supports user authentication, admin control, service management, and booking operations.

---

## Overview

BookIT provides an efficient system for users to:

* Register and authenticate using JWT tokens
* Browse available services (e.g., babysitting, cleaning, tutoring)
* Make, update, or cancel bookings
* Leave and view reviews
* Allow admins to manage users, services, and bookings

Why PostgreSQL?

Chosen Database: PostgreSQL

BookIT uses PostgreSQL instead of MongoDB because the project handles structured and relational data — like users, bookings, and services that depend on foreign keys and transactions. PostgreSQL ensures accuracy, supports complex joins, and maintains data integrity.
MongoDB works well for unstructured data or flexible schemas, but BookIT’s use case requires strong relationships and consistency, making PostgreSQL the better fit.

---

## Tech Stack

| Component         | Technology            |
| ----------------- | --------------------- |
| Backend Framework | FastAPI               |
| ORM               | SQLAlchemy            |
| Database          | PostgreSQL            |
| Authentication    | JWT (JSON Web Tokens) |
| Migrations        | Alembic               |
| Deployment        | Render                |

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/BookIT-API.git
cd BookIT-API
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` File

Example:

```
DATABASE_URL=postgresql+psycopg2://postgres:yourpassword@localhost:5432/bookit_db
SECRET_KEY=3e7cdd85b9d44af9b0e24d8d1a63c4fdc7f7dc123456789abcdef
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

ENVIRONMENT=development
DEBUG=True
```

### 5. Initialize Database

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 6. Run the Server

```bash
uvicorn main:app --reload
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API documentation.

---

## Example Data for Testing

### Babysitting Service

```json
{
  "title": "Babysitting",
  "description": "Professional babysitting service for children aged 2 to 10 years.",
  "price": 45.50,
  "duration_minutes": 180
}
```

### Cleaning Service

```json
{
  "title": "Home Cleaning",
  "description": "Comprehensive home cleaning service with eco-friendly supplies.",
  "price": 99.99,
  "duration_minutes": 120
}
```

### Tutoring Service

```json
{
  "title": "Math Tutoring",
  "description": "Private math tutoring sessions for secondary school students.",
  "price": 60.00,
  "duration_minutes": 90
}
```

---

## Deployment on Render

### 1. Push Code to GitHub

```bash
git add .
git commit -m "Deploy-ready version"
git push origin main
```

### 2. Create a Web Service on Render

* Go to [Render Dashboard](https://render.com/)
* Click **New → Web Service**
* Connect your GitHub repository and select this project

### 3. Configure the Build and Start Commands

| Setting       | Value                                                                  |
| ------------- | ---------------------------------------------------------------------- |
| Environment   | Python                                                                 |
| Build Command | `pip install -r requirements.txt`                                      |
| Start Command | `alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Branch        | main                                                                   |

Ensure `main.py` has the following to handle Render’s dynamic port:

```python
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
```

### 4. Add Environment Variables on Render

Go to your Render service → Environment tab → Add the following:

```
DATABASE_URL=postgresql+psycopg2://<user>:<password>@<hostname>:5432/<db_name>
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=production
DEBUG=False
```

### 5. Add PostgreSQL Database

* On Render, create a **PostgreSQL** instance
* Copy the **Internal Database URL**
* Paste it into your `DATABASE_URL` environment variable

### 6. Deploy and Test

Render will automatically build and deploy your app.
After deployment, access your live docs at:

```
https://bookit-api.onrender.com/docs
```

---

## Developer Notes

* Run migrations: `alembic revision --autogenerate -m "msg" && alembic upgrade head`
* Check logs on Render for debugging
* Test locally before pushing updates

---

## Author

**Fatimah Olaitan**
Backend Engineer | AltSchool Africa Diploma in Backend Engineering (2025)

---
