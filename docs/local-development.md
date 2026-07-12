# Local development

This repo keeps `src/vermitlo_mvp` as the canonical MVP core and adds `apps/web` as the first visible interface shell.

## Python demo mode

Use this mode to execute the synthetic workflow directly.

```bash
PYTHONPATH=src python -m vermitlo_mvp.demo
```

## Python server mode

Use this mode to run the lightweight HTTP API around the MVP core.

```bash
PYTHONPATH=src python -m vermitlo_mvp.server
```

Then open `http://127.0.0.1:8000/health` or post to `http://127.0.0.1:8000/demo/run`.

## Shared UI and backend mode

Use this mode to run the first web shell together with the current backend/runtime path.

```bash
docker compose up --build
```

Then open:

- Web shell: `http://127.0.0.1:3000`
- Backend health: `http://127.0.0.1:8000/health`
- Demo endpoint: `http://127.0.0.1:8000/demo/run`

`docker-compose.override.yml` keeps the backend reachable from outside the container without replacing the existing Python core.

## Current boundaries

- The web shell is an early product shell, not the final marketing website.
- Approval, submission, outcome, billing, and payment remain synthetic demo flows.
- No live tender portal submission, real payment execution, production source adapter, auth, tenancy, schema, or migration layer is included in this slice.
- No legally binding offer is created without explicit human approval.
