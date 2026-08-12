# Analyze Lakehouse Data with an LLM

You have data accumulating in your lakehouse and want an LLM to reason over it — with no export pipeline to build. This app runs statistical analysis directly on an Iceberg table, then sends the derived metrics to the Deepseek R1 LLM to generate buy/sell/hold recommendations from trends in stock prices and trading volume. Example [05-write-ticker-data-to-iceberg](../05-write-ticker-data-to-iceberg) populates the `daily_ticker_data` Iceberg table; this app reads it.

## Overview

1. Loads stock data from the `daily_ticker_data` Iceberg table
2. Computes 7-day and 30-day moving averages, volatility, and trend scores
3. Filters data to the specified analysis date
4. Sends the analysis to Deepseek R1 for buy/sell/hold recommendations

## App Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ANALYZE_DATE` | The date to analyze (YYYY-MM-DD format) | Yesterday's date |

## Prerequisites

- A Tower account with an Iceberg catalog configured (Tower-hosted, created automatically when you deploy from the [Tower app](https://app.tower.dev))
- The `daily_ticker_data` table populated by [05-write-ticker-data-to-iceberg](../05-write-ticker-data-to-iceberg)
- A Hugging Face account with an API token, or skip this and check **Use Tower sandbox value** on the setup screen when deploying from the Tower app

### Sign Up for Hugging Face Hub

1. [Sign up for Hugging Face](https://huggingface.co/join)
2. Get your [access token](https://huggingface.co/docs/hub/en/security-tokens)

## Setup

### 1. Install Dependencies

```bash
cd 06-analyze-ticker-data-in-iceberg
uv sync
```

### 2. Configure an Iceberg Catalog

Ensure you have an Iceberg catalog named `default` configured in the [Tower UI](https://app.tower.dev). If you haven't created one yet, follow the instructions in the Tower documentation.

### 3. Create the Secrets

If you deploy from the Tower app, the setup screen can fill these with Tower's sandbox values for testing, so no Hugging Face account is needed. On the CLI path, add your inference provider credentials as Tower secrets:

```bash
tower secrets create --environment="default" \
  --name=TOWER_INFERENCE_ROUTER --value="hugging_face_hub"

tower secrets create --environment="default" \
  --name=TOWER_INFERENCE_ROUTER_API_KEY --value="[YOUR_HF_TOKEN_HERE]"
```

### 4. Run the Pipeline Locally

Use Tower local mode to run the pipeline while accessing secrets from the Tower Secrets Manager:

```bash
tower run --local --parameter=ANALYZE_DATE='2025-04-11'
```

If `ANALYZE_DATE` is not specified, it defaults to yesterday's date.

## Deploying to Tower

### Deploy the App

```bash
tower deploy
```

If the app does not yet exist, Tower will prompt you to create it.

### Run the App

To run on Tower cloud:

```bash
tower run --parameter=ANALYZE_DATE='2025-04-11'
```

Or without parameters to analyze yesterday's data:

```bash
tower run
```

## Monitoring

Check the app status and recent runs:

```bash
tower apps show analyze-ticker-data-in-iceberg
```

View logs for a specific run (note: quote the run ID because `#` is a special shell character):

```bash
tower apps logs "analyze-ticker-data-in-iceberg#1"
```

## Related Apps

- [05-write-ticker-data-to-iceberg](../05-write-ticker-data-to-iceberg) - Populates the `daily_ticker_data` table
- [13-ticker-update-agent](../13-ticker-update-agent) - AI agent for managing ticker data