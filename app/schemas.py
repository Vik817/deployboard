"""Pydantic schemas: the shapes that cross the API boundary.

Separating these from the ORM models is deliberate — the DB model is the
internal representation; these control what the API accepts and returns.
"""
import datetime

from pydantic import BaseModel, ConfigDict

from .models import DeploymentStatus


# ---- Service ----

class ServiceCreate(BaseModel):
    """What a client sends to register a service."""
    name: str
    deploy_command: str
    target: str


class ServiceRead(BaseModel):
    """What the API returns for a service."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    deploy_command: str
    target: str
    created_at: datetime.datetime


# ---- Deployment (read-only for this chunk; creation comes next chunk) ----

class DeploymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    status: DeploymentStatus
    exit_code: int | None
    commit_ref: str | None
    logs: str | None
    started_at: datetime.datetime
    finished_at: datetime.datetime | None


class DeploymentCreate(BaseModel):
    """Optional body when triggering a deploy. commit_ref records what shipped."""
    commit_ref: str | None = None