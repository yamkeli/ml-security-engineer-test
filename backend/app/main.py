from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.secrets.secrets_manager import get_db_secrets
from app.core.db.database_manager import DatabaseManager


def get_db_manager() -> DatabaseManager:
    # get database secrets
    db_config = get_db_secrets()

    DB_NAME = db_config.get("db")
    DB_USER = db_config.get("username")
    DB_PASS = db_config.get("password")
    DB_ENDPOINT = db_config.get("host")
    DB_PORT = db_config.get("port")

    return DatabaseManager.get_instance(
        host=DB_ENDPOINT, user=DB_USER, password=DB_PASS, database=DB_NAME, port=DB_PORT
    )


origins = [
    "http://localhost:8080",
    "http://localhost:3000",
]

app = FastAPI(root_path="/api")

# CORS (example setup)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["local"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1.api import v1_api_router

# Main API
app.include_router(v1_api_router, prefix="/v1")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup

    yield
    # on shutdown
    get_db_manager().close_pool()


@app.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}
