# Builder scaffold mirror

This document records the visible builder scaffold that was mirrored into the repository without replacing the stronger existing root README.

## Mirrored structure

- `apps/api`: FastAPI backend shell with a `/health` endpoint
- `apps/web`: Next.js frontend shell for the visible MVP workflow areas
- `docker-compose.yml`: local orchestration baseline for API and web services

## Preserved repository structure

The repository already contains a Python MVP core under `src/vermitlo_mvp` with a documented demo flow in the root `README.md`. That structure remains the current executable product core. The new `apps/` scaffold is added alongside it as the next frontend/backend app foundation, not as a replacement.

## Current boundary

This scaffold is intentionally small. It does not yet include authentication, relational persistence, migrations, seed data, or the full domain API. Those are the next Stage 2 repository steps.
