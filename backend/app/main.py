from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.secrets.secrets_manager import get_db_secrets
from app.core.db.database_manager import DatabaseManager

from app.logging_config import setup_logging
import logging

from app.utils.utils import get_ip

setup_logging()
logger = logging.getLogger(__name__)


def get_db_manager() -> DatabaseManager:
    try:
        return DatabaseManager.get_instance()
    except:
        # get database secrets
        db_config = get_db_secrets()

        DB_NAME = db_config.get("db")
        DB_USER = db_config.get("username")
        DB_PASS = db_config.get("password")
        DB_ENDPOINT = db_config.get("host")
        DB_PORT = db_config.get("port")

        return DatabaseManager.get_instance(
            host=DB_ENDPOINT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            port=DB_PORT,
        )


origins = ["http://localhost:8080", "http://localhost:3000", "http://localhost"]

app = FastAPI(root_path="/api", redoc_url=None, docs_url=None)

# CORS (example setup)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
def health_check(request: Request):
    print(get_ip(request))
    return {"status": "ok"}
