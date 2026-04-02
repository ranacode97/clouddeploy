from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from server.core.database import Base
import enum


class Role(str, enum.Enum):
    owner = "owner"
    developer = "developer"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(SAEnum(Role), default=Role.developer)
    api_key: Mapped[str | None] = mapped_column(String(64), unique=True, index=True, nullable=True)
