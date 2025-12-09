import pandas as pd
import sys

try:
    file_path = '2025출석부(목자용).xlsx'
    xls = pd.ExcelFile(file_path)
    print(f"Sheet names: {xls.sheet_names}")
    
    for sheet_name in xls.sheet_names:
        print(f"\n--- Sheet: {sheet_name} ---")
        df = pd.read_excel(xls, sheet_name=sheet_name, nrows=5)
        print(df.to_string())
except Exception as e:
    print(f"Error: {e}")
