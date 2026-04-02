from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from server.core.database import Base


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[int] = mapped_column(primary_key=True)
    app_name: Mapped[str] = mapped_column(String(100), index=True)
    version: Mapped[str] = mapped_column(String(50))
    env: Mapped[str] = mapped_column(String(50), default="production")
    cloud: Mapped[str] = mapped_column(String(50), default="docker")
    status: Mapped[str] = mapped_column(String(20), default="running")
    port: Mapped[int] = mapped_column(Integer, default=8000)
    image: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
