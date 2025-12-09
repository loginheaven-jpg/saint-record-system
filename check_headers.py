import pandas as pd

try:
    file_path = '2025출석부(목자용).xlsx'
    xls = pd.ExcelFile(file_path)
    print(f"Sheet names: {xls.sheet_names}")
    
    # Check '시트11' specifically for headers
    if '시트11' in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name='시트11', header=None, nrows=10)
        print("\n--- Sheet: 시트11 (First 10 rows) ---")
        print(df.to_string())
        
except Exception as e:
    print(f"Error: {e}")
