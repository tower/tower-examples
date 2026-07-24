# Tower Examples

Working example apps for [Tower](https://tower.dev), each built around a common data problem. Every example is a complete Tower app — a few Python files plus a `Towerfile` — that you can clone, deploy, and run in minutes, then adapt to your own stack.

## Quick start

Install the [Tower CLI](https://docs.tower.dev/getting-started/installation), sign in, and run the first example — it needs no secrets and no setup:

```bash
git clone https://github.com/tower/tower-examples.git
cd tower-examples/01-hello-world
tower login
tower deploy
tower run
```

Then pick the example below that matches the problem you're actually trying to solve.

## Find your problem

### Start here — runs with zero setup

| Example | The problem it solves | What you need |
|---|---|---|
| [01-hello-world](./01-hello-world) | See the whole Tower workflow — deploy, run, parameters, logs — in two minutes | Nothing |
| [15-interactive-marimo-notebook](./15-interactive-marimo-notebook) | Serve an interactive Python notebook as a running app, no infra to host | Nothing |

### Load files into a warehouse

| Example | The problem it solves | What you need |
|---|---|---|
| [02-dlthub-s3-to-snowflake](./02-dlthub-s3-to-snowflake) | CSVs land in S3 and need to end up in Snowflake, incrementally and reliably (dlt) | Snowflake credentials — the source bucket is public |
| [03-dlthub-s3-to-motherduck](./03-dlthub-s3-to-motherduck) | Same S3 ingestion problem, targeting MotherDuck (dlt) | MotherDuck token — the source bucket is public |
| [16-sling-data](./16-sling-data) | Replicate local/JSON data into Snowflake with a declarative YAML config (Sling) | Snowflake connection secret |

### Build a lakehouse on Apache Iceberg

These examples form a small end-to-end lakehouse: ingest → analyze → query → maintain. They share one prerequisite: an Iceberg catalog named `default` in your Tower account ([how to set one up](https://docs.tower.dev)).

| Example | The problem it solves | What you need |
|---|---|---|
| [05-write-ticker-data-to-iceberg](./05-write-ticker-data-to-iceberg) | Pull data from an external API on a schedule and land it in an Iceberg table (demo data: stock prices) | Iceberg catalog — no API keys |
| [06-analyze-ticker-data-in-iceberg](./06-analyze-ticker-data-in-iceberg) | Run LLM-assisted analysis over data already in your lakehouse | Iceberg catalog + inference secrets |
| [09-run-duckdb-queries-on-iceberg](./09-run-duckdb-queries-on-iceberg) | Query Iceberg tables with plain SQL from DuckDB | Iceberg REST catalog credentials |
| [11-trim-ticker-table](./11-trim-ticker-table) | Enforce a retention window by deleting old rows from an Iceberg table | Iceberg catalog with data (run 05 first) |
| [17-list-catalog-tables](./17-list-catalog-tables) | Inspect what namespaces and tables exist in a catalog | Iceberg catalog |
| [18-read-table-rows](./18-read-table-rows) | Peek at the first rows of any Iceberg table | Iceberg catalog with data |

### Orchestrate many runs

| Example | The problem it solves | What you need |
|---|---|---|
| [08-fan-out-ticker-runs](./08-fan-out-ticker-runs) | Fan one job out into parallel runs and wait for them all (Tower `run`/`wait`) | Example 05 deployed |

### Put LLMs and agents to work on your data

| Example | The problem it solves | What you need |
|---|---|---|
| [07-deepseek-summarize-github](./07-deepseek-summarize-github) | Feed operational data (GitHub issues) to an LLM and get an actionable recommendation back | Iceberg catalog + inference secrets |
| [13-ticker-update-agent](./13-ticker-update-agent) | Deploy an AI agent that answers questions from — and maintains — business data in your lakehouse | Iceberg catalog + `OPENAI_API_KEY` |

### Run dbt in production

| Example | The problem it solves | What you need |
|---|---|---|
| [14-dbt-core-ecommerce-analytics](./14-dbt-core-ecommerce-analytics) | Run a real dbt Core project (seed → build) as a deployable, schedulable app | `DBT_PROFILE_YAML` secret with your warehouse profile |

## How every example works

Each directory is a self-contained Tower app:

- **`Towerfile`** — declares the app: name, entrypoint script, source files, and runtime parameters.
- **A Python script** — ordinary Python; no framework to learn.
- **`pyproject.toml`** — dependencies, installed automatically at run time.

The workflow is always the same: `tower deploy` from the example's directory, then `tower run` (add `--local` to execute on your machine while still using Tower secrets and catalogs). Set secrets with `tower secrets create`; each example's README lists exactly which ones it needs.

## Learn more

- [Tower documentation](https://docs.tower.dev) — concepts, CLI reference, guides
- [Tower Control](https://control.tower.dev) — describe an app in natural language and let the agent build and deploy it
- [tower.dev](https://tower.dev) — what Tower is and who it's for
