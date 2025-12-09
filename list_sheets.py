import pandas as pd

try:
    file_path = '2025출석부(목자용).xlsx'
    xls = pd.ExcelFile(file_path)
    print("--- All Sheet Names ---")
    for i, name in enumerate(xls.sheet_names):
        print(f"{i}: {name}")
        
    print("\n--- Checking for Year-like sheets ---")
    for name in xls.sheet_names:
        if any(year in name for year in ['2019', '2020', '2021', '2022', '2023', '2024']):
            print(f"\nScanning Sheet: {name}")
            try:
                df = pd.read_excel(xls, sheet_name=name, nrows=5)
                print(df.columns.tolist())
            except Exception as e:
                print(f"Error reading {name}: {e}")

except Exception as e:
    print(f"Error: {e}")
