from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.timing import timing_middleware
from app.routes.auth import router as auth_router
from app.routes.issues import router as issues_router
from app.storage import USERS_EXAMPLE_FILE, USERS_FILE


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not USERS_FILE.exists():
        print(
            f"Warning: {USERS_FILE} not found. "
            f"Copy {USERS_EXAMPLE_FILE} to {USERS_FILE} to enable login."
        )
    yield


app = FastAPI(
    title="Issue Tracker API",
    version="0.1.0",
    description="A mini production-style API built with FastAPI",
    lifespan=lifespan,
)


app.middleware("http")(timing_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend's origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(issues_router)
