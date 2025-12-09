import pandas as pd

def find_header_row(df, keywords=['성명', '이름']):
    """Find the row index containing any of the keywords"""
    for idx, row in df.iterrows():
        # Check if any cell in the row contains the keyword
        row_str = row.astype(str).values
        for keyword in keywords:
            if any(keyword in str(cell) for cell in row_str):
                return idx
    return -1

try:
    file_path = '2025출석부(목자용).xlsx'
    xls = pd.ExcelFile(file_path)
    
    # Target sheets: years 2019-2024 and '출석부' (2025)
    target_sheets = [s for s in xls.sheet_names if any(y in s for y in ['2019', '2020', '2021', '2022', '2023', '2024'])]
    if '출석부' in xls.sheet_names:
        target_sheets.append('출석부')
        
    print(f"Found sheets to check: {target_sheets}")
    
    for sheet_name in target_sheets:
        print(f"\nAnalyzing '{sheet_name}'...")
        # Read first 20 rows
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None, nrows=20)
        
        header_idx = find_header_row(df)
        if header_idx != -1:
            print(f"  -> Header found at row {header_idx}")
            # Show the header row
            print(f"  -> Header columns: {df.iloc[header_idx].tolist()[:10]} ...")
        else:
            print("  -> ⚠️ Header NOT found in first 20 rows")

except Exception as e:
    print(f"Error: {e}")
