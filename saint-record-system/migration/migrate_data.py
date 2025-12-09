import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.enums import AttendType

class DataMigrator:
    def __init__(self, excel_path: str, credentials_path: str = None):
        self.excel_path = excel_path
        
        # Check multiple locations for credentials
        base_dir = os.path.dirname(os.path.abspath(__file__)) # .../saint-record-system/migration
        root_dir = os.path.dirname(os.path.dirname(base_dir)) # .../#yebom
        
        possible_paths = [
            credentials_path,
            os.path.join(base_dir, '..', 'credentials', 'credentials.json'), # saint-record-system/credentials
            os.path.join(root_dir, 'credentials', 'credentials.json'),       # #yebom/credentials
        ]
        
        self.credentials_path = None
        for path in possible_paths:
            if path and os.path.exists(path):
                self.credentials_path = path
                break
        
        if not self.credentials_path:
             # Fallback to default for error message
             self.credentials_path = os.path.join(root_dir, 'credentials', 'credentials.json')

        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.client = None
        self.spreadsheet = None
        self.errors = []
        
        self.sheet_name = '성도기록부_시스템'

    def connect(self):
        """Google Sheets 연결"""
        try:
            if not os.path.exists(self.credentials_path):
                print(f"Error: Credentials file not found at {self.credentials_path}")
                return False
                
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path, self.scope
            )
            self.client = gspread.authorize(creds)
            
            try:
                # self.spreadsheet = self.client.open(self.sheet_name)
                # Use provided Sheet ID
                sheet_id = '1cDfZiWbbpV8Z9NwAauG3SAriarJ1HL9xXMkZMJhC5Jo'
                self.spreadsheet = self.client.open_by_key(sheet_id)
            except gspread.SpreadsheetNotFound:
                print(f"Spreadsheet with ID '{sheet_id}' not found. Please check permissions.")
                return False
                
            print("Successfully connected to Google Sheets")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def migrate_all(self):
        if not self.connect():
            return

        print("Starting Migration...")
        
        # Step 1: 시스템 시트 생성
        print("\n[Step 1] Creating System Sheets...")
        self.create_sequences_sheet()
        self.create_departments_sheet()
        
        # Step 2: 성도 데이터
        print("\n[Step 2] Migrating Members...")
        member_count = self.migrate_members()
        print(f"  - Migrated {member_count} members")
        
        # Step 3: 과거 출석 데이터 (2019-2024)
        print("\n[Step 3] Migrating Historical Attendance (2019-2024)...")
        hist_count = self.migrate_historical_attendance()
        print(f"  - Migrated {hist_count} historical records")

        # Step 4: 현재 출석 데이터 (2025)
        print("\n[Step 4] Migrating Current Attendance (2025)...")
        curr_count = self.migrate_current_attendance()
        print(f"  - Migrated {curr_count} current records")
        
        # Step 5: 검증
        print("\n[Step 5] Validating...")
        self.validate_all()
        
        print("\n=== Migration Completed ===")
        if self.errors:
            print(f"\n⚠️ {len(self.errors)} errors occurred:")
            for err in self.errors[:10]:
                print(f"  - {err}")

    def create_sequences_sheet(self):
        """_Sequences 시트 생성"""
        try:
            try:
                sheet = self.spreadsheet.worksheet('_Sequences')
                sheet.clear()
            except gspread.WorksheetNotFound:
                sheet = self.spreadsheet.add_worksheet('_Sequences', 10, 4)
            
            data = [
                ['seq_name', 'last_value', 'prefix', 'padding'],
                ['member_id', 0, 'M', 5],
                ['family_id', 0, 'F', 4],
                ['event_id', 0, 'E', 5],
                ['affil_id', 0, 'A', 5],
            ]
            sheet.update('A1:D5', data)
            print("  ✓ _Sequences created")
        except Exception as e:
            self.errors.append(f"Failed to create _Sequences: {e}")

    def create_departments_sheet(self):
        """_Departments 시트 생성"""
        try:
            try:
                sheet = self.spreadsheet.worksheet('_Departments')
                sheet.clear()
            except gspread.WorksheetNotFound:
                sheet = self.spreadsheet.add_worksheet('_Departments', 10, 3)
            
            data = [
                ['dept_id', 'name', 'sort_order'],
                ['D01', '장년부', 1],
                ['D02', '청년부', 2],
                ['D03', '청소년부', 3],
                ['D04', '어린이부', 4],
            ]
            sheet.update('A1:C5', data)
            print("  ✓ _Departments created")
        except Exception as e:
            self.errors.append(f"Failed to create _Departments: {e}")

    def _parse_gender(self, value) -> str:
        if pd.isna(value):
            return ''
        v = str(value).strip()
        if v in ('남', 'M', '남자'):
            return 'M'
        if v in ('여', 'F', '여자'):
            return 'F'
        return ''
    
    def _parse_date(self, value) -> str:
        if pd.isna(value):
            return ''
        try:
            if isinstance(value, pd.Timestamp):
                return value.strftime('%Y-%m-%d')
            return str(value)
        except:
            return ''

    def migrate_members(self) -> int:
        """성도 데이터 마이그레이션"""
        if not os.path.exists(self.excel_path):
            print(f"Excel file not found: {self.excel_path}")
            return 0
            
        excel = pd.ExcelFile(self.excel_path)
        
        real_sheets = excel.sheet_names
        # Map logical names to real sheet names (fuzzy match)
        target_map = {
            '장년부': next((s for s in real_sheets if '장년부' in s), None),
            '청년부': next((s for s in real_sheets if '청년부' in s), None),
            '청소년부': next((s for s in real_sheets if '청소년부' in s), None),
            '어린이부': next((s for s in real_sheets if '어린이부' in s), None)
        }
        
        dept_map = {
            '장년부': 'D01', '청년부': 'D02', 
            '청소년부': 'D03', '어린이부': 'D04'
        }
        
        all_members = []
        member_id = 1
        
        for logical_name, sheet_name in target_map.items():
            if not sheet_name:
                print(f"  ⚠️ '{logical_name}' matching sheet not found, skipping")
                continue
            
            print(f"  Processing {sheet_name}...")
            # Header check logic (0 or 1)
            df = pd.read_excel(excel, sheet_name=sheet_name, header=0)
            if '이름' not in df.columns and '성명' not in df.columns:
                 df = pd.read_excel(excel, sheet_name=sheet_name, header=1)
            
            name_col = '이름' if '이름' in df.columns else '성명'
            if name_col not in df.columns:
                print(f"  ⚠️ Failed to find Name column in {sheet_name}")
                continue

            for _, row in df.iterrows():
                name = str(row.get(name_col, '')).strip()
                if not name or name == 'nan' or name == '이름' or name == '성명':
                    continue
                
                try:
                    member_data = {
                        'member_id': f'M{member_id:05d}',
                        'name': name,
                        'family_id': '',
                        'dept_id': dept_map[logical_name],
                        'group_id': '',  # 별도 매핑 필요
                        'gender': self._parse_gender(row.get('성별')),
                        'birth_date': self._parse_date(row.get('생년월일')),
                        'lunar_solar': 'Y' if '양' in str(row.get('(양음)', '양')) else 'N',
                        'phone': str(row.get('핸드폰', '')).strip(),
                        'address': str(row.get('주소', '')).strip(),
                        'church_role': str(row.get('연합교회직분', '성도')).strip(),
                        'group_role': str(row.get('목장직분', '목원')).strip(),
                        'member_type': str(row.get('구분', '등록교인')).strip(),
                        'status': '재적',
                        'photo_url': '',
                        'created_at': self._parse_date(row.get('등록일')),
                        'updated_at': pd.Timestamp.now().strftime('%Y-%m-%d'),
                    }
                    
                    all_members.append(member_data)
                    member_id += 1
                    
                except Exception as e:
                    self.errors.append(f"Member '{name}' error: {e}")
        
        # Google Sheets에 저장
        if all_members:
            try:
                try:
                    sheet = self.spreadsheet.worksheet('Members')
                    sheet.clear()
                except gspread.WorksheetNotFound:
                    sheet = self.spreadsheet.add_worksheet('Members', 1000, 20)
                
                headers = list(all_members[0].keys())
                rows = [headers] + [[m[h] for h in headers] for m in all_members]
                sheet.update(f'A1:T{len(rows)}', rows)
                
                # 시퀀스 업데이트
                try:
                    worksheet = self.spreadsheet.worksheet('_Sequences')
                    # Find member_id row (usually 2nd row)
                    worksheet.update('B2', [[member_id - 1]])
                except:
                    pass # Ignore if sequence update fails
                    
                print("  ✓ Members sheet updated")
            except Exception as e:
                self.errors.append(f"Failed to update Members sheet: {e}")
            
        return len(all_members)


    def get_name_to_id_map(self):
        """성도 이름 -> ID 매핑 가져오기"""
        try:
            members_sheet = self.spreadsheet.worksheet('Members')
            members_data = members_sheet.get_all_records()
            return {m['name']: m['member_id'] for m in members_data}
        except Exception as e:
            print(f"  ⚠️ Failed to read Members sheet for mapping: {e}")
            return {}

    def migrate_historical_attendance(self) -> int:
        """2019-2024 과거 데이터 마이그레이션"""
        excel = pd.ExcelFile(self.excel_path)
        name_to_id = self.get_name_to_id_map()
        total_records = 0

        # Sheet configuration: (sheet_name, header_row_index)
        # Note: header_row_index is 0-based. 
        # 2024: Row 11 (index 10)
        # 2019-2023: Row 6 (index 5)
        # Sheet configuration: (sheet_name, header_row_index)
        # Note: header_row_index is 0-based index from detect_headers (which matched exact row index)
        history_config = [
            ('2024년', 11), 
            ('2023년', 6), 
            ('2022년', 6), 
            ('2021이전', 6)
        ]

        for sheet_name, header_idx in history_config:
            if sheet_name not in excel.sheet_names:
                print(f"  ⚠️ Sheet '{sheet_name}' not found, skipping.")
                continue

            print(f"  Processing '{sheet_name}'...")
            try:
                df = pd.read_excel(excel, sheet_name=sheet_name, header=header_idx)
                
                # Identify Date Columns (type check)
                from datetime import datetime
                date_cols = []
                for col in df.columns:
                    match = False
                    if isinstance(col, pd.Timestamp):
                        match = True
                    elif isinstance(col, datetime):
                        match = True
                    
                    if match:
                        date_cols.append(col)
                    else:
                        # Try parsing string if it looks like a date?
                        # For now, let's stick to object types as seen in analysis
                        pass
                        
                print(f"    - Found {len(date_cols)} date columns ({[str(c)[:10] for c in date_cols[:3]]}...)")
                if len(date_cols) == 0:
                    print(f"    [DEBUG] First 5 columns: {df.columns[:5].tolist()}")
                    print(f"    [DEBUG] Types: {[type(c) for c in df.columns[:5]]}")
                
                sheet_records = []
                
                for _, row in df.iterrows():
                    name = str(row.get('성명', '')).strip()
                    if not name or name not in name_to_id:
                        continue
                    
                    member_id = name_to_id[name]

                    for date_col in date_cols:
                        value = row[date_col]
                        if pd.isna(value):
                            continue
                        
                        # Normalize value
                        val_str = str(value).strip()
                        attend_type = None
                        
                        if val_str == '1' or val_str == '1.0':
                            attend_type = AttendType.PRESENT.value
                        elif val_str == '0' or val_str == '0.0':
                            attend_type = AttendType.ABSENT.value
                        elif val_str.upper() in ['O', 'ON', 'ONLINE', '2']:
                            attend_type = AttendType.ONLINE.value
                        
                        if attend_type:
                            year = date_col.year
                            week_no = date_col.isocalendar()[1]
                            attend_id = f"AT{year}_W{week_no:02d}_{member_id}"
                            
                            sheet_records.append({
                                'attend_id': attend_id,
                                'member_id': member_id,
                                'attend_date': date_col.strftime('%Y-%m-%d'),
                                'attend_type': attend_type,
                                'year': year,
                                'week_no': week_no,
                            })
                
                # Batch save by year (since '2021이전' has multiple years)
                if sheet_records:
                    df_sheet = pd.DataFrame(sheet_records)
                    for year, group in df_sheet.groupby('year'):
                        self._save_attendance_batch(int(year), group.to_dict('records'))
                        total_records += len(group)
                        
            except Exception as e:
                self.errors.append(f"Error processing {sheet_name}: {e}")
        
        return total_records

    def migrate_current_attendance(self) -> int:
        """2025 현재 출석부 마이그레이션"""
        excel = pd.ExcelFile(self.excel_path)
        name_to_id = self.get_name_to_id_map()
        
        if '출석부' not in excel.sheet_names:
            print("  ⚠️ '출석부' 시트 없음")
            return 0
            
        print("  Processing '출석부' (2025)...")
        # Header is at Row 7 (index 6) for 2025 -> index 7 actually if detect_headers output was 7
        try:
            df = pd.read_excel(excel, sheet_name='출석부', header=7)
            
            # Robust date column detection
            from datetime import datetime
            date_cols = []
            for col in df.columns:
                if isinstance(col, (pd.Timestamp, datetime)):
                    date_cols.append(col)
                    
            print(f"    - Found {len(date_cols)} date columns")
            
            attendance_records = []
            
            for _, row in df.iterrows():
                name = str(row.get('성명', '')).strip()
                if not name or name not in name_to_id:
                    continue
                
                member_id = name_to_id[name]
                
                for date_col in date_cols:
                    value = row[date_col]
                    if pd.isna(value):
                        continue
                        
                    val_str = str(value).strip()
                    attend_type = None
                    
                    if val_str == '1' or val_str == '1.0':
                        attend_type = AttendType.PRESENT.value
                    elif val_str == '0' or val_str == '0.0':
                        attend_type = AttendType.ABSENT.value
                    elif val_str.upper() in ['O', 'ON', '2']:
                        attend_type = AttendType.ONLINE.value
                        
                    if attend_type:
                        year = date_col.year
                        week_no = date_col.isocalendar()[1]
                        attend_id = f"AT{year}_W{week_no:02d}_{member_id}"
                        
                        attendance_records.append({
                            'attend_id': attend_id,
                            'member_id': member_id,
                            'attend_date': date_col.strftime('%Y-%m-%d'),
                            'attend_type': attend_type,
                            'year': year,
                            'week_no': week_no,
                        })
            
            if attendance_records:
                self._save_attendance_batch(2025, attendance_records)
                return len(attendance_records)
        except Exception as e:
             self.errors.append(f"Error processing 2025 출석부: {e}")
             
        return 0

    def _save_attendance_batch(self, year: int, records: list):
        """Helper to save attendance records to year-specific sheet"""
        sheet_name = f'Attendance_{year}'
        try:
            try:
                sheet = self.spreadsheet.worksheet(sheet_name)
                # Append strategy is risky if run multiple times. 
                # For migration, we might want to clear or carefully append.
                # Let's clear for now to ensure clean state during dev.
                # In prod, Upsert or Append is better.
                sheet.clear() 
            except gspread.WorksheetNotFound:
                sheet = self.spreadsheet.add_worksheet(sheet_name, 10000, 10)
            
            if not records:
                return

            headers = list(records[0].keys())
            rows = [headers] + [[r[h] for h in headers] for r in records]
            sheet.update(f'A1:F{len(rows)}', rows)
            print(f"    ✓ Saved {len(records)} records to {sheet_name}")
            
        except Exception as e:
            self.errors.append(f"Failed to update {sheet_name}: {e}")

    def migrate_attendance(self):
        """Legacy wrapper"""
        pass

    def validate_all(self):
        """전체 데이터 검증"""
        try:
            members_sheet = self.spreadsheet.worksheet('Members')
            members = members_sheet.get_all_records()
            print(f"  - Total Members: {len(members)}")
            
            ids = [m['member_id'] for m in members]
            duplicates = [id for id in ids if ids.count(id) > 1]
            if duplicates:
                print(f"  ⚠️ Duplicate IDs found: {set(duplicates)}")
            else:
                print("  ✓ No duplicate IDs")
        except Exception as e:
            print(f"Validation failed: {e}")

if __name__ == '__main__':
    # Default Paths
    EXCEL_PATH = r"g:\내 드라이브\g_dev\#yebom\2025출석부(목자용).xlsx"
    
    migrator = DataMigrator(excel_path=EXCEL_PATH)
    migrator.migrate_all()
