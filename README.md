# ChatNet

Welcome to **ChatNet** – a complete social media platform built using modern, scalable, and efficient technologies. This README provides an overview of the project, its features, and instructions to set it up locally or deploy it in production.

---

## **Features**

- **REST API with FastAPI**  
  High-performance, RESTful API built with Python's FastAPI framework.

- **Contextual-Based Search Engine**  
  Advanced search capabilities using vector embeddings for context-aware results.

- **Authentication & Security**  
  - OTP-based Two-Factor Authentication (2FA).  
  - Secure login with JWT (access and refresh tokens) and token rotation.  

- **Caching & Rate Limiting**  
  Optimized performance and controlled usage using **Redis**.

- **Testing**  
  Comprehensive test suite written in **pytest** to ensure code reliability.

- **CI/CD Pipeline**  
  Automated integration and deployment pipeline for seamless updates.

- **Dockerized Environment**  
  Fully containerized application for consistent and quick deployments.

---

## **Technologies Used**

- **Backend Framework**: FastAPI  
- **Database**: PostgreSQL  
- **Caching**: Redis  
- **Containerization**: Docker & Docker Compose  
- **Deployment**: CI/CD Pipeline (e.g., GitHub Actions)  
- **Search**: Vector-based embeddings for contextual search  
- **Testing**: Pytest  

---

## **Setup Instructions**

### Prerequisites

Ensure you have the following installed:
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL
- Redis

### Local Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/chatnet.git
   cd chatnet

## Set Up Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
DB = "postgresql"
DB_NAME = "your_db_name"
DB_USERNAME = "your_db_username"
DB_PASSWORD = "your_db_password"
DB_HOST = "localhost"
DB_PORT = 5432
TEST_DB_PORT = 5432
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = "0"
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 43200
OTP_EMAIL = "your_email@example.com"
OTP_PASSWORD = "your_email_password"
```


## Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Run Database Migrations

Apply the database migrations to set up your schema:

```bash
alembic upgrade head
```

## Start the Server

Run the server locally with the following command:

```bash
uvicorn app.main:app --reload
```

### Access the API Documentation

Open your browser and navigate to `http://127.0.0.1:8000/docs` to access the interactive API documentation.


# Dockerized Setup
## Build and Start the Containers

If you prefer a Dockerized setup, use the following command to build and start the containers:

```bash
docker-compose up --build
```

### Access the Application

Once the containers are running, the API will be available at `http://127.0.0.1:8000`.


# Testing

Run the test suite to validate the functionality:

```bash
pytest
```


# CI/CD Pipeline

1. The CI/CD pipeline automates the following tasks:

    Running tests with every commit.
    Building Docker images.
    Deploying updates to the production server.

2. Ensure you configure your CI/CD service (e.g., GitHub Actions) with the correct environment secrets.

# Roadmap

Here are some upcoming features and improvements:

    Add WebSocket support for real-time messaging.
    Implement machine learning models for feed recommendations.
    Support Kubernetes for orchestration and scaling.
    Extend search capabilities with Elasticsearch.

# Contributing

Contributions are welcome! Please follow these steps to contribute:

    Create a new branch for your feature or bugfix.
    Submit a pull request with a clear description of your changes.


For inquiries, feedback, or support, feel free to reach out at hamzaxd1123@gmail.com
Enjoy building with ChatNet! 🚀
