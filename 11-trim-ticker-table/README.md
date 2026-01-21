# Trim Ticker Table

This app demonstates deletes from an Iceberg table. It shows how to delete old data from an Iceberg table using Tower.

## Overview

The app inspects the `daily_ticker_data` table and removes all records older than a specified time window. This is useful for maintaining a rolling window of recent data and controlling storage costs.

The app is **idempotent** - you can safely re-run it multiple times with the same parameters.

## App Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `TIME_WINDOW_DAYS` | Number of days of history to keep | `31` |

## Prerequisites

- Tower CLI installed
- An Iceberg catalog configured in Tower (see setup below)
- The `daily_ticker_data` table exists (created by example 05)

## Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure an Iceberg Catalog

This app reads from and writes to an Iceberg table, which requires an Iceberg catalog configured in Tower.

1. Go to [app.tower.dev](https://app.tower.dev/)
2. Navigate to your environment settings
3. Check if a catalog named `default` already exists; if not, create one

> **Note:** This app expects a catalog with the name `default`. See the [Tower Iceberg catalog guide](https://docs.tower.dev/docs/concepts/environments#catalogs) for setup instructions.

### 3. Run the Pipeline Locally

Use **Tower local mode** to run the pipeline on your machine:

```bash
tower run --local
```

Or override the time window:

```bash
tower run --local \
  --parameter=TIME_WINDOW_DAYS="14"
```

> **Note:** When using `tower run --local`, Tower connects to your configured Iceberg catalog. Make sure the catalog is set up before running.

## Deploying to Tower

### 1. Deploy the App

```bash
tower deploy
```

If the app doesn't exist, Tower will prompt you to create it.

### 2. Run the App

**Run on Tower cloud:**

```bash
tower run
```

**Run with custom parameters:**

```bash
tower run \
  --parameter=TIME_WINDOW_DAYS="7"
```

## Schedule

This app is designed to run on a daily schedule to complement the `write-ticker-data-to-iceberg` app. Together they maintain a rolling window of recent ticker data.

**Create a schedule** (runs daily at 10:00 AM UTC):

```bash
tower schedules create --app=trim-ticker-table --cron="0 10 * * *"
```

**List schedules:**

```bash
tower schedules list --app=trim-ticker-table
```

**Delete a schedule:**

```bash
tower schedules delete --app=trim-ticker-table --schedule=<schedule-id>
```

## Monitoring

### Check Run Status

```bash
tower apps show trim-ticker-table
```

### View Run Logs

```bash
tower apps logs "trim-ticker-table#1"
```

## Related Apps

This app is part of a ticker data project:

- **05-write-ticker-data-to-iceberg** - Acquires daily ticker data from Yahoo Finance
- **06-analyze-ticker-data-in-iceberg** - Creates buy/sell recommendations from the data
- **11-trim-ticker-table** (this app) - Cleans old data from the table
- **13-ticker-update-agent** - AI agent that answers stock price questions using cached data