# dltHub Pipeline: S3 to Snowflake

This example demonstrates how to load CSV files from S3 into Snowflake using [dlt](https://dlthub.com/), running on Tower.

## Overview

The pipeline reads CSV files from an S3 bucket and loads them into a Snowflake table. All configuration is done through Tower app parameters and secrets.

## Prerequisites

- A Snowflake account with a database and warehouse
- AWS credentials with read access to the S3 bucket
- Tower CLI installed

## Setup for Local Development

### 1. Create a Snowflake Database and Users

Run the `snowflake_create_database.sql` script to set up:
- The `mango_data` database
- The `raw` schema
- A `LOADER` user for dlt to use

> **Note:** Modify the script to set a secure password for the LOADER user.

### 2. Install Dependencies

```bash
uv sync
```

Or if you prefer pip:
```bash
uv pip install -e .
```

### 3. Create the Secrets

Tower integrates directly with dlt. Create these secrets:

```bash
# Snowflake connection string
tower secrets create --name=dlt.destination.snowflake.credentials --value='snowflake://...'

# S3 credentials
tower secrets create --name=dlt.sources.filesystem.credentials.aws_access_key_id --value='AK...'
tower secrets create --name=dlt.sources.filesystem.credentials.aws_secret_access_key --value='...'
```

> **Tip:** The Snowflake connection string format:
>
> ```
> snowflake://<user>:<password>@<account_id>/<database>?warehouse=<warehouse>&role=<role>
> ```
>
> For example:
> ```
> snowflake://loader:mypassword@abc12345.us-east-1/mango_data?warehouse=COMPUTE_WH&role=LOADER_ROLE
> ```

### 4. Run the Pipeline Locally

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
tower apps create --name=dlthub-s3-to-snowflake
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
| `TARGET_SCHEMA_NAME` | Snowflake schema | `raw` |
| `TARGET_TABLE_NAME` | Snowflake table | `trade_stats` |
| `WRITE_DISPOSITION` | Write mode: `replace`, `merge`, or `append` | `replace` |
| `REPLACE_STRATEGY` | For replace: `truncate-and-insert` or `insert-from-staging` | `truncate-and-insert` |
| `MERGE_KEY` | Column for merge key (required when using `merge`) | *(empty)* |

## Monitoring

### Check Run Status

```bash
tower apps show
```

### View Run Logs

```bash
tower apps logs dlthub-s3-to-snowflake#1
```

## Troubleshooting

### Credentials Not Working

1. **Verify your secrets are set correctly:**
   ```bash
   tower secrets list
   ```

2. **Check the secret names match exactly:**
   - `dlt.destination.snowflake.credentials`
   - `dlt.sources.filesystem.credentials.aws_access_key_id`
   - `dlt.sources.filesystem.credentials.aws_secret_access_key`

3. **Test your Snowflake connection string locally** before deploying to Tower.

### Common Errors

- **"No credentials found"**: Ensure you've created all required secrets in Tower
- **"Access denied to S3"**: Check your AWS credentials have read access to the bucket
- **"Database does not exist"**: Verify the database name in your connection string matches your Snowflake setup

