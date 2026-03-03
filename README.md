# WebUp

A production-oriented scaffold for an agnostic, event-driven data pipeline with a dual-purpose PWA control plane.

## What This Includes

- Temporal orchestration (control plane) with worker + trigger consumer
- Valkey streams as message bus + real-time observability feed
- Next.js 15 PWA with:
  - Command Center (JSON config validate + trigger)
  - Bespoke Viewer (logs + data inspector)
- Python plugin ingestor fleet (hot-swappable domains)
- AI analyzer service (Ollama local, OpenAI-compatible cloud path)
- PostgreSQL 16 + TimescaleDB, ClickHouse, MinIO
- Log retention cleanup service (`N`-day retention)
- Unit, sanity, and Playwright e2e test scaffolds

## Repo Layout

- `/apps/pwa-interface`
- `/services/workflow-engine`
- `/services/ingestor-fleet`
- `/services/ai-analyzer`
- `/packages/shared-lib`
- `/config/job-templates`
- `/config/sql`
- `/tests`

## Prerequisites

- Docker Desktop (with `docker` + `docker compose` in PATH)
- Node.js 22+
- Python 3.12+ (3.14 works for local tests)

## Quick Start (Ready-to-Use)

1. Create env file:
   - `cp .env.example .env`
2. Install local tooling:
   - `make install`
3. Start full stack:
   - `make up`
4. Pull local LLM model once:
   - `make model-pull`
5. Run all tests:
   - `make test-all`
6. Run full live pipeline e2e check:
   - `make full-e2e`
   - optional timeout override: `E2E_TIMEOUT_SECONDS=1200 make full-e2e`

## URLs

- PWA: `http://localhost:3000`
- Temporal UI: `http://localhost:8080`
- Analyzer API docs: `http://localhost:8010/docs`
- MinIO Console: `http://localhost:9001`

## Job Config Contract

Schema: `/config/job-templates/job_config.schema.json`

Required sections:
- `ingestor_plugin`
- `analyzer_plugin`
- `pipeline_settings`
- `storage_policy`

Default template:
- `/config/job-templates/default.job_config.json`

## Test Layers

- Unit:
  - `make test-unit`
- Sanity (service wiring):
  - `make test-sanity`
- Browser e2e + screenshots:
  - `make test-e2e`
  - screenshots in `/tests/e2e/screenshots/`
- Full pipeline e2e (trigger -> ingest -> analyze completion):
  - `make full-e2e`
  - first run can take several minutes while Ollama warms `llama3`

## Log Retention (N Days)

Service:
- `log-cleanup` (`services/workflow-engine/src/workflow_engine/log_cleanup.py`)

Env controls:
- `LOG_RETENTION_DAYS` (default: `14`)
- `CLEANUP_INTERVAL_SECONDS` (default: `86400`)

Cleanup targets:
- Valkey stream `logs:stream`
- PostgreSQL: `jobs`, `ingested_records`, `analysis_results`
- ClickHouse: `webup.logs_stream`

## Operations

- Start: `make up`
- Stop: `make down`
- Tail logs: `make logs`
- Rebuild specific services:
  - `docker compose up --build -d workflow-engine workflow-trigger ai-analyzer`

## Packaging Notes

- Services are containerized with multi-stage Dockerfiles where relevant.
- Worker services are stateless and restart automatically (`restart: unless-stopped`).
- The scaffold is cloud-ready by env override (managed Postgres/Valkey/OpenAI endpoints).
- Generated screenshots and test artifacts are local and reproducible.
