# Data Agent for Stock Data Retrieval

This agent answers stock price questions and maintains a cache of prices in an Iceberg table.
If stock prices are not in cache, the agent will fetch them from Yahoo Finance and store in cache for future use.
The agent is based on the LangChain framework and can use local language models like Salesforce's xLAM-2 for local execution and any other type of LM for cloud execution.


# Environment Configuration

## Secrets

Following secrets need to be defined in the environment where this app is running:
* LANGCHAIN_API_KEY - see [docs](https://docs.smith.langchain.com/administration/how_to_guides/organization_management/create_account_api_key)

(Optional - when using any models remotely served by OpenAI):
* OPENAI_API_KEY - see [here](https://platform.openai.com/api-keys)

## Iceberg catalogs

This example expects an Iceberg catalog with the slug `default`
to be present in the environment where it is executed.

# Tower app dependencies

This app uses the "write-ticker-data-to-iceberg" app to acquire new daily ticker stats and populate the "daily_ticker_data" table. It needs to be deployed into the account where this app is going to run.

# Installing dependencies

Run this in the folder where pyproject.toml is located

```bash
uv sync
uv export --format=requirements-txt --no-hashes > requirements.txt
pip install -r requirements.txt --upgrade
```

# Login to Tower (optional)

If you haven't logged into Tower, or if you are getting "Error: fetching secrets failed" errors

```bash
tower login
```

# Install a local inference server (optional)

If you are planning to execute this agentic app locally, you should install an inference server (llama.cpp, ollama, vLLM or others).
We recommend llama.cpp

```bash
brew install llama.cpp
```

# Run a local inference server (optional) 

This agent can be run using different models depending on the available system memory. We recommend using the following versions depending on how much memory is available. 


| Model | Approx. RAM required | Recommended for |
|------|----------------------|-----------------|
| `bartowski/xLAM-7b-fc-r-GGUF` | ~6–8 GB | Laptops, local debugging |
| `Leepaper/xLAM-2-32b-fc-r-Q4_K_M-GGUF` | ~20–24 GB | Workstations, servers |

If the larger model does not fit in memory, use the smaller 7B model instead. To run either of these, use the following command in a new terminal and replace HF_MODEL_NAME with `bartowski/xLAM-7b-fc-r-GGUF` or 
`Leepaper/xLAM-2-32b-fc-r-Q4_K_M-GGUF`. 

```bash
llama-server \
    -hf HF_MODEL_NAME \
    --port 8080 \
	--jinja
```

# Run the app locally (optional)

To debug this app, you can run the app locally. 
You don't need to specify a name, the Tower CLI will figure out what app to run based on the Towerfile.

Replace "<TIC1,TIC2,...>" with a list of stock tickers, e.g. "AMZN,MSFT,ORCL".

Replace "< YYYY-MM-DD>" with a date when US stock exchanges were open (e.g. Mon-Fri, except banking holidays).

Replace HF_MODEL_NAME with the model you hosted above.

```bash
tower run --local \
--parameter=USER_INPUT="What was the stock price for each given ticker on a particular day?" \
--parameter=TICKERS="<TIC1,TIC2,...>" \
--parameter=PULL_DATE="<YYYY-MM-DD>" \
--parameter=MODEL_TO_USE="<HF_MODEL_NAME>" \
--parameter=INFERENCE_SERVER_BASE_URL="http://127.0.0.1:8080/v1"
```

# Deploy the app to Tower cloud

Tower uses a manifest file called Towerfile to figure out how to deploy your
app.  Use the following command from the folder where your Towerfile is

```bash
tower deploy
```

If the app does not yet exist, Tower will suggest creating it.

# Run the app in Tower cloud

To run the app in the Tower cloud, pick a model that you have access to. In the below example, we will use "gpt-4o-mini" served by OpenAI.

```bash
tower run \
--parameter=USER_INPUT="What was the stock price for each given ticker on a particular day?" \
--parameter=TICKERS="<TIC1,TIC2,...>" \
--parameter=PULL_DATE="<YYYY-MM-DD>" \
--parameter=MODEL_TO_USE="gpt-4o-mini"
```


