# 18: Read Table Rows

Read the first N rows from an Iceberg table using the Tower SDK and Polars.

## Overview

This app connects to a Tower Iceberg catalog, loads a specified table, and returns the first N rows. It's useful for quickly previewing table contents and schema without loading the entire dataset.

## App Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `CATALOG_NAME` | Name of the Iceberg catalog | `default` |
| `NAMESPACE` | Namespace (schema) containing the table | `default` |
| `TABLE_NAME` | Name of the Iceberg table to read | `daily_ticker_data` |
| `NUM_ROWS` | Number of rows to return | `10` |

## Prerequisites

1. **Tower CLI**: Install and authenticate with Tower
   ```bash
   tower login
   ```

2. **Iceberg Catalog**: Ensure you have a catalog configured in your Tower environment. Check your catalogs in **Tower Settings → Catalogs** in the web UI.

3. **Existing Table**: The table you want to read must already exist in the catalog.

## Setup

Navigate to the example directory:

```bash
cd 18-read-table-rows
```

## Running the App

### Local Mode

Run with default parameters (reads `daily_ticker_data` table):

```bash
tower run --local
```

Run with a specific environment:

```bash
tower run --local --environment=prod
```

Specify a different table and number of rows:

```bash
tower run --local --parameter=TABLE_NAME=url_html_snapshots --parameter=NUM_ROWS=5
```

Read from a specific namespace:

```bash
tower run --local --parameter=TABLE_NAME=issue_threads --parameter=NAMESPACE=github --parameter=NUM_ROWS=20
```

Read from a different catalog:

```bash
tower run --local --parameter=CATALOG_NAME=my-catalog --parameter=TABLE_NAME=my_table
```

### Deploying to Tower

1. Create the app (first time only):
   ```bash
   tower apps create --name=read-table-rows
   ```

2. Deploy:
   ```bash
   tower deploy
   ```

3. Run on Tower Cloud:
   ```bash
   tower run --environment=prod --parameter=CATALOG_NAME=default --parameter=TABLE_NAME=daily_ticker_data --parameter=NUM_ROWS=10
   ```

## Example Output

```
============================================================
📊 READ TABLE ROWS
============================================================
Catalog: default
Table: default.daily_ticker_data
Rows to fetch: 10
============================================================

✓ Table loaded successfully
  Total rows in table: 1500
  Rows returned: 10

📋 SCHEMA (6 columns)
----------------------------------------
  ticker: String
  date: String
  open: Float64
  high: Float64
  low: Float64
  close: Float64

📄 DATA (first 10 rows)
----------------------------------------
shape: (10, 6)
┌────────┬────────────┬─────────┬─────────┬─────────┬─────────┐
│ ticker ┆ date       ┆ open    ┆ high    ┆ low     ┆ close   │
│ ---    ┆ ---        ┆ ---     ┆ ---     ┆ ---     ┆ ---     │
│ str    ┆ str        ┆ f64     ┆ f64     ┆ f64     ┆ f64     │
╞════════╪════════════╪═════════╪═════════╪═════════╪═════════╡
│ AAPL   ┆ 2024-01-15 ┆ 185.23  ┆ 186.45  ┆ 184.12  ┆ 185.89  │
│ ...    ┆ ...        ┆ ...     ┆ ...     ┆ ...     ┆ ...     │
└────────┴────────────┴─────────┴─────────┴─────────┴─────────┘

============================================================
✓ Done!
============================================================
```

## Monitoring

View logs from a run:

```bash
tower apps logs "read-table-rows#1"
```

## Related Apps

- **[05-write-ticker-data-to-iceberg](../05-write-ticker-data-to-iceberg/)**: Write ticker data to the table this app reads
- **[17-list-catalog-tables](../17-list-catalog-tables/)**: List all tables in a catalog to find what to read
- **[21-read-url-snapshots](../21-read-url-snapshots/)**: Another example of reading Iceberg tables
