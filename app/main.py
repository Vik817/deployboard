"""DeployBoard API — Phase 1 skeleton.

Endpoints in this chunk:
- GET  /healthz            -> liveness check
- POST /services          -> register a service
- GET  /services          -> list services

Run locally:
    pip install -r requirements.txt
    uvicorn app.main:app --reload
Then open http://127.0.0.1:8000/docs for the auto-generated API docs.
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import Base, engine, get_db
from . import models, schemas
from .deploys import run_deployment

# DEV-ONLY shortcut: auto-create tables on startup. This is fine for the v1
# skeleton but is NOT how schema should be managed in production — it can't
# handle schema changes safely (drift / data loss). TODO(next phase): replace
# with migrations (Alembic — the SQLAlchemy equivalent of Liquibase).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DeployBoard", version="0.1.0")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/services", response_model=schemas.ServiceRead, status_code=201)
def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    db_service = models.Service(
        name=service.name,
        deploy_command=service.deploy_command,
        target=service.target,
    )
    db.add(db_service)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Service name already exists")
    db.refresh(db_service)
    return db_service


@app.get("/services", response_model=list[schemas.ServiceRead])
def list_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()


# ---- Deployments ----

@app.post(
    "/services/{service_id}/deployments",
    response_model=schemas.DeploymentRead,
    status_code=201,
)
def trigger_deployment(
    service_id: int,
    background_tasks: BackgroundTasks,
    body: schemas.DeploymentCreate | None = None,
    db: Session = Depends(get_db),
):
    """Trigger a deploy for a service.

    Returns immediately (201) with a RUNNING deployment; the command runs in a
    background task so the client isn't blocked. Poll the GET endpoints for the
    final status + logs.
    """
    service = db.get(models.Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    deployment = models.Deployment(
        service_id=service.id,
        status=models.DeploymentStatus.RUNNING,
        commit_ref=body.commit_ref if body else None,
    )
    db.add(deployment)
    db.commit()
    db.refresh(deployment)

    # Run after the response is sent. Pass the command now so the background
    # task doesn't need to re-read the service.
    background_tasks.add_task(run_deployment, deployment.id, service.deploy_command)

    return deployment


@app.get(
    "/services/{service_id}/deployments",
    response_model=list[schemas.DeploymentRead],
)
def list_deployments(service_id: int, db: Session = Depends(get_db)):
    service = db.get(models.Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return (
        db.query(models.Deployment)
        .filter(models.Deployment.service_id == service_id)
        .order_by(models.Deployment.started_at.desc())
        .all()
    )


@app.get("/deployments/{deployment_id}", response_model=schemas.DeploymentRead)
def get_deployment(deployment_id: int, db: Session = Depends(get_db)):
    """Poll this for a single deployment's status + logs."""
    deployment = db.get(models.Deployment, deployment_id)
    if deployment is None:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment