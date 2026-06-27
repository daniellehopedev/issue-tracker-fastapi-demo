# Issue Tracker API

A small, production-style REST API for managing issues, built with [FastAPI](https://fastapi.tiangolo.com/) and [Pydantic](https://docs.pydantic.dev/). Issues and users are persisted to local JSON files, making this a lightweight demo that still follows common API patterns: JWT authentication, request validation, structured routing, middleware, and OpenAPI documentation.

## Features

- JWT authentication (OAuth2 password flow)
- Protected issue endpoints (Bearer token required)
- Full CRUD for issues (create, read, update, delete)
- Pydantic schemas with field validation and enum constraints
- Environment-based config via `.env` (Pydantic Settings)
- JSON file persistence (no database required)
- Request timing middleware (`X-Process-Time` response header)
- CORS enabled for frontend integration
- Auto-generated interactive API docs at `/docs`

## Architecture

The app follows a simple layered structure:

```
Request → Middleware → Router → Auth → Schema validation → Storage → JSON file
```

| Layer | Responsibility |
|-------|----------------|
| **Entry point** (`main.py`) | Creates the FastAPI app, lifespan hooks, middleware, and mounts routers |
| **Routes** (`app/routes/`) | HTTP handlers for auth and issues |
| **Auth** (`app/auth.py`) | Password verification, JWT creation, and dependency guards |
| **Config** (`app/config.py`) | Settings loaded from environment variables |
| **Schemas** (`app/schemas.py`) | Pydantic models for request/response validation |
| **Storage** (`app/storage.py`) | Read/write issues and users from JSON files |
| **Middleware** (`app/middleware/`) | Cross-cutting concerns (e.g. request timing) |

### Request flow (protected endpoints)

1. Client obtains a JWT via `POST /api/v1/auth/token`.
2. Client sends requests with `Authorization: Bearer <token>`.
3. Middleware runs (timing, CORS).
4. FastAPI validates the token via `get_current_active_user`.
5. Request body is validated against Pydantic schemas where applicable.
6. The route handler loads data from disk, performs the operation, and saves back.
7. Response is returned with an `X-Process-Time` header.

## File structure

```
issue-tracker-fastapi-demo/
├── main.py                      # FastAPI app entry point
├── requirements.txt             # Python dependencies
├── README.md
├── .env                         # Local secrets (gitignored)
├── app/
│   ├── __init__.py
│   ├── config.py                # Settings from environment variables
│   ├── auth.py                  # JWT and password utilities
│   ├── schemas.py               # Pydantic models and enums
│   ├── storage.py               # JSON file persistence
│   ├── middleware/
│   │   └── timing.py            # Adds X-Process-Time header to responses
│   └── routes/
│       ├── __init__.py
│       ├── auth.py              # Login / token endpoint
│       └── issues.py            # Issue CRUD endpoints (protected)
└── data/
    ├── users.example.json       # Committed user template
    ├── users.json               # Local users (gitignored)
    └── issues.json              # Local issues (gitignored)
```

## Getting started

### Prerequisites

- Python 3.10+

### Setup

```bash
# Clone the repo and enter the project directory
cd issue-tracker-fastapi-demo

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create local config and data files
cp data/users.example.json data/users.json
```

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

On startup, the app warns if `data/users.json` is missing and points you to the example file.

### Run the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

- **Interactive docs:** http://127.0.0.1:8000/docs
- **Health check:** http://127.0.0.1:8000/health

## Authentication

Login uses the OAuth2 password flow. Send form data (not JSON) to the token endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=secret"
```

The default user is defined in `data/users.json` (copied from `data/users.example.json`). Use the response `access_token` on all issue endpoints:

```bash
curl http://127.0.0.1:8000/api/v1/issues \
  -H "Authorization: Bearer <access_token>"
```

In Swagger UI (`/docs`), click **Authorize**, enter `johndoe` / `secret`, then call protected endpoints.

## API endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | No | Health check |
| `POST` | `/api/v1/auth/token` | No | Obtain access token |
| `GET` | `/api/v1/issues` | Yes | List all issues |
| `GET` | `/api/v1/issues/{issue_id}` | Yes | Get a single issue |
| `POST` | `/api/v1/issues` | Yes | Create a new issue |
| `PUT` | `/api/v1/issues/{issue_id}` | Yes | Update an issue (partial) |
| `DELETE` | `/api/v1/issues/{issue_id}` | Yes | Delete an issue |

### Issue data model

| Field | Type | Notes |
|-------|------|-------|
| `id` | `string` | UUID, generated on create |
| `title` | `string` | 3–100 characters |
| `description` | `string` | 5–2000 characters |
| `priority` | `enum` | `low`, `medium`, `high` (default: `medium`) |
| `status` | `enum` | `open`, `in_progress`, `closed` (default: `open`) |

### Example: create an issue

```bash
curl -X POST http://127.0.0.1:8000/api/v1/issues \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix login bug",
    "description": "Users cannot log in with SSO",
    "priority": "high"
  }'
```

### Example: update an issue

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/issues/{issue_id} \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

Invalid enum values (e.g. `"status": "test"`) return a `422 Unprocessable Entity` validation error.

## Persistence

| File | Purpose | Git |
|------|---------|-----|
| `data/issues.json` | Issue storage | Ignored |
| `data/users.json` | User credentials (hashed passwords) | Ignored |
| `data/users.example.json` | Template for local user setup | Committed |

JSON files in `data/` are gitignored except `*.example.json` templates. The storage layer creates files and directories automatically on first write.

## Tech stack

- **FastAPI** — web framework and routing
- **Pydantic / pydantic-settings** — data validation and environment config
- **PyJWT** — JWT encoding and decoding
- **pwdlib** — password hashing (Argon2)
- **Uvicorn** — ASGI server
- **Starlette** — underlying ASGI toolkit (CORS, middleware)

## To-do

- Persistent storage / real database
- User registration
