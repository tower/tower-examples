import tower
import polars as pl
from datetime import datetime, timedelta
import pyarrow as pa
import yfinance as yf
import os



def get_ticker_data(tickers: str, pull_date_str: str) -> pa.Table:
    """
    Download stock data for specific tickers and date from Yahoo Finance.
    
    Args:
        tickers: List of stock ticker symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])
        date: Date string in YYYY-MM-DD format
        
    Returns:
        Arrow Table with columns: ticker, date, open, close, volume
    """
    # Convert date string to datetime
    pull_date = datetime.strptime(pull_date_str, "%Y-%m-%d")
    next_day = pull_date + timedelta(days=1)
    next_day_str = next_day.strftime("%Y-%m-%d")
    
    # Download data for all tickers
    data = yf.download(
        tickers,
        start=pull_date_str,
        end=next_day_str,
        group_by='ticker'
    )
    
    # Initialize empty list to store rows
    rows = []
    ticker_list = [ticker.strip() for ticker in tickers.split(",")]
    
    # Process each ticker's data
    for ticker in ticker_list:
        if ticker in data.columns.levels[0]:
            ticker_data = data[ticker]
            if not ticker_data.empty:
                rows.append({
                    'ticker': ticker,
                    'date': pull_date_str,
                    'open': ticker_data['Open'].iloc[0],
                    'close': ticker_data['Close'].iloc[0],
                    'volume': ticker_data['Volume'].iloc[0]
                })
    
    # Create Polars DataFrame
    return pa.Table.from_pylist(rows)



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
    # Step 1: Download ticker data from Yahoo Finance 
    #   and store into an Arrow Table
    ###

    data = get_ticker_data(tickers_str,pull_date_str)


    ###
    # Step 2: Get a reference to the table in Tower. 
    #   If it doesn't exist, create it.
    ###

    SCHEMA = pa.schema([
        ("ticker", pa.string()),
        ("date", pa.string()),
        ("open", pa.float64()),
        ("close", pa.float64()),
        ("volume", pa.int64()),
    ])

    table = tower.tables("daily_ticker_data").create_if_not_exists(SCHEMA)
    
  
    ###
    # Step 3: Upsert new stats into the table. 
    #   Use Upsert to make the pipeline idempotent.
    ###
    table = table.upsert(data,join_cols=['ticker','date'])
    #table.insert(data)

 
if __name__ == "__main__":
    main()
