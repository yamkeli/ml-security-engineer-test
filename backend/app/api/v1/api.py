from fastapi import APIRouter
from app.api.v1.subrouters.auth import auth_router

v1_api_router = APIRouter()

v1_api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
