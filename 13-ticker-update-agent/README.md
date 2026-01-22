# Ticker Update Agent

This example demonstrates how to deploy and operate a data agent that uses business data for decision making. It creates an AI data agent that answers stock price questions and maintains a cache of prices in an Iceberg table.

## Overview

This agent uses a data set of stock info (stored in Iceberg) to answer questions about stock prices. If stock information is not in that data set, the agent fetches it from Yahoo Finance and stores it for future use. The agent can run with:

- **Local inference** - Using llama.cpp or ollama with models like xLAM-2
- **Cloud inference** - Using OpenAI, DeepSeek, or other providers

The agent demonstrates how to build **agentic workflows** in Tower that can orchestrate other Tower apps.

## App Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `USER_INPUT` | The user query to the agent | `What was the stock price for each given ticker on a particular day?` |
| `TICKERS` | Comma-separated list of stock tickers | `NVDA` |
| `PULL_DATE` | Date to pull stock data (YYYY-MM-DD) | `2025-06-17` |
| `MODEL_TO_USE` | Name of the LLM model to use | `deepseek-ai/DeepSeek-R1` |
| `INFERENCE_SERVER_BASE_URL` | Base URL of local inference server (leave empty for cloud) | `` |

## Prerequisites

- Tower CLI installed
- An Iceberg catalog configured in Tower (see setup below)
- The `daily_ticker_data` table exists (created by example 05)
- The `write-ticker-data-to-iceberg` app deployed (example 05)

## Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Create Secrets

**Required:**

```bash
tower secrets create LANGCHAIN_API_KEY "<your-langchain-api-key>"
```

> Get your LangChain API key from [LangSmith](https://docs.smith.langchain.com/administration/how_to_guides/organization_management/create_account_api_key)

**Optional (for OpenAI models):**

```bash
tower secrets create OPENAI_API_KEY "<your-openai-api-key>"
```

### 3. Configure an Iceberg Catalog

This app reads from and writes to an Iceberg table, which requires an Iceberg catalog configured in Tower.

1. Go to [app.tower.dev](https://app.tower.dev/)
2. Navigate to your environment settings
3. Check if a catalog named `default` already exists; if not, create one

> **Note:** This app expects a catalog with the name `default`. See the [Tower Iceberg catalog guide](https://docs.tower.dev/docs/concepts/environments#catalogs) for setup instructions.

### 4. Deploy the Dependency App

This agent calls the `write-ticker-data-to-iceberg` app to fetch missing data. Make sure it's deployed:

```bash
cd ../05-write-ticker-data-to-iceberg
tower deploy
cd ../13-ticker-update-agent
```

### 5. Set Up Local Inference (Optional)

If running locally, install an inference server. We recommend llama.cpp:

```bash
brew install llama.cpp
```

Start the server with a model that fits your system:

| Model | RAM Required | Recommended For |
|-------|--------------|-----------------|
| `bartowski/xLAM-7b-fc-r-GGUF` | ~6–8 GB | Laptops, local debugging |
| `Leepaper/xLAM-2-32b-fc-r-Q4_K_M-GGUF` | ~20–24 GB | Workstations, servers |

```bash
llama-server \
    -hf Leepaper/xLAM-2-32b-fc-r-Q4_K_M-GGUF \
    --port 8080 \
    --jinja
```

### 6. Run the Agent Locally

**With local inference:**

```bash
tower run --local \
  --parameter=TICKERS="AMZN,MSFT" \
  --parameter=PULL_DATE="2025-01-15" \
  --parameter=MODEL_TO_USE="Leepaper/xLAM-2-32b-fc-r-Q4_K_M-GGUF" \
  --parameter=INFERENCE_SERVER_BASE_URL="http://127.0.0.1:8080/v1"
```

**With cloud inference (requires OPENAI_API_KEY):**

```bash
tower run --local \
  --parameter=TICKERS="AMZN,MSFT" \
  --parameter=PULL_DATE="2025-01-15" \
  --parameter=MODEL_TO_USE="gpt-4o-mini"
```

## Deploying to Tower

### 1. Deploy the App

```bash
tower deploy
```

If the app doesn't exist, Tower will prompt you to create it.

### 2. Run the App

**Run on Tower cloud with defaults:**

```bash
tower run
```

**Run with custom parameters:**

```bash
tower run \
  --parameter=TICKERS="AAPL,GOOGL,NFLX" \
  --parameter=PULL_DATE="2025-01-15" \
  --parameter=MODEL_TO_USE="gpt-4o-mini"
```

## Monitoring

### Check Run Status

```bash
tower apps show ticker-update-agent
```

### View Run Logs

```bash
tower apps logs "ticker-update-agent#1"
```

## How It Works

This agent uses a **reasoning loop** powered by a language model specialized in tool calling (such as xLAM or GPT-4). The LLM reasons about each step and decides which tool to invoke:

1. The agent receives a list of tickers and a date as input
2. For each ticker, the LLM reasons whether data might already be cached
3. It calls the `check_if_ticker_data_is_already_available` tool to query the Iceberg table
4. If data exists, the agent extracts the price and moves to the next ticker
5. If data is missing, the LLM reasons that it needs to fetch from an external source
6. It calls the `fetch_and_store_data_for_ticker_into_database` tool, which triggers the `write-ticker-data-to-iceberg` app
7. After processing all tickers, the agent summarizes the results

This **agentic approach** lets the LLM dynamically decide the best path for each ticker, minimizing external API calls by leveraging cached data when available.

## Troubleshooting

### "Error: fetching secrets failed"

Make sure you're logged in:

```bash
tower login
```

### Agent stops without processing all tickers

The agent has a maximum of 10 iterations. For many tickers, consider running multiple times or adjusting the `max_iterations` in `agent.py`.

### Local inference model doesn't fit in memory

Use the smaller 7B model instead of the 32B model.

## Related Apps

This app is part of a ticker data project:

- **05-write-ticker-data-to-iceberg** - Acquires daily ticker data from Yahoo Finance
- **06-analyze-ticker-data-in-iceberg** - Creates buy/sell recommendations from the data
- **11-trim-ticker-table** - Cleans old data from the table
- **13-ticker-update-agent** (this app) - AI agent that answers stock price questions using cached data