# Persistence Baseline

The first persistence layer is intentionally small and local-first.

## What exists

- `migrations/0001_initial.sql` defines the SQLite-compatible MVP schema.
- `vermitlo_mvp.persistence.apply_migrations(db_path)` applies all SQL files in order.
- `seed_demo_data(db_path)` loads the existing `data/company_profile.json` and `data/tender.json` into the schema.
- `persist_demo_run(db_path, approved=True)` runs the current demo workflow and stores the resulting match, dossier, approval, submission simulation, outcome simulation, billing event, and audit event.
- Read-model helpers return tenant, company, tender, and latest dossier snapshots for API use.

## API surface

The FastAPI scaffold exposes persisted demo objects through read-only endpoints:

- `POST /demo/persist`
- `GET /tenants/tenant-demo-it-001`
- `GET /company-profile`
- `GET /tender`
- `GET /dossier/latest`

Each endpoint initializes and seeds the local demo database if needed. The default database path is `var/vermitlo.sqlite3` and can be changed with `VERMITLO_DB_PATH`.

## Current boundary

This layer is not yet a production repository abstraction. It is a persistence baseline for local MVP verification and future API endpoints. The schema keeps simulation tables separate from real submission or payment integrations.

## Example

```bash
PYTHONPATH=src python - <<'PY'
from pathlib import Path
from vermitlo_mvp.persistence import apply_migrations, persist_demo_run

db = Path('var/vermitlo.sqlite3')
apply_migrations(db)
print(persist_demo_run(db, approved=True))
PY
```

## Next step

Add a small UI read path that calls the persisted API endpoints and renders the current tenant, tender, match, dossier, approval/submission, and billing state in one dashboard view.
