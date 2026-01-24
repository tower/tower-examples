"""
Fetches daily stock data (prices and volume) from Yahoo Finance
for top 100 NYSE stocks and stores in Tower lakehouse table.
"""

import os
import tower
import yfinance as yf
import pyarrow as pa
from datetime import datetime, timedelta


# Top 100 NYSE stocks by market cap (as of 2024)
TOP_100_NYSE_TICKERS = [
    # Technology & Communications
    "AAPL", "MSFT", "GOOGL", "GOOG", "META", "NVDA", "ORCL", "IBM", "CRM", "CSCO",
    "INTC", "AMD", "QCOM", "TXN", "AVGO", "NOW", "ADBE", "ACN", "INTU", "AMAT",
    # Financial Services
    "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP", "BLK",
    "C", "SCHW", "USB", "PNC", "TFC", "COF", "BK", "CME", "ICE", "SPGI",
    # Healthcare & Pharmaceuticals
    "UNH", "JNJ", "LLY", "PFE", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY",
    "AMGN", "MDT", "ISRG", "GILD", "CVS", "CI", "ELV", "HUM", "SYK", "ZTS",
    # Consumer & Retail
    "AMZN", "HD", "WMT", "MCD", "NKE", "SBUX", "TGT", "LOW", "COST", "TJX",
    "DG", "DLTR", "ORLY", "AZO", "ROST", "YUM", "CMG", "DPZ", "KO", "PEP",
    # Energy & Industrials
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
    "CAT", "DE", "UNP", "UPS", "HON", "GE", "RTX", "BA", "LMT", "MMM",
]


def get_stock_data(tickers: list[str], pull_date: datetime) -> pa.Table:
    """
    Download stock data from Yahoo Finance for given tickers and date.

    Args:
        tickers: List of stock ticker symbols
        pull_date: Date to fetch data for

    Returns:
        PyArrow Table with stock data
    """
    end_date = pull_date + timedelta(days=1)

    print(f"Fetching data for {len(tickers)} tickers from {pull_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Download data from Yahoo Finance
    # Using group_by='ticker' to handle multiple tickers
    data = yf.download(
        tickers,
        start=pull_date,
        end=end_date,
        group_by='ticker',
        progress=False
    )

    if data.empty:
        print("No data returned from Yahoo Finance")
        return pa.Table.from_pylist([])

    # Transform to list of records for PyArrow
    rows = []

    for ticker in tickers:
        try:
            if len(tickers) == 1:
                # Single ticker returns flat DataFrame
                ticker_data = data
            else:
                # Multiple tickers returns multi-level columns
                if ticker not in data.columns.levels[0]:
                    print(f"No data for ticker: {ticker}")
                    continue
                ticker_data = data[ticker]

            if ticker_data.empty:
                print(f"Empty data for ticker: {ticker}")
                continue

            for date_idx, row in ticker_data.iterrows():
                # Skip rows with NaN values in core columns
                core_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                if any(row[col] != row[col] for col in core_cols if col in row.index):  # NaN check
                    continue

                # Handle both old and new yfinance column names for adjusted close
                adj_close_col = 'Adjusted Close' if 'Adjusted Close' in row.index else 'Adj Close'
                adj_close_val = float(row[adj_close_col]) if adj_close_col in row.index else float(row['Close'])

                rows.append({
                    'ticker': ticker,
                    'date': date_idx.strftime("%Y-%m-%d"),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'adj_close': adj_close_val,
                    'volume': int(row['Volume'])
                })
        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")
            continue

    print(f"Successfully processed {len(rows)} records")
    return pa.Table.from_pylist(rows)


def main():
    """Main entry point for the Tower app."""

    # Get parameters from environment
    pull_date_str = os.getenv("PULL_DATE", "")
    tickers_override = os.getenv("TICKERS", "")

    # Default to yesterday if no date specified
    if pull_date_str == "":
        pull_date = datetime.now() - timedelta(days=1)
    else:
        pull_date = datetime.strptime(pull_date_str, "%Y-%m-%d")

    # Use override tickers if provided, otherwise use top 100
    if tickers_override:
        tickers = [t.strip() for t in tickers_override.split(",")]
        print(f"Using custom ticker list: {len(tickers)} tickers")
    else:
        tickers = TOP_100_NYSE_TICKERS
        print(f"Using default top 100 NYSE tickers")

    print(f"Pull date: {pull_date.strftime('%Y-%m-%d')}")

    # Fetch stock data from Yahoo Finance
    data = get_stock_data(tickers, pull_date)

    if data.num_rows == 0:
        print("No data to store. This may be a non-trading day (weekend/holiday).")
        return

    # Define schema for the lakehouse table
    SCHEMA = pa.schema([
        ("ticker", pa.string()),
        ("date", pa.string()),
        ("open", pa.float64()),
        ("high", pa.float64()),
        ("low", pa.float64()),
        ("close", pa.float64()),
        ("adj_close", pa.float64()),
        ("volume", pa.int64()),
    ])

    # Get or create the table
    table_name = "nyse_top100_daily"
    print(f"Writing {data.num_rows} records to table: {table_name}")

    table = tower.tables(table_name).create_if_not_exists(SCHEMA)

    # Upsert data (idempotent - safe to re-run)
    table.upsert(data, join_cols=['ticker', 'date'])

    print(f"Successfully stored data in {table_name}")


if __name__ == "__main__":
    main()
