import tower
from datetime import datetime, timedelta
import pyarrow as pa
import os


def main():
    pull_date_str = os.getenv("PULL_DATE", "")
    tickers_str = os.getenv("TICKERS", "")

    # Set pull_date_str to yesterday if empty
    if pull_date_str == "":
        pull_date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Exit if TICKERS parameter is not set
    if tickers_str == "":
        print("TICKERS parameter was not set")
        return

    ###
    # Step: Fan Out: Start the downloads of ticker data 
    #   for each ticker in parallel.
    ###

    ticker_list = [ticker.strip() for ticker in tickers_str.split(",")]
    
    # Process each ticker's data
    child_runs = []
    for ticker in ticker_list:

        params = {
            "PULL_DATE": f"{pull_date_str}",
            "TICKERS": f"{ticker}"
        }

        run = tower.run_app("write-ticker-data-to-iceberg", parameters=params)
        child_runs.append(run)

    ###
    # Step: Wait for all child runs to complete
    ###

    (successful_runs,unsuccessful_runs) = tower.wait_for_runs(child_runs)


    print(f"Successful ticker downloads: {len(successful_runs)}")
    print(f"Unsuccessful ticker downloads: {len(unsuccessful_runs)}")

if __name__ == "__main__":
    main()
