# dbt Core Research (2025)

This note captures current (dbt Core 1.8.x) conventions for building and deploying analytics projects so we can design a Tower example that runs a dbt workload end-to-end.

## Project Layout
- `dbt_project.yml` – central metadata (project name, model paths, default configs, dispatch rules, semantic layer settings).
- `profiles.yml` – connection profiles per environment (`dev`, `staging`, `prod`). Each profile points at a warehouse (Snowflake, BigQuery, Redshift, Databricks, Postgres, DuckDB, etc.) and supplies credentials; most teams template the file with environment variables and keep secrets outside version control.
- `models/` – SQL or Python models organized by subdirectories (e.g. `models/staging`, `models/marts/core`). Each model has a paired `.yml` file defining schema tests, descriptions, and metadata.
- `macros/` – reusable Jinja macros, custom materializations, logging helpers.
- `snapshots/` – slowly changing dimension logic (`dbt snapshot`).
- `seeds/` – CSV inputs versioned with the repo (`dbt seed` to load).
- `tests/` – data quality tests (bespoke macros) to complement schema tests.
- `analyses/`, `exposures/`, `metrics/`, `semantic_models/` – optional directories for ad hoc queries, downstream dependencies, semantic layer definitions, and metrics.
- `packages.yml` – external packages (`dbt-utils`, `dbt-labs/dbt_expectations`, adapter-specific macros).

## Tooling & Environments
- Python 3.10+ is required. Teams typically pin via `pyproject.toml` or `requirements.txt`.
- Install dbt Core plus an adapter (`pip install dbt-core dbt-snowflake`). Adapters track the same 1.8.x major, and 1.8 tightened the adapter contract (`python_sdk` replaced `dbt.adapters.factory`).
- `dbt init` scaffolds `dbt_project.yml`, asks for target warehouse, and optionally generates a starter profile.
- Local developers activate a virtualenv (`uv`, `venv`, `poetry`, `conda`) and copy a templated `profiles.yml` to `~/.dbt/` or point `DBT_PROFILES_DIR` at a project-local profiles directory for CI/CD.
- Credentials are passed with env vars (e.g. `DBT_ENV_SECRET_*`) or secrets managers; dbt 1.8 adds native `.secrets` lookup for Cloud CLI.

## Core Commands
- `dbt deps` – install packages listed in `packages.yml`.
- `dbt seed` – load CSV seed data.
- `dbt run` – build SQL/Python models (incremental models use `unique_key`/`on_schema_change` configs).
- `dbt test` – execute schema tests plus custom data tests.
- `dbt build` – recommended production entrypoint (`deps` + `run` + `test` + `snapshot` + `seed` for selected resources).
- `dbt snapshot` – apply snapshot strategies (`timestamp` or `check`).
- `dbt compile` / `dbt parse` – validation steps used in CI to catch issues quickly.
- `dbt docs generate` & `dbt docs serve` – create documentation site; artifacts land in `target/`.
- `dbt run-operation` – execute macros (e.g., grant statements, maintenance tasks).
- Selection syntax: `state:modified`, `+model_name`, `tag:hourly`, `path:models/marts`, `config.materialized:incremental`.

## Development Flow
1. **Local iteration**
   - Pull latest repo, install deps, configure profile (`dbt debug` to verify connectivity).
   - Edit models/tests, run `dbt build --select state:modified+` to build changed resources with parents/children.
   - Inspect outputs with `dbt show` (new in 1.7/1.8) to preview SQL & sample data.
2. **Documentation/observability**
   - Keep model descriptions in `.yml` files.
   - Use exposures/metrics for downstream visibility.
   - Monitor freshness via `dbt source freshness`.

## Deployment Patterns
- **Version control**: dbt projects live in Git; PRs run CI checks.
- **Continuous integration**:
  - Install Python env, `dbt deps`, optionally `dbt compile` to gate merges.
  - Run targeted builds against a dev warehouse (`dbt build --target ci --select state:modified+`).
  - Store artifacts (`manifest.json`, `run_results.json`) for lineage diffing and anomaly detection.
- **Production orchestration**:
  - `dbt Cloud` provides scheduled jobs, IDE, semantic layer API.
  - CLI-based deployments (self-hosted) use orchestrators like Airflow, Dagster, Prefect, GitHub Actions, or Terraform Cloud. Flow:
    1. Fetch code and packages.
    2. Inject secrets (env vars, profiles).
    3. Run `dbt build --target prod` (or multiple commands separated into tasks).
    4. Persist artifacts to object storage for observability (e.g. ship to S3/GCS via `dbt docs generate` and upload).
    5. Trigger downstream alerts (Slack, PagerDuty) on failure via macros or orchestrator hooks.
- **Semantic Layer**:
  - dbt 1.8 introduces `dbt-sl` (preview) and metrics definitions via `semantic_models/` + `metrics/`. Deployments may run `dbt sl serve` in long-lived services; adapters integrate with BI tools.

## Typical Project Defaults
- Materializations: `table`, `view`, `incremental`, `ephemeral`. Many teams set `models/staging:` to `view` and `models/marts:` to `table`.
- Incremental strategies: `insert_overwrite`, `merge` (adapter-specific). `on_schema_change: sync` standard since 1.8.
- Tests: schema (`unique`, `not_null`, `accepted_values`) and data (`relationships`, custom macros). Failures exit non-zero—important for schedulers.
- Source freshness checks scheduled separately (`dbt source freshness --select source:finance.*`).

## Packaging & Reuse
- `dbt package` is deprecated; `dbt deps` handles installs.
- Packages pinned via git tags or `@` selectors (e.g. `version: [">=1.4.0,<2.0.0"]`).
- Macros allow cross-project reuse; exposures document downstream dashboards.

## Deployment Considerations for Tower
- dbt commands are pure CLI and can run in any container/VM with warehouse connectivity, making them suitable for Tower apps.
- Required inputs:
  - Warehouse credentials (env vars or secrets).
  - `profiles.yml` template or dynamic generation during runtime.
  - Optional target selection, schema naming conventions, `DBT_TARGET_PATH` overrides for artifact storage.
- Outputs to capture:
  - `target/manifest.json`, `run_results.json`, `run_results.dbt` for logging.
  - Console logs for orchestrator visibility (`--log-format json` for structured logging).
- Execution flow inside Tower app:
  1. Install dependencies (e.g. `uv pip install -r requirements.txt` or pre-bake via `pyproject.toml`).
  2. Materialize `profiles.yml` with Tower parameters/secrets.
  3. Optionally run `dbt deps`, `dbt seed`.
  4. Run `dbt build --target {{target}} --select {{selectors}}`.
  5. Upload artifacts to Tower tables or object storage for later review.

These notes will guide the design of `14-dbt-core-ecommerce-analytics`, ensuring the example mirrors real-world dbt Core workflows from local development through scheduled production runs.
