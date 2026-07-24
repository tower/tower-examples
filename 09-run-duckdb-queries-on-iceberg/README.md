# Query Iceberg Tables with DuckDB

You have data in an Iceberg lakehouse and just want to run SQL on it — without standing up a query engine. This app connects DuckDB to a Tower Iceberg catalog and runs a query against the `daily_ticker_data` table (populated by [05-write-ticker-data-to-iceberg](../05-write-ticker-data-to-iceberg)).

## What It Does

1. Loads DuckDB's `iceberg` and `httpfs` extensions
2. Creates a DuckDB `SECRET` from your Iceberg REST catalog credentials
3. Attaches the catalog as a database and runs a plain `SELECT` against it

Swap the query at the bottom of [main.py](./main.py) for your own SQL.

## What You Need

- A Tower Iceberg catalog containing data (run example 05 first)
- Three Tower secrets with your Iceberg REST catalog credentials:

```bash
tower secrets create --name=IRC_CLIENT_ID --value="[YOUR_CLIENT_ID]"
tower secrets create --name=IRC_CLIENT_SECRET --value="[YOUR_CLIENT_SECRET]"
tower secrets create --name=IRC_ENDPOINT --value="[YOUR_CATALOG_ENDPOINT]"
```

## Run It

```bash
cd 09-run-duckdb-queries-on-iceberg
tower deploy
tower run
```

Add `--local` to `tower run` to execute on your machine while still reading secrets from Tower.
