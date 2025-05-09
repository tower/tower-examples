import tower
import polars as pl
from datetime import datetime, timedelta
import pyarrow as pa
import pyarrow.compute as pc
import os



def calculate_cutoff_date(df: pl.LazyFrame, time_window_days: int) -> str:
    """
    Calculate the cutoff date for trimming the table.
    
    Args:
        df: Polars LazyFrame containing the data
        time_window_days: Number of days of data to keep
        
    Returns:
        String representation of the cutoff date in YYYY-MM-DD format
    """
    max_date = df.select(pl.col("date").str.to_date().max()).collect().item()
    cutoff_date = max_date - timedelta(days=time_window_days)
    return cutoff_date.strftime("%Y-%m-%d")

def main():
    """
    Trim the table to have at most NN days of ticker data
    """

    time_window_days_str = os.getenv("TIME_WINDOW_DAYS", "31")
    time_window_days = int(time_window_days_str)

    ###
    # Step 1: Get a reference to the table in Tower.
    #   We will use it for reads and writes.
    ###

    table = tower.tables("daily_ticker_data").load()


    ###
    # Step 2: Get a LazyFrame of the data in the table. 
    #   Don't load it yet to memory.
    ###

    df = table.to_polars()

    ###
    # Step 3: Calculate stats per ticker before trimming the table
    ###

    ticker_stats = df.group_by("ticker").agg([
        pl.count().alias("row_count"),
        pl.col("date").str.to_date().max().alias("latest_date")
    ]).collect()    

    # Print the stats with a descriptive header
    print("\nTicker Statistics Before Trimming:")
    print(ticker_stats)

    ###
    # Step 4: Trim the table: remove all records older than the time window
    ###

    cutoff_date_str = calculate_cutoff_date(df, time_window_days)

    # Delete records older than the cutoff date
    table.delete(f"date < '{cutoff_date_str}'")

    # Print confirmation
    print(f"\nDeleted records older than {cutoff_date_str}")


if __name__ == "__main__":
    main()
