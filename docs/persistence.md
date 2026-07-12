# Persistence Baseline

The first persistence layer is intentionally small and local-first.

## What exists

- `migrations/0001_initial.sql` defines the SQLite-compatible MVP schema.
- `vermitlo_mvp.persistence.apply_migrations(db_path)` applies all SQL files in order.
- `seed_demo_data(db_path)` loads the existing `data/company_profile.json` and `data/tender.json` into the schema.
- `persist_demo_run(db_path, approved=True)` runs the current demo workflow and stores the resulting match, dossier, approval, submission simulation, outcome simulation, billing event, and audit event.

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

Expose read-only API endpoints for persisted tenants, company profiles, tenders, and the latest demo dossier snapshot. Then add a proper migration command or script once the repository layout settles.
