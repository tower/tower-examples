# List Catalog Tables

A Tower app that lists all namespaces and tables in a Tower Iceberg catalog.

## Overview

This app connects to a Tower Iceberg REST catalog and displays:
- All namespaces in the catalog
- All tables within each namespace
- Optional: table schema details

This is useful for exploring what data is available in your Tower catalog.

## App Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `CATALOG_NAME` | Name of the Tower Iceberg catalog | `default` |
| `SHOW_DETAILS` | Show table schema details (true/false) | `false` |

## Prerequisites

- Tower CLI installed and configured
- At least one Iceberg catalog configured in Tower

## Setup

### 1. Install Dependencies

```bash
cd 17-list-catalog-tables
uv sync
```

### 2. Configure Iceberg Catalog

Ensure you have at least one Iceberg catalog configured in Tower. Catalogs are managed through the Tower web interface:

1. Go to Tower Settings → Catalogs
2. Check if you have any catalogs configured
3. If not, create one by clicking "Add Catalog" and following the setup wizard

The app uses the `default` catalog by default, but you can specify a different catalog using the `CATALOG_NAME` parameter.

### 3. Run Locally

List tables in the default catalog:

```bash
tower run --local
```

List tables with schema details:

```bash
tower run --local --parameter=SHOW_DETAILS=true
```

List tables in a different catalog:

```bash
tower run --local --parameter=CATALOG_NAME=my-catalog
```

### 4. Run in a Different Environment

To list tables using a specific Tower environment's catalog configuration:

```bash
tower run --local --environment=prod
```

Combine environment with catalog name:

```bash
tower run --local --environment=prod --parameter=CATALOG_NAME=my-catalog
```

## Deploying to Tower

### Deploy the App

```bash
tower deploy
```

### Run on Tower Cloud

```bash
tower run
```

Or with parameters:

```bash
tower run --environment=prod --parameter=CATALOG_NAME=production --parameter=SHOW_DETAILS=true
```

## Example Output

```
Connecting to catalog: default
Endpoint: https://...
============================================================

📁 NAMESPACES
----------------------------------------
  • default
  • analytics

📊 TABLES BY NAMESPACE
----------------------------------------

  [default]
    └─ daily_ticker_data
    └─ url_html_snapshots

  [analytics]
    └─ aggregated_metrics

============================================================
📈 SUMMARY
   Namespaces: 2
   Total Tables: 3
============================================================
```

With `SHOW_DETAILS=true`:

```
  [default]
    └─ daily_ticker_data
       Schema: 8 columns
         - ticker: string
         - date: date
         - open: double
         - high: double
         - low: double
         ... and 3 more columns
```

## Monitoring

### Check App Status

```bash
tower apps show list-catalog-tables
```

### View Run Logs

```bash
tower apps logs "list-catalog-tables#1"
```

## How It Works

1. The app connects to the catalog using PyIceberg's REST catalog client
2. Lists all namespaces using `catalog.list_namespaces()`
3. For each namespace, lists tables using `catalog.list_tables(namespace)`
4. Optionally loads and displays schema information for each table

