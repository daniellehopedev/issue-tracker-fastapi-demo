# Issue Tracker API

A small, production-style REST API for managing issues, built with [FastAPI](https://fastapi.tiangolo.com/) and [Pydantic](https://docs.pydantic.dev/). Issues are persisted to a local JSON file, making this a lightweight demo that still follows common API patterns: request validation, structured routing, middleware, and OpenAPI documentation.

## Features

- Full CRUD for issues (create, read, update, delete)
- Pydantic schemas with field validation and enum constraints
- JSON file persistence (no database required)
- Request timing middleware (`X-Process-Time` response header)
- CORS enabled for frontend integration
- Auto-generated interactive API docs at `/docs`

## Architecture

The app follows a simple layered structure:

```
Request → Middleware → Router → Schema validation → Storage → JSON file
```

| Layer                              | Responsibility                                                                            |
| ---------------------------------- | ----------------------------------------------------------------------------------------- |
| **Entry point** (`main.py`)        | Creates the FastAPI app, registers middleware, mounts routers, and exposes a health check |
| **Routes** (`app/routes/`)         | HTTP handlers — parse requests, call storage, return responses                            |
| **Schemas** (`app/schemas.py`)     | Pydantic models for request/response validation and serialization                         |
| **Storage** (`app/storage.py`)     | Read/write issues to `data/issues.json`                                                   |
| **Middleware** (`app/middleware/`) | Cross-cutting concerns (e.g. request timing)                                              |

### Request flow

1. A client sends an HTTP request to an endpoint (e.g. `POST /api/v1/issues`).
2. Middleware runs first (timing starts, CORS headers applied).
3. FastAPI validates the request body against a Pydantic schema (`IssueCreate`, `IssueUpdate`, etc.).
4. The route handler loads issues from disk, performs the operation, and saves back to disk.
5. The response is serialized through `IssueOut` and returned with an `X-Process-Time` header.

## File structure

```
issue-tracker-fastapi-demo/
├── main.py                  # FastAPI app entry point
├── requirements.txt         # Python dependencies
├── README.md
├── app/
│   ├── __init__.py
│   ├── schemas.py           # Pydantic models and enums
│   ├── storage.py           # JSON file persistence
│   ├── middleware/
│   │   └── timing.py        # Adds X-Process-Time header to responses
│   └── routes/
│       ├── __init__.py
│       └── issues.py        # Issue CRUD endpoints
└── data/
    └── issues.json          # Issue storage (gitignored)
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
```

### Run the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

- **Interactive docs:** http://127.0.0.1:8000/docs
- **Health check:** http://127.0.0.1:8000/health

## API endpoints

| Method   | Path                        | Description               |
| -------- | --------------------------- | ------------------------- |
| `GET`    | `/health`                   | Health check              |
| `GET`    | `/api/v1/issues`            | List all issues           |
| `GET`    | `/api/v1/issues/{issue_id}` | Get a single issue        |
| `POST`   | `/api/v1/issues`            | Create a new issue        |
| `PUT`    | `/api/v1/issues/{issue_id}` | Update an issue (partial) |
| `DELETE` | `/api/v1/issues/{issue_id}` | Delete an issue           |

### Data model

An issue has the following fields:

| Field         | Type     | Notes                                             |
| ------------- | -------- | ------------------------------------------------- |
| `id`          | `string` | UUID, generated on create                         |
| `title`       | `string` | 3–100 characters                                  |
| `description` | `string` | 5–2000 characters                                 |
| `priority`    | `enum`   | `low`, `medium`, `high` (default: `medium`)       |
| `status`      | `enum`   | `open`, `in_progress`, `closed` (default: `open`) |

### Example: create an issue

```bash
curl -X POST http://127.0.0.1:8000/api/v1/issues \
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
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

Invalid enum values (e.g. `"status": "test"`) return a `422 Unprocessable Entity` validation error.

## Persistence

Issues are stored in `data/issues.json`. The `data/` directory is gitignored, so each environment maintains its own local data. The storage layer creates the file and directory automatically on first write.

## Tech stack

- **FastAPI** — web framework and routing
- **Pydantic** — data validation and settings
- **Uvicorn** — ASGI server
- **Starlette** — underlying ASGI toolkit (CORS, middleware)

## TO-DO

- **Auth**
- **Persistent Storage/Real Database**
- **User Registration**
- **env variables for Auth**
