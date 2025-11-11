# Tower dbt Core Ecommerce Analytics App

This example shows how to run a dbt Core project from a Tower app. It packages the `olist_dbt` project, remote seed hydration helpers (defaulting to Tower’s S3 archive), and a lightweight wrapper around `dbtRunner` so you can repurpose the workflow for your own dbt repository.

## How it works
- Seeds are hydrated from a zip archive before `dbt seed`. Tower’s environment defaults to `s3://tower-sandbox/olist_ecommerce_dataset/olist-seeds.zip` when no CSVs are present; override this by setting `DBT_SEED_ARCHIVE_URI`. If the `seeds/` folder already contains CSVs (e.g., you unzipped the [Kaggle Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerc)), the app skips the download.
- A runtime `profiles.yml` is written from the `DBT_PROFILE_YAML` secret.
- dbt commands (defaults: `deps`, `seed`, `build`) are executed via `dbtRunner` and the results are streamed to Tower logs.

## Parameters
| Name | Description | Default |
| ---- | ----------- | ------- |
| `DBT_COMMANDS` | Comma-separated dbt commands (flags allowed, e.g. `build --select tag:daily`). | `deps,seed,build` |
| `DBT_PROJECT_PATH` | Relative path to the dbt project root. | `dbt-project/olist_dbt` |
| `DBT_TARGET` | Target name from the profile (blank uses the profile default). | _empty_ |
| `DBT_SELECT` | Extra `--select` applied when commands don’t already include one. | _empty_ |
| `DBT_FULL_REFRESH` | `true` adds `--full-refresh` to run/build/seed (unless already provided). | `false` |

Advanced options like `DBT_THREADS` or `DBT_VARS_JSON` remain supported—set them with `tower run -p VAR=value` or bake them into your Towerfile.

### Required secret
- `DBT_PROFILE_YAML`: provide the full `profiles.yml` contents via `tower secrets set` so the app can render it at runtime.

## Local workflow
1. Ensure Python 3.11+ is available.
2. Install dependencies:
   ```bash
   uv venv
   uv sync
   ```
3. Export a profile for local testing:
   ```bash
   export DBT_PROFILE_YAML="$(cat dbt-project/olist_dbt/profiles.example.yml)"
   ```
4. Optional: hydrate seeds locally (e.g., unzip the Kaggle dataset into `dbt-project/olist_dbt/seeds`) or point the app at your own archive (if unset and no CSVs exist, the default S3 archive is used automatically):
   ```bash
   export DBT_SEED_ARCHIVE_URI="s3://my-bucket/path/to/seeds.zip"
   ```
5. Run the app:
   ```bash
   uv run python task.py
   ```

## Deploying to Tower
1. From this directory, deploy (creates the app if needed):
   ```bash
   tower deploy
   ```
2. Set the required secret:
   ```bash
   tower secrets create --name DBT_PROFILE_YAML --value "$(cat dbt-project/olist_dbt/profiles.example.yml)"
   ```
3. If Tower should pull seeds from a different location, set `DBT_SEED_ARCHIVE_URI` as a secret:
   ```bash
   tower secrets create --name DBT_SEED_ARCHIVE_URI --value "s3://my-bucket/path/to/seeds.zip"
   ```

## Running the Tower app
- Local run (executes with your workstation’s Python/dbt):
  ```bash
  tower run --local
  ```
- Cloud run (executes on Tower infrastructure):
  ```bash
  tower run
  ```

Monitor progress with:
```bash
tower apps show dbt-core-ecommerce-analytics
```