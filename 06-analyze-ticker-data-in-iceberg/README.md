# Make buy/sell recommendations for stocks using LLMs and ticker data in Iceberg tables

This app uses the Deepseek R1 LLM to come up with buy/sell recommendations based on trends in stock prices and sale volume. The data for stocks is taken from the "daily_ticker_data" Iceberg table, which, in turn, is populated from the Yahoo Finance API.  

# Schedule 

This app is supposed to be run on a schedule daily. The app is idempotent and can be re-run multiple times with the same parameters.

# App Dependencies

This app takes its data from the "daily_ticker_data" table, which is populated by the "write-ticker-data-to-iceberg" app. 

# Deploying app to Tower cloud

Tower uses a manifest file called Towerfile to figure out how to deploy your
app. Review the Towerfile, deploy the code, create secrets or catalogs, and run the app!

## Creating and deploying the app

Use the following command from the folder where your Towerfile is

```bash
tower deploy
```

If the app does not yet exist, Tower will suggest creating it.

## Defining an Iceberg catalog

You need to tell us about your Iceberg catalog in the [Tower UI](https://app.tower.dev). 
Use the catalog slug `default` as that's what this sample app expects it to be called.

## Running the app

You can run the app using the Tower CLI. You don't need to specify a name, it
will figure out what app to run based on the Towerfile.

To run locally

```bash
tower run --local \
 --parameter=ANALYZE_DATE='2025-04-11'
```

To run on Tower cloud, remove --local

## Check the run status

You can use the following command to see how the app is progressing. 

```bash
tower apps show analyze-ticker-data-in-iceberg
```

