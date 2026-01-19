# dltHub Pipeline: S3 to MotherDuck

This example demonstrates how to load CSV files from S3 into [MotherDuck](https://motherduck.com/) using [dlt](https://dlthub.com/), running on Tower.

## Overview

The pipeline reads CSV files from an S3 bucket and loads them into a MotherDuck table. MotherDuck is a serverless analytics platform built on DuckDB, providing a powerful cloud-based SQL analytics experience. All configuration is done through Tower app parameters and secrets.

## Prerequisites

- A MotherDuck account (free tier available at [motherduck.com](https://motherduck.com/))
- AWS credentials with read access to the S3 bucket
- Tower CLI installed

## Setup for Local Development

### 1. Create a MotherDuck Account

1. Sign up at [motherduck.com](https://motherduck.com/)
2. After signing in, go to **Settings** → **Access Tokens**
3. Create a new access token and save it securely (you will use it to create a Tower secret)

### 2. Install DuckDB CLI (Optional)

To interact with MotherDuck from the command line, install the DuckDB CLI. See the official installation guide: [duckdb.org/docs/installation](https://duckdb.org/docs/installation/)

### 3. Install Dependencies

```bash
uv sync
```

Or if you prefer pip:

```bash
uv pip install -e .
```

### 4. Create the Secrets

Tower integrates directly with dlt. Create these secrets:

```bash
# MotherDuck token (just the token value, not a connection string)
tower secrets create --name=dlt.destination.motherduck.credentials.password --value='<your_motherduck_token>'

# S3 credentials
tower secrets create --name=dlt.sources.filesystem.credentials.aws_access_key_id --value='AK...'
tower secrets create --name=dlt.sources.filesystem.credentials.aws_secret_access_key --value='...'
```

> **Tip:** Get your MotherDuck token from [app.motherduck.com](https://app.motherduck.com/) → Settings → Access Tokens. The token looks like `eyJhbGciOiJS...`

### 5. Run the Pipeline Locally

Use **Tower local mode** to run the pipeline on your machine while using Tower's secrets management:

```bash
tower run --local
```

To override parameters in local mode:

```bash
tower run --local \
  --parameter=BUCKET_URL="s3://my-bucket/" \
  --parameter=FILE_GLOB="data/*.csv" \
  --parameter=TARGET_TABLE_NAME="my_table"
```

> **Note:** When using `tower run --local`, Tower will inject secrets from your Tower environment. Make sure you've created the required secrets (see "Create the Secrets" section above).

## Deploying to Tower

### 1. Create the App

```bash
tower apps create --name=dlthub-s3-to-motherduck
```

### 2. Deploy the Code

```bash
tower deploy
```

### 3. Run the App

**Run on Tower cloud** (executes on Tower infrastructure):

```bash
tower run
```


**Run with custom parameters** (works with both `--local` and cloud):

```bash
tower run --parameter=BUCKET_URL="s3://my-bucket/" \
  --parameter=FILE_GLOB="data/*.csv" \
  --parameter=TARGET_TABLE_NAME="my_table"
```

## App Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `BUCKET_URL` | S3 bucket URL | `s3://mango-public-data/` |
| `FILE_GLOB` | File pattern to match | `japan-trade-stats/custom_2020.csv` |
| `TARGET_DATABASE` | MotherDuck database name | `my_db` |
| `TARGET_TABLE_NAME` | MotherDuck table name | `trade_stats` |
| `WRITE_DISPOSITION` | Write mode: `replace`, `merge`, or `append` | `replace` |
| `MERGE_KEY` | Column for merge key (required when using `merge`) | *(empty)* |

## Querying Your Data in MotherDuck

### Using the MotherDuck Web UI

1. Go to [app.motherduck.com](https://app.motherduck.com/)
2. Navigate to your database in the left sidebar
3. Click on your table to view the schema
4. Use the SQL editor to run queries:

```sql
SELECT * FROM my_db.trade_stats LIMIT 100;
```

### Using DuckDB CLI with UI Mode

DuckDB provides a browser-based UI for interactive SQL queries. Connect to MotherDuck and launch the UI:

```bash
duckdb -ui "md:?token=<your_token>"
```

This opens a browser window with:
- SQL editor with syntax highlighting
- Table browser
- Query results visualization
- Schema explorer

Once connected, run queries like:

```sql
-- View first 100 rows
SELECT * FROM my_db.trade_stats LIMIT 100;

-- Get row count
SELECT COUNT(*) FROM my_db.trade_stats;

-- Explore schema
DESCRIBE my_db.trade_stats;

-- Sample aggregation
SELECT 
    "Country",
    SUM("Value") as total_value
FROM my_db.trade_stats 
GROUP BY "Country"
ORDER BY total_value DESC
LIMIT 10;
```

### Using DuckDB CLI (Command Line)

For command-line access without the UI:

```bash
duckdb "md:?token=<your_token>"
```

Then run SQL commands directly:

```sql
D SELECT COUNT(*) FROM my_db.trade_stats;
```

## Monitoring

### Check Run Status

```bash
tower apps show
```

### View Run Logs

```bash
tower apps logs dlthub-s3-to-motherduck#1
```

## Troubleshooting

### Credentials Not Working

1. **Verify your secrets are set correctly:**
   ```bash
   tower secrets list
   ```

2. **Check the secret names match exactly:**
   - `dlt.destination.motherduck.credentials.password`
   - `dlt.sources.filesystem.credentials.aws_access_key_id`
   - `dlt.sources.filesystem.credentials.aws_secret_access_key`

3. **Test your MotherDuck connection locally:**
   ```bash
   duckdb "md:?token=<your_token>" -c "SELECT 1"
   ```

### Common Errors

- **"No credentials found"**: Ensure you've created all required secrets in Tower
- **"Access denied to S3"**: Check your AWS credentials have read access to the bucket
- **"Invalid token"**: Verify your MotherDuck token is correct and hasn't expired
- **"Database does not exist"**: The database will be created automatically on first run

## MotherDuck vs Snowflake

| Feature | MotherDuck | Snowflake |
|---------|------------|-----------|
| Pricing | Free tier + usage-based | Warehouse-based |
| Setup | Just a token | Database, warehouse, user, role |
| Local Development | Native DuckDB | Requires cloud connection |
| Query Engine | DuckDB | Snowflake |
| Best For | Analytics, prototyping | Enterprise data warehousing |
