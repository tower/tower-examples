# Write Ticker Data to Iceberg

This example demonstrates how to download stock ticker data from Yahoo Finance and write it to an Iceberg table using Tower.

## Overview

The pipeline uses [yfinance](https://github.com/ranaroussi/yfinance) to download daily stock data (open, close, volume) for a list of tickers and stores it in an Iceberg table. The pipeline uses **upsert** to make it idempotent - you can safely re-run it with the same parameters without creating duplicates.

## Prerequisites

- Tower CLI installed
- An Iceberg catalog configured in Tower (see setup below)

## App Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `PULL_DATE` | Date of stock data to pull (YYYY-MM-DD). If empty, uses yesterday's date. | *(empty)* |
| `END_DATE` | Optional end date. Data is pulled from PULL_DATE up to (but not including) END_DATE. | *(empty)* |
| `TICKERS` | Comma-separated list of stock tickers | `MSFT,AAPL,GOOGL,NVDA` |

## Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure an Iceberg Catalog

This app writes to an Iceberg table, which requires an Iceberg catalog configured in Tower.

1. Go to [app.tower.dev](https://app.tower.dev/)
2. Navigate to your environment settings
3. Check if a catalog named `default` already exists; if not, create one

> **Note:** This app expects a catalog with the name `default`. See the [Tower Iceberg catalog guide](https://docs.tower.dev/docs/concepts/environments#catalogs) for setup instructions.

### 3. Run the Pipeline Locally

Use **Tower local mode** to run the pipeline on your machine:

```bash
tower run --local \
  --parameter=PULL_DATE="2025-05-01" \
  --parameter=TICKERS="MSFT,AAPL,AMZN,GOOGL,NVDA"
```

To pull a range of dates:

```bash
tower run --local \
  --parameter=PULL_DATE="2025-05-01" \
  --parameter=END_DATE="2025-05-08" \
  --parameter=TICKERS="MSFT,AAPL"
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
  --parameter=PULL_DATE="2025-05-01" \
  --parameter=TICKERS="MSFT,AAPL,AMZN"
```

## Schedule

You can configure this app to run automatically on a schedule using the Tower CLI.

**Create a schedule** (runs daily at 9:00 AM UTC):

```bash
tower schedules create --app=write-ticker-data-to-iceberg --cron="0 9 * * *"
```

**Create a schedule with parameters:**

```bash
tower schedules create --app=write-ticker-data-to-iceberg --cron="0 9 * * *" \
  --parameter=TICKERS="MSFT,AAPL,GOOGL"
```

## Querying the Data

After running the pipeline, the data is stored in the `daily_ticker_data` table. You can query it using any tool that connects to your Iceberg catalog.

**Table Schema:**

| Column | Type | Description |
|--------|------|-------------|
| `ticker` | string | Stock ticker symbol (e.g., AAPL) |
| `date` | string | Date in YYYY-MM-DD format |
| `open` | float64 | Opening price |
| `close` | float64 | Closing price |
| `volume` | int64 | Trading volume |

**Example query (DuckDB):**

```sql
SELECT ticker, date, open, close, volume
FROM daily_ticker_data
WHERE ticker = 'AAPL'
ORDER BY date DESC
LIMIT 10;
```

## Monitoring

### Check Run Status

```bash
tower apps show write-ticker-data-to-iceberg
```

### View Run Logs

```bash
tower apps logs "write-ticker-data-to-iceberg#1"
```

## Related Apps

This app is part of a ticker project:

- **05-write-ticker-data-to-iceberg** (this app) - Acquires daily ticker data
- **06-analyze-ticker-data-in-iceberg** - Creates buy/sell recommendations from the data
- **11-trim-ticker-table** - Cleans old data from the table
- **13-ticker-update-agent** - AI agent that answers stock price questions using cached data