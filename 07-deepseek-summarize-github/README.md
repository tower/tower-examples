# Learn from GitHub Issues with LLMs

This app demonstrates how to acquire data from external data sources and feed it into language models to extract insights. In this example we use the DeepSeek R1 model (or any other model) to analyze a GitHub issue and its comments, then proposes the best course of action to address the issue.

## Overview

The pipeline performs the following steps:
1. Fetches a GitHub issue and its comments using the GitHub API
2. Formats the thread as a conversation
3. Sends it to DeepSeek R1 for analysis and recommendations
4. Writes the results to an Iceberg table

This example demonstrates Tower's flexibility with inference providers:
- **Local development**: Use [ollama](https://ollama.com/) for free local inference on your GPU
- **Production**: Use serverless inference via Hugging Face Hub (e.g., Together.ai)


## App Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `gh_repo_owner` | Owner of the GitHub repository | `tower` |
| `gh_repo` | Name of the GitHub repository | `tower-cli` |
| `gh_issue_number` | Issue number to analyze | `11` |
| `model_to_use` | Model identifier (local or serverless) | `deepseek-ai/DeepSeek-R1` |
| `max_tokens` | Maximum output length in tokens | `1000` |

## Prerequisites

- Tower CLI installed
- An Iceberg catalog configured in Tower (named `default`)
- A Hugging Face account with an API token (for production)
- [ollama](https://ollama.com/) installed (for local development)

> **Note:** This example requires `dlt==1.4.0`. Newer versions of the dlt library have breaking changes in the custom destination API that are incompatible with this code.


### Sign Up for Hugging Face Hub

For production runs, you'll use Hugging Face Hub to route inference calls to providers like Together.ai:

1. [Sign up for Hugging Face](https://huggingface.co/join)
2. Get your [access token](https://huggingface.co/docs/hub/en/security-tokens)
3. Sign up for [Together.ai](https://www.together.ai/) and get your [API key](https://docs.together.ai/reference/authentication-1)
4. [Enable Together.ai in Hugging Face Hub](https://docs.together.ai/docs/quickstart-using-hugging-face-inference)

## Setup

### 1. Install Dependencies

```bash
cd 07-deepseek-summarize-github
uv sync
```

### 2. Install ollama (for Local Development)

Install ollama and pull a small DeepSeek R1 model:

```bash
pip install ollama
ollama pull deepseek-r1:14b
```

### 3. Configure an Iceberg Catalog

This app writes results to an Iceberg table, which requires an Iceberg catalog configured in Tower.

1. Go to [app.tower.dev](https://app.tower.dev/)
2. Navigate to your environment settings
3. Check if a catalog named `default` already exists; if not, create one

> **Note:** See the [Tower Iceberg catalog guide](https://docs.tower.dev/docs/concepts/environments#catalogs) for setup instructions.

### 4. Create the Secrets

Add your inference provider credentials as Tower secrets. Configure different settings for local development vs production:

**For local development (default environment)** - uses ollama:

```bash
tower secrets create --environment="default" \
  --name=TOWER_INFERENCE_ROUTER --value="ollama"
```

**For production (prod environment)** - uses Hugging Face Hub:

```bash
tower secrets create --environment="prod" \
  --name=TOWER_INFERENCE_ROUTER --value="hugging_face_hub"

tower secrets create --environment="prod" \
  --name=TOWER_INFERENCE_ROUTER_API_KEY --value="[YOUR_HF_TOKEN_HERE]"

tower secrets create --environment="prod" \
  --name=TOWER_INFERENCE_PROVIDER --value="together"
```

### 5. Run the Pipeline Locally

First, start ollama in a separate terminal:

```bash
ollama run deepseek-r1:14b
```

Then run the app in local mode (note: override `model_to_use` for ollama):

```bash
tower run --local --parameter=model_to_use='deepseek-r1:14b'
```

Or override more parameters as needed:

```bash
tower run --local \
  --parameter=model_to_use='deepseek-r1:14b' \
  --parameter=gh_repo_owner='dlt-hub' \
  --parameter=gh_repo='dlt' \
  --parameter=gh_issue_number=933
```

## Deploying to Tower

### Deploy the App

```bash
tower deploy
```

If the app does not yet exist, Tower will prompt you to create it.

### Run the App

To run on Tower cloud with serverless inference (uses prod environment):

```bash
tower run --environment="prod"
```

Or override parameters as needed:

```bash
tower run --environment="prod" \
  --parameter=gh_repo_owner='dlt-hub' \
  --parameter=gh_repo='dlt' \
  --parameter=gh_issue_number=933
```

## Monitoring

Check the app status and recent runs:

```bash
tower apps show deepseek-summarize-github
```

View logs for a specific run (note: quote the run ID because `#` is a special shell character):

```bash
tower apps logs "deepseek-summarize-github#1"
```

You can also use the [Tower web UI](https://app.tower.dev) to monitor your app runs.

## Troubleshooting

### ModuleNotFoundError: No module named 'core'

Add the current directory to your Python path:

```bash
export PYTHONPATH=.:$PYTHONPATH
```

### NotImplementedError on MPS device

If you're running local PyTorch inference on Apple Silicon and see:

```
NotImplementedError: The operator 'aten::isin.Tensor_Tensor_out' is not currently implemented for the MPS device.
```

Run this before executing the script:

```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

## Related Apps

- [06-analyze-ticker-data-in-iceberg](../06-analyze-ticker-data-in-iceberg) - Another example using LLM inference with Tower