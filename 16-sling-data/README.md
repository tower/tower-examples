# Replicate Data into Snowflake with Sling

You need to move data into a warehouse without writing pipeline code. This app uses [Sling](https://slingdata.io/) to replicate a local JSON file into a Snowflake table from a declarative YAML config — the Python is just a thin runner.

## What It Does

1. Reads the replication config from [sling.yaml](./sling.yaml) (source: the bundled [data/input.json](./data/input.json); target: `PUBLIC.SLING_JSON_TOWER_DEMO`)
2. Runs the replication in `full-refresh` mode

Point `sling.yaml` at your own sources and targets; Sling supports databases, object stores, and files.

## What You Need

A Tower secret named `SNOWFLAKE_URL` with your Snowflake connection string, in [Sling's URL format](https://docs.slingdata.io/connections/database-connections/snowflake):

```bash
tower secrets create --name=SNOWFLAKE_URL --value="snowflake://user:password@account/database?schema=PUBLIC&warehouse=COMPUTE_WH"
```

> **Note:** Inline values like this end up in your shell history. Use a throwaway or sandbox Snowflake user for testing, and avoid pasting production credentials into commands.

## Run It

```bash
cd 16-sling-data
tower deploy
tower run
```
