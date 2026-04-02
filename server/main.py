from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.core.database import create_tables
from server.routers import auth, deployments


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="CloudDeploy API",
    description="Control plane for the CloudDeploy CLI",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(deployments.router)


@app.get("/")
async def root():
    return {"service": "CloudDeploy API", "version": "0.2.0", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}
