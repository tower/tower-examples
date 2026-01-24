"""
Tower Example: List Tables in an Iceberg Catalog

This app connects to a Tower Iceberg catalog and lists all namespaces
and tables within it, using the same catalog loading mechanism as Tower.
"""

import os
from pyiceberg.catalog import load_catalog


def list_catalog_contents(catalog_name: str = "default"):
    """
    Connect to a Tower Iceberg catalog and list all namespaces and tables.
    
    Args:
        catalog_name: The name of the Tower catalog to connect to
    """
    print(f"Connecting to catalog: {catalog_name}")
    print("=" * 60)
    
    # Load the catalog using PyIceberg's load_catalog
    # Tower sets up the required environment variables (PYICEBERG_CATALOG__*)
    # when running through `tower run`
    try:
        catalog = load_catalog(catalog_name)
    except Exception as e:
        print(f"Error loading catalog '{catalog_name}': {e}")
        print("\nMake sure you have a catalog configured in Tower:")
        print("  tower catalogs list")
        print("  tower catalogs create default")
        return
    
    print(f"Catalog type: {type(catalog).__name__}")
    
    # List all namespaces
    print("\n📁 NAMESPACES")
    print("-" * 40)
    
    try:
        namespaces = catalog.list_namespaces()
        
        if not namespaces:
            print("  (no namespaces found)")
        else:
            for ns in namespaces:
                namespace_name = ".".join(ns) if isinstance(ns, tuple) else str(ns)
                print(f"  • {namespace_name}")
        
        # List tables in each namespace
        print("\n📊 TABLES BY NAMESPACE")
        print("-" * 40)
        
        total_tables = 0
        
        for ns in namespaces:
            namespace_name = ".".join(ns) if isinstance(ns, tuple) else str(ns)
            
            try:
                tables = catalog.list_tables(ns)
                
                if tables:
                    print(f"\n  [{namespace_name}]")
                    for table_id in tables:
                        table_name = table_id.name if hasattr(table_id, 'name') else str(table_id[-1]) if isinstance(table_id, tuple) else str(table_id)
                        print(f"    └─ {table_name}")
                        total_tables += 1
                        
                        # Optionally show table details
                        show_details = os.environ.get("SHOW_DETAILS", "false").lower() == "true"
                        if show_details:
                            try:
                                table = catalog.load_table(table_id)
                                schema = table.schema()
                                print(f"       Schema: {len(schema.fields)} columns")
                                for field in schema.fields[:5]:  # Show first 5 columns
                                    print(f"         - {field.name}: {field.field_type}")
                                if len(schema.fields) > 5:
                                    print(f"         ... and {len(schema.fields) - 5} more columns")
                            except Exception as e:
                                print(f"       (could not load schema: {e})")
                else:
                    print(f"\n  [{namespace_name}]")
                    print("    (no tables)")
                                
            except Exception as e:
                print(f"\n  [{namespace_name}]")
                print(f"    (error listing tables: {e})")
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📈 SUMMARY")
        print(f"   Namespaces: {len(namespaces)}")
        print(f"   Total Tables: {total_tables}")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error listing catalog contents: {e}")
        raise


def main():
    catalog_name = os.environ.get("CATALOG_NAME", "default")
    list_catalog_contents(catalog_name)


if __name__ == "__main__":
    main()
