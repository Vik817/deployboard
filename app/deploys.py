"""Deployment runner: executes a service's deploy_command and records the result.

SECURITY — trust boundary (read before changing):
    We run deploy_command with shell=True. That is SAFE here ONLY because
    deploy_command is TRUSTED admin-authored config — it's set by whoever
    registers the service (you), not by untrusted end-user request data.
    shell=True lets deploy commands use shell features (&&, |, env vars),
    which real deploys need.

    *** If a future version ever lets end users submit or influence
    deploy_command, shell=True becomes a remote-code-execution (command
    injection) vector. At that point switch to shell=False with an argument
    list, or strictly validate/escape the input. Do NOT remove this comment. ***
"""
import datetime
import subprocess

from sqlalchemy.orm import Session

from . import models
from .database import SessionLocal

# A deploy that runs longer than this is treated as failed, so a hung command
# can't leave a deployment stuck in "running" forever.
DEPLOY_TIMEOUT_SECONDS = 300


def run_deployment(deployment_id: int, command: str) -> None:
    """Run `command`, capture output + exit code, update the Deployment row.

    Intended to run as a background task AFTER the HTTP response is sent, so the
    client isn't blocked while a deploy (which can take minutes) runs. Because
    it runs in the background, it opens its OWN DB session — the request's
    session is already closed by the time this executes.
    """
    db: Session = SessionLocal()
    try:
        deployment = db.get(models.Deployment, deployment_id)
        if deployment is None:
            return  # row vanished (deleted?) — nothing to do

        deployment.status = models.DeploymentStatus.RUNNING
        db.commit()

        try:
            result = subprocess.run(
                command,
                shell=True,              # SAFE: trusted admin input only (see module docstring)
                capture_output=True,
                text=True,
                timeout=DEPLOY_TIMEOUT_SECONDS,
            )
            deployment.exit_code = result.returncode
            deployment.status = (
                models.DeploymentStatus.SUCCESS
                if result.returncode == 0          # 0 = success (Unix convention)
                else models.DeploymentStatus.FAILED
            )
            deployment.logs = _format_logs(result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            deployment.status = models.DeploymentStatus.FAILED
            deployment.exit_code = None
            deployment.logs = f"Deployment timed out after {DEPLOY_TIMEOUT_SECONDS}s."
        except Exception as exc:  # noqa: BLE001 — record any unexpected failure rather than crash the worker
            deployment.status = models.DeploymentStatus.FAILED
            deployment.exit_code = None
            deployment.logs = f"Deployment run failed to start: {exc!r}"

        deployment.finished_at = datetime.datetime.now(datetime.UTC)
        db.commit()
    finally:
        db.close()


def _format_logs(stdout: str, stderr: str) -> str:
    """Store stdout and stderr together in one field, clearly delimited, so a
    failed deploy's error output is readable alongside its normal output."""
    return f"--- STDOUT ---\n{stdout or ''}\n--- STDERR ---\n{stderr or ''}"