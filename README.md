🚀 Flask Task Management API
A professional-grade Task Management REST API built with Flask, PostgreSQL, and Docker. This project demonstrates a complete development lifecycle, from basic CRUD operations to advanced security and documentation.

🛠 Key Features
Authentication: Secure user registration and login using JWT (JSON Web Tokens) and Werkzeug password hashing.

Database: Fully relational schema using PostgreSQL with UUIDs for enhanced security and scalability.

Search & Pagination: Case-insensitive search and server-side pagination for optimized data retrieval.

Infrastructure: Fully containerized database using Docker Compose.

Documentation: Interactive API documentation via Swagger (OpenAPI).

🏗 Project Architecture
The system is designed using the Application Factory Pattern for modularity:

app/models/: Database schemas (User, Task).

app/routes/: Blueprint-based API endpoints.

app/extensions.py: Centralized extension management (DB, JWT, Swagger).

migrations/: Database version control.

🚀 Getting Started
1. Prerequisites
Python 3.10+

Docker & Docker Desktop

Virtual Environment (venv)

2. Installation
PowerShell
# Clone the repository
git clone <your-repo-link>
cd flask-task-api

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
3. Database Setup (Docker)
PowerShell
# Start the PostgreSQL container
docker-compose up -d

# Initialize the database
flask db upgrade
4. Running the App
PowerShell
python run.py
📖 API Documentation
Once the server is running, you can access the Interactive Swagger UI at:
👉 http://localhost:5000/apidocs/

This dashboard allows you to:

Register a new user.

Login to receive a JWT.

Authorize the dashboard using that token.

Test Task creation, searching, and pagination.

🛣 Development Phases
Phase 1: Core Flask setup & Blueprints.

Phase 2: Database migrations & PostgreSQL integration.

Phase 3: JWT Authentication & User-Task relationships.

Phase 4: Advanced query logic (Search/Pagination).

Phase 5: Swagger Documentation & Infrastructure cleanup.