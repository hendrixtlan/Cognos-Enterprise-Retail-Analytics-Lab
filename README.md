# Cognos Enterprise Retail Analytics Lab (v0.2)

Reproducible, testable PostgreSQL retail warehouse and Cognos 12 semantic-modeling lab. No IBM software or unlicensed artifacts are distributed. v0.2 includes a line-versus-order semantic contract, inventory snapshots, validation-first SQL benchmark, reporting roles, and PostgreSQL integration CI.

## Prerequisites

- Python 3.10+ and Docker Compose; run commands from the repository root.
- PostgreSQL 16 supplied by Docker Compose.
- Cognos Analytics 12 server and compatible authoring tools **only for the IBM-dependent exercises**.

## Quickstart

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate   # PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
docker compose --env-file .env -f infrastructure/docker-compose.yml up -d --wait
retail-lab init
retail-lab generate --sales 100000 --stores 25 --products 200 --days 365
retail-lab load
retail-lab optimize
retail-lab contract
retail-lab validate
retail-lab benchmark --repeats 5
pytest -q
```

**Version upgrade warning:** v0.2 changes fact table schema from v0.1. Reset your disposable v0.1 local DB volume before running `init`; schema creation is **not** an in-place migration. `docker compose -f infrastructure/docker-compose.yml down -v` permanently deletes local database volume data.

`DATABASE_URL` must match the Docker credentials. The example uses development-only credentials and binds PostgreSQL to 127.0.0.1. Never publish this port or example credentials for production. The `.env` file is gitignored. `load` is a one-time bulk load; regenerate/reset a disposable database before repeating it.

## What is runnable without Cognos?

| Item | Execution | Evidence |
|---|---|---|
| Dockerized PostgreSQL | Local Compose / GitHub Actions service | DB readiness |
| Deterministic 3-line-order sales generation | Python / CLI | Unit tests; full CSV files |
| Periodic inventory snapshots | Python / CLI | Snapshot key tests; FK constraints |
| Warehouse and reporting views | SQL and DB ingestion | Integration tests |
| Refreshable sales aggregate | PostgreSQL materialized view | Reconciliation |
| Static semantic KPI catalog | `retail-lab contract` | Machine-readable JSON |
| SQL performance benchmark | PostgreSQL | Exact result parity, JSON plans, timings |
| Cognos FM package and reports | **Cognos access required** | Guide only; no fabricated native artifacts |
| Cognos Data Modules/reporting | **Cognos access required** | Guide only; no fabricated native artifacts |

## Grain and modeling pitfalls

- `mart.fact_sales` = one row **per sales line**. Three consecutive lines share an `order_id` and the same store/date. `COUNT(*)` is sales-line count, not distinct order count.
- `COUNT(DISTINCT order_id)` is non-additive across SKU groups, so the daily SKU-grain MV only exposes `sales_line_count`.
- `mart.fact_inventory_daily` = store-product-date snapshot at a configurable interval (`--inventory-step-days 7`); summed across dates, `on_hand_units` is meaningless.
- Ratio KPIs (margin%, AOV) are calculated from correctly aggregated numerators and denominators, not averaged from row-level ratios.
- No tax, returns, promotions, customers, or seasonal demand yet. Synthetic data proves mechanics and grain, not real-world demand realism.

## Repository map

- `src/retail_lab/`: generator, DB CLI, validations, SQL benchmarks, catalog checks.
- `warehouse/`: schema, indexes, materialized view, curated views, reporting role.
- `semantic/`: KPI catalog, relationship matrix, determinant reference.
- `cognos/framework-manager/`: IBM Cognos 12 Framework Manager authoring and package steps.
- `cognos/data-modules/`: IBM Cognos 12 Data Modules comparison track.
- `cognos/reports/`: reports and acceptance tests requiring Cognos.
- `docs/verification.md`: repeatable evidence collection protocol.
- `.github/workflows/ci.yml`: unit and PostgreSQL service integration jobs; SQL benchmark artifact.

## Test commands

```bash
pytest -q -k 'not integration'    # Python, no PostgreSQL required
# PostgreSQL integration requires full quickstart and:
RUN_DB_TESTS=1 pytest -q tests/test_integration.py
```

CI runs actual PostgreSQL integration separately. Until executed in a Docker-capable environment, the CI definition alone is **not** evidence that the integration tests pass.

## Cognos dependency boundary

There is no Cognos instance in this repository. Framework Manager packages, native report specs and report-duration proof require a licensed Cognos server and compatible authoring client. SQL performance evidence is never labeled as Cognos report-performance evidence. See [Framework Manager guide](cognos/framework-manager/modeling-guide.md), [Data Modules guide](cognos/data-modules/modeling-guide.md) and [verification plan](docs/verification.md).
