from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
from server.core.database import get_db
from server.core.auth import get_current_user, require_role
from server.models.user import User
from server.models.deployment import Deployment

router = APIRouter(prefix="/deployments", tags=["deployments"])


class DeploymentCreate(BaseModel):
    app_name: str
    version: str
    env: str = "production"
    cloud: str = "docker"
    port: int = 8000
    image: str
    notes: Optional[str] = None


class DeploymentOut(BaseModel):
    id: int
    app_name: str
    version: str
    env: str
    cloud: str
    status: str
    port: int
    image: str
    notes: Optional[str]
    user_id: int

    class Config:
        from_attributes = True


@router.post("/", response_model=DeploymentOut, status_code=201)
async def create_deployment(
    body: DeploymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("owner", "developer")),
):
    deployment = Deployment(**body.model_dump(), user_id=current_user.id)
    db.add(deployment)
    await db.commit()
    await db.refresh(deployment)
    return deployment


@router.get("/", response_model=list[DeploymentOut])
async def list_deployments(
    app_name: Optional[str] = None,
    env: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Deployment).order_by(desc(Deployment.created_at))
    if app_name:
        query = query.where(Deployment.app_name == app_name)
    if env:
        query = query.where(Deployment.env == env)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{deployment_id}", response_model=DeploymentOut)
async def get_deployment(
    deployment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Deployment).where(Deployment.id == deployment_id)
    )
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment


@router.patch("/{deployment_id}/status")
async def update_status(
    deployment_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("owner", "developer")),
):
    result = await db.execute(
        select(Deployment).where(Deployment.id == deployment_id)
    )
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    deployment.status = status
    await db.commit()
    return {"message": f"Status updated to {status}"}


@router.delete("/{deployment_id}", status_code=204)
async def delete_deployment(
    deployment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("owner")),
):
    result = await db.execute(
        select(Deployment).where(Deployment.id == deployment_id)
    )
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    await db.delete(deployment)
    await db.commit()
