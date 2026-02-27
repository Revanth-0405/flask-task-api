# Flask Task Management API

A robust, scalable RESTful API built with Flask, demonstrating polyglot persistence using PostgreSQL for primary transactional data and AWS DynamoDB for high-speed activity logging.

---

## 🚀 Features

- **Polyglot Database Architecture:**  
  Uses PostgreSQL (via SQLAlchemy) for relational user and task data, and AWS DynamoDB (via Boto3) for scalable activity logging.

- **Secure Authentication:**  
  JWT-based authentication (`flask-jwt-extended`) protecting all task management routes.

- **Robust Data Validation:**  
  Request validation and serialization using Marshmallow.

- **Advanced Querying:**  
  Supports pagination, status filtering, and priority filtering.

- **Global Error Handling:**  
  Centralized exception handling ensuring consistent JSON error responses (400, 401, 404, 500).

- **Comprehensive Testing:**  
  Fully tested using `pytest` with mock integrations for external AWS services.

- **Docker Ready:**  
  Includes `docker-compose.yml` for easy provisioning of local database services.

---

## 🛠️ Tech Stack

- **Framework:** Python 3, Flask  
- **Primary Database:** PostgreSQL, SQLAlchemy, Alembic  
- **Secondary Database:** AWS DynamoDB, Boto3  
- **Authentication:** Flask-JWT-Extended  
- **Validation:** Marshmallow  
- **Testing:** Pytest, unittest.mock  
- **Containerization:** Docker  

---

## 📁 Project Structure

```
flask-task-api/
│
├── app/
│   ├── models/           # PostgreSQL database models
│   ├── routes/           # API endpoints and blueprints
│   ├── schemas/          # Marshmallow validation schemas
│   ├── services/         # Business logic and DynamoDB integration
│   ├── utils/            # Custom decorators and error handlers
│   ├── __init__.py       # Application factory
│   ├── config.py         # Configuration classes
│   └── extensions.py     # Flask extensions (db, jwt, etc.)
│
├── migrations/           # Alembic migrations
├── tests/                # Test suite
├── .env                  # Environment variables
├── .env.example         # Environment template
├── docker-compose.yml   # Docker services
├── README.md            # Documentation
├── requirements.txt     # Dependencies
└── run.py               # Application entry point
```

---

## ⚙️ Local Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/flask-task-api.git
cd flask-task-api
```

### 2. Create and activate virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Update `.env` with:

- PostgreSQL database URI  
- JWT secret key  
- AWS credentials  

---

### 5. Start Local Services (Optional)

```bash
docker-compose up -d
```

---

### 6. Initialize Database

```bash
flask db upgrade
```

---

### 7. Run the Application

```bash
python run.py
```

API runs at:

```
http://127.0.0.1:5000
```

---

## 🧪 Running Tests

Run full test suite:

```bash
python -m pytest
```

AWS services are mocked during testing.

---

## 📡 Core API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /api/auth/register | Register user | No |
| POST | /api/auth/login | Login and get JWT | No |

---

### Tasks

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /api/tasks | Create task | Yes |
| GET | /api/tasks | Get all tasks | Yes |
| GET | /api/tasks/<task_id> | Get specific task | Yes |
| PUT | /api/tasks/<task_id> | Update task | Yes |
| DELETE | /api/tasks/<task_id> | Soft delete task | Yes |

---

## ✅ Key Highlights

- Secure JWT authentication  
- PostgreSQL + DynamoDB integration  
- Clean architecture  
- Fully tested  
- Production-ready structure  

---