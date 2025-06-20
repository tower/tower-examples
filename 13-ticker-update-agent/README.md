# Use an Agent to maintain ticker data in an Iceberg table

This agent is based on the LangChain framework and 
maintains ticker data (open/close prices and volume) for a list of tickers.

Before getting the stock data from Yahoo Finance, 
it checks if the data is already available.

# Environment Configuration

## Secrets

Following secrets need to be defined in Tower

* LANGCHAIN_API_KEY - see [docs](https://docs.smith.langchain.com/administration/how_to_guides/organization_management/create_account_api_key)
* OPENAI_API_KEY - see [here](https://platform.openai.com/api-keys)

## Iceberg catalogs

This example expects an Iceberg catalog with the slug `default`
to be present in the environment where it is executed.


# Tower App Dependencies

This agentic app uses the "write-ticker-data-to-iceberg" app that 
acquires new daily ticker stats and populates the "daily_ticker_data" table. 

This app is idempotent and can be re-run multiple times with the same parameters.


# Deploying app to Tower cloud

Tower uses a manifest file called Towerfile to figure out how to deploy your
app. Review the Towerfile, deploy the code, create secrets or catalogs, and run the app!

## Creating and deploying the app

Use the following command from the folder where your Towerfile is

```bash
tower deploy
```

If the app does not yet exist, Tower will suggest creating it.

## Running the app

You can run the app using the Tower CLI. You don't need to specify a name, it
will figure out what app to run based on the Towerfile.

To run locally

```bash
tower run --local
```

To run on Tower cloud, remove --local

## Check the run status

You can use the following command to see how the app is progressing. 

```bash
tower apps show <app-name>
```

