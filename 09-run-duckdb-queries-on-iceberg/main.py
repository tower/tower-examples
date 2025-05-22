import os
import duckdb

IRC_CLIENT_ID = os.getenv("IRC_CLIENT_ID")
IRC_CLIENT_SECRET = os.getenv("IRC_CLIENT_SECRET")
IRC_ENDPOINT = os.getenv("IRC_ENDPOINT")

def main():
    # Setup DuckDB extensions for talking to Tower
    duckdb.sql("LOAD iceberg;")
    duckdb.sql("INSTALL httpfs;")
    duckdb.sql("LOAD httpfs;")

    # Setup the connection to the Iceberg catalog (passed in as secrets)
    duckdb.sql(f"""CREATE SECRET (
     TYPE ICEBERG,
     CLIENT_ID '{IRC_CLIENT_ID}',
     CLIENT_SECRET '{IRC_CLIENT_SECRET}',
     ENDPOINT '{IRC_ENDPOINT}'
);""")

    duckdb.sql("ATTACH 'tower-demo-lakehouse' AS tower_demo_lakehouse (TYPE ICEBERG);")
    duckdb.sql("SELECT * FROM tower_demo_lakehouse.default.daily_ticker_data LIMIT 10;").show()


if __name__ == "__main__":
    main()
