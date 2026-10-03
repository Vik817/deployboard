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
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import Base, engine, get_db
from . import models, schemas

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
