from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from server.core.database import get_db
from server.core.auth import hash_password, verify_password, create_access_token
from server.models.user import User, Role
import secrets

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.developer


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class ApiKeyResponse(BaseModel):
    api_key: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        role=body.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"message": "User created", "email": user.email, "role": user.role}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, role=user.role)


@router.post("/api-key", response_model=ApiKeyResponse)
async def generate_api_key(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(__import__('server.core.auth', fromlist=['get_current_user']).get_current_user),
):
    api_key = secrets.token_hex(32)
    current_user.api_key = api_key
    await db.commit()
    return ApiKeyResponse(api_key=api_key)
