"""Google Sheets API 래퍼"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from typing import List, Dict, Optional
import streamlit as st
import os

from .validators import MemberCreate, MemberUpdate, AttendanceCreate
from .apps_script_client import AppsScriptClient


class SheetsAPI:
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Streamlit Secrets 또는 로컬 credentials.json
        # Streamlit Secrets 또는 로컬 credentials.json
        used_secrets = False
        try:
            if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
                creds_dict = st.secrets["gcp_service_account"]
                creds = ServiceAccountCredentials.from_json_keyfile_dict(
                    dict(creds_dict), self.scope
                )
                self.sheet_name = st.secrets.get("sheet_name", "성도기록부_시스템")
                self.script_url = st.secrets.get("apps_script_url", "")
                used_secrets = True
        except Exception:
            # secrets.toml이 없거나 형식이 잘못된 경우 무시하고 로컬 파일 시도
            pass
            
        if not used_secrets:
            # 로컬 개발/마이그레이션용
            base_dir = os.path.dirname(os.path.abspath(__file__)) # saint-record-system/utils
            project_dir = os.path.dirname(base_dir) # saint-record-system
            root_dir = os.path.dirname(project_dir) # #yebom
            
            possible_paths = [
                os.path.join(project_dir, 'credentials', 'credentials.json'),
                os.path.join(root_dir, 'credentials', 'credentials.json')
            ]
            
            creds_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    creds_path = path
                    break
            
            if creds_path:
                print(f"DEBUG: Found credentials at {creds_path}")
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    creds_path, self.scope
                )
                self.sheet_name = "성도기록부_시스템" # 기본값
                # Sheet ID 사용 (마이그레이션 스크립트와 동일하게)
                self.sheet_id = '1cDfZiWbbpV8Z9NwAauG3SAriarJ1HL9xXMkZMJhC5Jo'
                self.script_url = "" # Local fallback
        
        if creds:
            self.client = gspread.authorize(creds)
            if hasattr(self, 'sheet_id') and self.sheet_id:
                 self.spreadsheet = self.client.open_by_key(self.sheet_id)
            else:
                 self.spreadsheet = self.client.open(self.sheet_name)
        
        # Apps Script 클라이언트
        self.apps_script = AppsScriptClient(self.script_url)
    
    def get_sheet(self, name: str):
        """시트 가져오기"""
        return self.spreadsheet.worksheet(name)
        
    # ===== Members =====
    
    def get_members(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """성도 목록 조회"""
        sheet = self.get_sheet('Members')
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        if df.empty:
            return df
        
        if filters:
            if filters.get('dept_id'):
                df = df[df['dept_id'] == filters['dept_id']]
            if filters.get('group_id'):
                df = df[df['group_id'] == filters['group_id']]
            if filters.get('status'):
                df = df[df['status'] == filters['status']]
            if filters.get('search'):
                df = df[df['name'].str.contains(filters['search'], na=False)]
        
        return df
    
    def get_member_by_id(self, member_id: str) -> Optional[Dict]:
        """성도 상세 조회"""
        df = self.get_members()
        member = df[df['member_id'] == member_id]
        if len(member) > 0:
            return member.iloc[0].to_dict()
        return None
    
    def create_member(self, data: MemberCreate) -> Dict:
        """
        성도 등록
        - ID는 Apps Script에서 생성 (락 처리)
        """
        # ID 생성 (Apps Script 호출)
        member_id = self.apps_script.generate_member_id()
        
        sheet = self.get_sheet('Members')
        headers = sheet.row_values(1)
        
        # 데이터 준비
        member_data = data.dict()
        member_data['member_id'] = member_id
        member_data['created_at'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        member_data['updated_at'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        # 행 추가
        row = [member_data.get(col, '') for col in headers]
        sheet.append_row(row)
        
        return {'success': True, 'member_id': member_id}
    
    def update_member(self, member_id: str, data: MemberUpdate) -> Dict:
        """성도 수정"""
        sheet = self.get_sheet('Members')
        
        # member_id로 행 찾기
        cell = sheet.find(member_id, in_column=1)
        if not cell:
            return {'success': False, 'error': 'Member not found'}
        
        row_num = cell.row
        headers = sheet.row_values(1)
        
        # 변경된 필드만 업데이트
        update_data = data.dict(exclude_unset=True)
        update_data['updated_at'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        for key, value in update_data.items():
            if key in headers:
                col_num = headers.index(key) + 1
                sheet.update_cell(row_num, col_num, value)
        
        return {'success': True}
    
    # ===== Attendance =====
    
    def get_attendance(
        self, 
        year: int, 
        week_no: Optional[int] = None,
        member_ids: Optional[List[str]] = None,
        date: Optional[str] = None
    ) -> pd.DataFrame:
        """출석 조회"""
        sheet_name = f'Attendance_{year}'
        
        try:
            sheet = self.get_sheet(sheet_name)
        except:
            return pd.DataFrame()
        
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        if df.empty:
            return df
        
        if week_no:
            df = df[df['week_no'] == week_no]
        if member_ids:
            df = df[df['member_id'].isin(member_ids)]
        if date:
            # 문자열 비교 (YYYY-MM-DD)
            df = df[df['attend_date'] == date]
            
        return df
    
    def save_attendance(self, records: List[AttendanceCreate]) -> Dict:
        """
        출석 저장 (Upsert 패턴)
        - 기존 데이터 삭제 후 새 데이터 삽입
        """
        if not records:
            return {'success': False, 'error': 'No records provided'}
        
        year = records[0].year
        week_no = records[0].week_no
        member_ids = [r.member_id for r in records]
        
        sheet_name = f'Attendance_{year}'
        
        try:
            sheet = self.get_sheet(sheet_name)
        except:
            # 시트 없으면 생성
            # add_worksheet might fail if not authorized scope, but usually typical scope is fine.
            # Row count 10000, Col count 10
            sheet = self.spreadsheet.add_worksheet(sheet_name, 10000, 10)
            headers = ['attend_id', 'member_id', 'attend_date', 
                      'attend_type', 'year', 'week_no']
            sheet.append_row(headers)
        
        # 1. 기존 데이터 조회
        all_data = sheet.get_all_records()
        
        # 2. 삭제할 행 찾기
        rows_to_delete = []
        for i, row in enumerate(all_data):
            # Check conditions
            if (row.get('week_no') == week_no and 
                row.get('member_id') in member_ids):
                # row index is i + 2 because header is row 1
                rows_to_delete.append(i + 2)
        
        # 3. 역순으로 삭제
        deleted_count = 0
        for row_num in sorted(rows_to_delete, reverse=True):
            sheet.delete_rows(row_num)
            deleted_count += 1
        
        # 4. 새 데이터 삽입
        inserted_count = 0
        for record in records:
            attend_id = f"AT{year}_W{week_no:02d}_{record.member_id}"
            row = [
                attend_id,
                record.member_id,
                record.attend_date.strftime('%Y-%m-%d'),
                record.attend_type.value,
                year,
                week_no
            ]
            sheet.append_row(row)
            inserted_count += 1
        
        return {
            'success': True,
            'deleted': deleted_count,
            'inserted': inserted_count
        }
    
    # ===== 기타 =====
    
    def get_departments(self) -> pd.DataFrame:
        """부서 목록"""
        sheet = self.get_sheet('_Departments')
        return pd.DataFrame(sheet.get_all_records())
    
    def get_groups(self, dept_id: Optional[str] = None) -> pd.DataFrame:
        """목장 목록"""
        sheet = self.get_sheet('_Groups')
        df = pd.DataFrame(sheet.get_all_records())
        if dept_id:
            df = df[df['dept_id'] == dept_id]
        return df
    
    def get_faith_events(self, member_id: str) -> pd.DataFrame:
        """신앙이력 조회"""
        sheet = self.get_sheet('FaithEvents')
        df = pd.DataFrame(sheet.get_all_records())
        return df[df['member_id'] == member_id]
