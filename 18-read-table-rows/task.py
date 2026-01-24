"""
Tower Example: Read First N Rows from an Iceberg Table

This app reads the first N rows from a specified Iceberg table and displays
them using Polars. The table and number of rows are configurable via parameters.
"""

import tower
import polars as pl
import os


def main():
    # Get parameters from environment
    catalog_name = os.getenv("CATALOG_NAME", "default")
    namespace = os.getenv("NAMESPACE", "default")
    table_name = os.getenv("TABLE_NAME", "daily_ticker_data")
    num_rows = int(os.getenv("NUM_ROWS", "10"))
    
    print("=" * 60)
    print("📊 READ TABLE ROWS")
    print("=" * 60)
    print(f"Catalog: {catalog_name}")
    print(f"Table: {namespace}.{table_name}")
    print(f"Rows to fetch: {num_rows}")
    print("=" * 60)
    
    # Load the table using Tower tables SDK
    try:
        if namespace and namespace != "default":
            df = tower.tables(table_name, namespace=namespace, catalog=catalog_name).load().read()
        else:
            df = tower.tables(table_name, catalog=catalog_name).load().read()
    except Exception as e:
        print(f"\n❌ Error loading table: {e}")
        print("\nMake sure:")
        print(f"  1. The table '{table_name}' exists in namespace '{namespace}'")
        print(f"  2. The catalog '{catalog_name}' is configured in your Tower environment")
        print("  3. Run 'tower run --local --environment=<env>' with the right environment")
        return
    
    total_rows = len(df)
    print(f"\n✓ Table loaded successfully")
    print(f"  Total rows in table: {total_rows}")
    
    # Get the first N rows
    result_df = df.head(num_rows)
    actual_rows = len(result_df)
    
    print(f"  Rows returned: {actual_rows}")
    
    # Display schema
    print(f"\n📋 SCHEMA ({len(df.columns)} columns)")
    print("-" * 40)
    for col_name, col_type in df.schema.items():
        print(f"  {col_name}: {col_type}")
    
    # Display the data
    print(f"\n📄 DATA (first {actual_rows} rows)")
    print("-" * 40)
    
    # Configure Polars display options for better output
    with pl.Config(
        tbl_rows=num_rows,
        tbl_cols=20,
        fmt_str_lengths=50,
        tbl_width_chars=120
    ):
        print(result_df)
    
    print("\n" + "=" * 60)
    print("✓ Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
