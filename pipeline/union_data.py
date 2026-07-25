#!/usr/bin/env python3
"""
Union all optimized export CSV files into a complete dataset.
"""

import os
import pandas as pd
import glob
from datetime import datetime

def union_export_data(data_dir="data", output_file="complete_export_matrix.csv"):
    """
    Union all optimized export CSV files into a single dataset.
    """
    print(f"[start] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Unioning export data")
    
    # Find all optimized export CSV files
    pattern = os.path.join(data_dir, "optimized_exports_*_XPRT-TRD-VL_*.csv")
    csv_files = glob.glob(pattern)
    
    if not csv_files:
        print(f"[error] No CSV files found matching pattern: {pattern}")
        return
    
    print(f"[found] {len(csv_files)} CSV files")
    
    # Read and union all CSV files
    all_dataframes = []
    total_rows = 0
    
    for csv_file in sorted(csv_files):
        try:
            df = pd.read_csv(csv_file)
            all_dataframes.append(df)
            total_rows += len(df)
            print(f"[loaded] {os.path.basename(csv_file)}: {len(df)} rows")
        except Exception as e:
            print(f"[error] Failed to load {csv_file}: {e}")
    
    if not all_dataframes:
        print("[error] No data loaded successfully")
        return
    
    # Union all dataframes
    print(f"[union] Combining {len(all_dataframes)} dataframes...")
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Sort by reporter, year, partner, product
    combined_df = combined_df.sort_values(['reporter', 'year', 'partner', 'product'])
    
    # Save combined dataset
    output_path = os.path.join(data_dir, output_file)
    combined_df.to_csv(output_path, index=False)
    
    # Generate summary statistics
    print(f"\n[SUMMARY] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total rows: {len(combined_df):,}")
    print(f"Unique reporters: {combined_df['reporter'].nunique()}")
    print(f"Unique partners: {combined_df['partner'].nunique()}")
    print(f"Unique products: {combined_df['product'].nunique()}")
    print(f"Year range: {combined_df['year'].min()}-{combined_df['year'].max()}")
    print(f"Output file: {output_path}")
    
    # Reporter breakdown
    print("\n[REPORTERS]")
    reporter_counts = combined_df['reporter'].value_counts().sort_index()
    for reporter, count in reporter_counts.items():
        print(f"  {reporter}: {count:,} rows")
    
    # Year breakdown
    print("\n[YEARS]")
    year_counts = combined_df['year'].value_counts().sort_index()
    for year, count in year_counts.items():
        print(f"  {year}: {count:,} rows")
    
    # Product breakdown
    print("\n[PRODUCTS]")
    product_counts = combined_df['product'].value_counts().sort_values(ascending=False)
    for product, count in product_counts.head(10).items():
        print(f"  {product}: {count:,} rows")
    
    return output_path

if __name__ == "__main__":
    union_export_data()
