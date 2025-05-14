import tower
import polars as pl
from datetime import datetime, timedelta
# We need the OS package to get parameters from the environment.
import os

# 
# These are a few helper functions to help with the overall analysis of data.
#
def add_trend_column(df: pl.DataFrame) -> pl.DataFrame:
    """
    `add_trend_column` is a helper function that does a linear regression to
    understand the overall trend in the past 30 days of the data within the
    DataFrame.

    Args:
        df (pl.DataFrame): The input DataFrame containing stock data.

    Returns:
        pl.DataFrame: The DataFrame with an additional column for the trend.
    """
    import numpy as np
    from sklearn.linear_model import LinearRegression

    def compute_trend(prices):
        if len(prices) < 2:
            return np.nan
        x = np.arange(len(prices)).reshape(-1, 1)
        y = np.array(prices).reshape(-1, 1)
        model = LinearRegression().fit(x, y)
        return model.coef_[0][0]

    result = []

    for ticker, group_df in df.group_by("ticker", maintain_order=True):
        closes = group_df["close"].to_list()
        trends = [None] * 29  # First 29 days have no trend

        for i in range(29, len(closes)):
            window = closes[i-29:i+1]
            slope = compute_trend(window)
            trends.append(slope)

        group_df = group_df.with_columns(pl.Series("trend_30", trends))
        result.append(group_df)

    return pl.concat(result)

def analyze_dataframe(df: pl.DataFrame) -> pl.DataFrame:
    """
    `analyze_dataframe` is a function that processes a DataFrame containing
    stock data in the format of ticker, date, open price, close price, and
    volume and computes a 7-day and a 30-day moving average, as well as a
    volatility score and an overall trend score.

    Args:
        df (pl.DataFrame): The input DataFrame containing stock data.

    Returns:
        pl.DataFrame: The processed DataFrame with additional columns for
        moving averages, volatility, and trend.
    """
    df = df.with_columns(
        pl.col("date").str.to_date()
    )

    # Ensure proper date types and sort
    df = df.sort(["ticker", "date"])

    # Calculate moving averages and volatility using group_by().over()
    df = df.with_columns([
        pl.col("close")
            .rolling_mean(window_size=7)
            .over("ticker")
            .alias("ma_7"),
        pl.col("close")
            .rolling_mean(window_size=30)
            .over("ticker")
            .alias("ma_30"),
        pl.col("close")
            .rolling_std(window_size=30)
            .over("ticker")
            .alias("volatility_30"),
    ])

    # Add in the trend column 
    df = add_trend_column(df)

    return df
#
# END analysis functions
#

def main():
    analyze_date_str = os.getenv("ANALYZE_DATE", "")

    # Set analyze_date_str to yesterday if empty
    if analyze_date_str == "":
        analyze_date = (datetime.now() - timedelta(days=1))
        analyze_date_str = analyze_date.strftime("%Y-%m-%d")
    else:
        analyze_date = datetime.strptime(analyze_date_str, "%Y-%m-%d")

    ###
    #
    # Step 1: Load the Iceberg table into a Polars DataFrame.
    #
    ###
    df = tower.tables("daily_ticker_data").load().read()

    ###
    #
    # Step 2: Analyze the Polars DataFrame accordingly.
    #
    ###
    df = analyze_dataframe(df)

    df = df.filter(pl.col("date") == analyze_date)

    # This is the final DataFrame with the analysis fully applied. We output it
    # so we can see what's going on.
    print(df)

    ###
    #
    # Step 3: Generate a summary of the analysis and recommendations for how to
    #   invest (or divest) accordingly. We'll use Deepseek R1 to do this.
    #
    ###
    summaries = [
        f"Ticker: {r['ticker']}, "
        f"7-day avg: {r['ma_7']}, "
        f"30-day avg: {r['ma_30']}, "
        f"30-day volatility: {r['volatility_30']}, "
        f"30-day trend: {r['trend_30']}"
        for r in df.iter_rows(named=True)
    ]

    prompt = f"""\
I'm going to give you some stock tickers with some associated volatility data.
Which of them would you recommend buying, holding, or selling? {summaries}"
    """

    # Ship the results off to the LLM for analysis.
    result = tower.llms("deepseek-r1").prompt(prompt)

    print(result)

if __name__ == "__main__":
    main()
