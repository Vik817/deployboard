# DeployBoard — Issue Board (starter)

Copy these into GitHub Issues (or a Projects board) once the repo is up. Grouped by phase. Keep v1 ruthless — if a new idea shows up, it goes in the Parking Lot in the README, not into an open issue.

## Phase 0 — Shape it
- [ ] Initialize repo, add README, add MIT (or Apache-2.0) license
- [ ] Set up GitHub Projects board (or just Issues + labels: `phase-0`, `phase-1`, `backend`, `frontend`, `infra`)
- [ ] Write the spec + lock the 3 core features (done — in README)
- [ ] Choose frontend approach (keep minimal — decide in Phase 1)

## Phase 1 — Build the app
### Data & backend
- [ ] Model the domain: `Service` (name, deploy command, target) and `Deployment` (service, status, started_at, finished_at, exit_code, commit/target ref)
- [ ] Stand up FastAPI skeleton with `/healthz`
- [ ] Wire up Postgres + SQLAlchemy + a migration tool (Alembic)
- [ ] `POST /services` and `GET /services` — register and list services
- [ ] `GET /services/{id}/deployments` — list deployments (Feature 1)
- [ ] `POST /services/{id}/deployments` — trigger a deploy: run the defined command, capture exit code (Feature 2)
- [ ] Capture stdout/stderr from the deploy command, store it, expose `GET /deployments/{id}/logs` (Feature 3)
- [ ] Run the deploy command as a background task so the API doesn't block

### Frontend (minimal)
- [ ] Deployments list view (status badges, timestamps)
- [ ] Trigger-deploy button per service
- [ ] Log viewer per deployment (polling is fine for v1)

### Done = definition
- [ ] App runs end-to-end locally: register a service → trigger a deploy → watch it run → read the logs

## Notes
- **Deploy command safety:** you're literally running shell commands. Even for a single-tenant tool, don't interpolate untrusted input into a shell string. Note this now; handle it properly when you build Feature 2 (it's a genuine security-track learning moment).
