# Helsa - AI Health Advisor

A backend application built with **FastAPI**, using OAuth2 authentication, 
modular architecture, and clean API design. The application and database run as containerized services.

Goal of the project is to help user gain insights from AI generated diagnoses based on provided symptom data and related images.

## Specifics

- **FastAPI** with async support
- **OAuth2 Password Flow** with JWT
- **Pydantic** models for validation
- **PostgreSQL** database
- **Docker** with docker-compose for containerized deployment
- Interactive API docs (Swagger & ReDoc)
- Modular route and service structure

## Requirements

- Docker

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/martinschne/helsa.git
cd helsa
```

### 2. Configure environment variables

## Add your own .env file to the project root
```env
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_api_key

POSTGRES_USER=your_db_username
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=your_db_name

BUILD_TARGET=dev

DB_PORT=5432
SERVER_PORT=8000
SERVER_DEBUG_PORT=5678
```

Set env variable `BUILD_TARGET` to `dev` when you want to enable debugging from VS Code. Set the value `prod` for production deployment.

`DB_PORT`, `SERVER_PORT` and `SERVER_DEBUG_PORT` are ports enabling `server` and `db` containers connect to the host. In the example the host ports are same as container ports, but feel free to change them if they are occupied on your machine.

### 3. Run server and database
```bash
docker compose up --build -d
```

### 3. Check the created containers
```bash
docker ps
```
You should see two containers with names `helsa-server` and `helsa-db` running.

Now you can use tools like **Postman** to send requests
to the running server. 
Server runs on: http://localhost:8000/

## API documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Disclaimer
The information provided here is for informational purposes only and is not intended to replace professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. No guarantees are made regarding the accuracy or completeness of the information provided, and reliance on any information obtained from this source is solely at your own risk.
