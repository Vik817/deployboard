# DeployBoard

A small, self-hostable deployment dashboard. Point it at your services, trigger deploys, and watch what happened — without wiring up a heavyweight CI/CD platform.

## Why this exists

DeployBoard is a learning-driven project with a real product core: a single place to see your deployments, kick one off, and read the logs when something breaks. It's deliberately small so it can be finished, and deliberately full-stack so building it exercises backend, frontend, containers, IaC, Kubernetes, CI/CD, and observability end to end.

## Spec (one paragraph)

DeployBoard is a self-hostable web app that shows a list of deployments for the services you register, lets you trigger a new deployment of a service (by running a defined deploy command against a target), and streams/stores the logs from each deploy so you can see what happened and why it failed. It is single-tenant and self-hosted: you run it next to the infrastructure it deploys to.

## v1 — three core features (and nothing else)

1. **View deployments** — a list of past and in-progress deployments per service, each with status (pending / running / success / failed), timestamps, and which commit/target it ran against.
2. **Trigger a deploy** — start a new deployment for a registered service. v1 definition: run a *defined deploy command* against a target and record the outcome. Not a full orchestration engine — that's later.
3. **View logs** — capture and display the output (stdout/stderr) of each deployment, viewable per-deployment.

### Explicitly out of scope for v1 (parking lot)

Keeping these here so they stop nagging without expanding the build:

- Rollback / redeploy-previous
- Multi-user / auth beyond a single admin
- Repo integration (webhooks, auto-deploy on push)
- Multiple environments (staging/prod) as first-class objects
- Real-time log streaming over websockets (v1 can poll)
- Notifications (Slack/email)
- Metrics dashboards

## Stack

- **Backend:** Python + FastAPI (async, typed, auto OpenAPI docs)
- **DB:** PostgreSQL (via SQLAlchemy)
- **Frontend:** minimal — talks to the API (framework TBD in Phase 1; keep it light)
- **Later phases:** Docker + docker-compose → Terraform → Kubernetes → CI/CD → observability

## Project phases

Tracked in full in the Career Tracker (Side Project track). Short version:

- **Phase 0 — Shape it** ← *you are here*
- **Phase 1 — Build the app** (API + DB, minimal frontend, one useful feature end-to-end)
- **Phase 2 — Cloud-native** (Dockerize, docker-compose, Terraform, deploy to K8s)
- **Phase 3 — Productionize** (CI/CD, metrics + logging + Grafana, blog post)
- **Phase 4 — Share it** (open-source, post it, decide: portfolio piece or startup seed)

## Status

Phase 0. Spec written, stack chosen, repo initialized. Next: model the `Deployment` and `Service` data, stand up the FastAPI skeleton with a health check.
