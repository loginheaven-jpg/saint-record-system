import pandas as pd

try:
    file_path = '2025출석부(목자용).xlsx'
    xls = pd.ExcelFile(file_path)
    
    if '2024년' in xls.sheet_names:
        print("--- 2024년 Sheet Head ---")
        df = pd.read_excel(xls, sheet_name='2024년', header=None, nrows=10)
        print(df.to_string())
    else:
        print("Sheet '2024년' not found. Available:", xls.sheet_names)

except Exception as e:
    print(f"Error: {e}")
