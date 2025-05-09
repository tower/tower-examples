# Get ticker data from Yahoo Finance and write to Iceberg

We use Yahoo Finance's public API and the [yfinance](https://github.com/ranaroussi/yfinance) library to download major indicators for a set of tickers, including Open, Close, and Volume. We save them in an Iceberg table.

# Schedule 

This app is supposed to be run on a schedule daily. The app is idempotent and can be re-run multiple times with the same parameters.

# App Dependencies

 The data this app acquires is used by the "analyze-ticker-data-in-iceberg" app to create sell/buy recommendations. This app is complemented by the "trim-ticker-table" app that cleans the "daily_ticker_data" table of old data. 

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
  --parameter=PULL_DATE="2025-05-01" \
  --parameter=TICKERS="MSFT,AAPL,AMZN,GOOGL,NVDA"
```

To run on Tower cloud, remove --local

## Check the run status

You can use the following command to see how the app is progressing. 

```bash
tower apps show write-ticker-data-to-iceberg
```

