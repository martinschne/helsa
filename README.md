## Helsa - AI Health Advisor MVP

A minimal MVP backend built with **FastAPI**, using OAuth2 authentication, 
modular architecture, and clean API design. 

Goal of the project is to help user gain insights from AI generated diagnoses based on provided symptom data and related images.

## Specifics

- **FastAPI** with async support
- **OAuth2 Password Flow** with JWT
- **Pydantic** models for validation
- **SQLite** support
- Interactive API docs (Swagger & ReDoc)
- Modular route and service structure

## Requirements

- Python 3.10+
- uv

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/martinschne/helsa.git
cd helsa
```
### 2. Install the dependencies
```bash
uv pip install -r pyproject.toml
```
### 3. Run the server locally
```bash
fastapi run app/main.py
```

Now you can use tools like **Postman** to send requests
to the running server. 
Local server runs on: http://localhost:8000/

## API documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc