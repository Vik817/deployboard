"""SQLAlchemy ORM models for DeployBoard.

Two tables for v1:
- Service: a thing you can deploy (has a name, a deploy command, a target)
- Deployment: one run of a service's deploy command (status, timing, logs)

A Service has many Deployments (one-to-many).
"""
import datetime
import enum

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped

from .database import Base


class DeploymentStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    # The command DeployBoard runs to deploy this service (v1: a defined command).
    deploy_command: Mapped[str] = mapped_column(String(500), nullable=False)
    # Where it deploys to (free-form for v1: a host, a label, etc.)
    target: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.UTC)
    )

    deployments: Mapped[list["Deployment"]] = relationship(
        back_populates="service", cascade="all, delete-orphan"
    )


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    status: Mapped[DeploymentStatus] = mapped_column(
        Enum(DeploymentStatus), default=DeploymentStatus.PENDING, nullable=False
    )
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    logs: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Which version of the code this deployment shipped (git SHA, tag, etc.).
    # Nullable: not every deploy target has a commit ref. Useful later for
    # answering "what's actually running?" — part of the Phase 0 spec.
    commit_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    started_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.UTC)
    )
    finished_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    service: Mapped["Service"] = relationship(back_populates="deployments")