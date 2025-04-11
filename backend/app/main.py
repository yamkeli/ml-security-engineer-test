from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.api import api_router 
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:8080",
    "http://localhost:3000",
]

app = FastAPI(root_path='/api')

# CORS (example setup)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["local"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Main API
app.include_router(api_router, prefix="/v1")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    
    yield
    # on shutdown

@app.get('/health', status_code=200)
def health_check():
    return {"status": "ok"}
