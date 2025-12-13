"""Google Sheets API 래퍼"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from typing import List, Dict, Optional
import streamlit as st
import os
import json

from .validators import MemberCreate, MemberUpdate, AttendanceCreate
from .apps_script_client import AppsScriptClient

# 상수
SHEET_ID = '1cDfZiWbbpV8Z9NwAauG3SAriarJ1HL9xXMkZMJhC5Jo'


# ============================================================
# 전역 캐시 함수 (API 429 에러 방지)
# ============================================================

def _get_gspread_client():
    """gspread 클라이언트 생성 (캐시용 내부 함수)"""
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = None

    # 1순위: 환경변수 (Railway 배포용)
    gcp_json = os.environ.get('GCP_CREDENTIALS_JSON')
    if gcp_json:
        try:
            creds_dict = json.loads(gcp_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        except Exception:
            pass

    # 2순위: Streamlit Secrets
    if not creds:
        try:
            if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
                creds_dict = dict(st.secrets["gcp_service_account"])
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        except Exception:
            pass

    # 3순위: 로컬 credentials.json 파일
    if not creds:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(base_dir)
        root_dir = os.path.dirname(project_dir)

        possible_paths = [
            os.path.join(project_dir, 'credentials', 'credentials.json'),
            os.path.join(root_dir, 'credentials', 'credentials.json')
        ]

        for path in possible_paths:
            if os.path.exists(path):
                creds = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
                break

    if not creds:
        raise Exception("인증 정보를 찾을 수 없습니다.")

    return gspread.authorize(creds)


@st.cache_data(ttl=300, show_spinner=False)  # 5분 캐시
def _cached_get_sheet_data(sheet_name: str) -> List[Dict]:
    """시트 데이터 캐시 (5분 TTL)"""
    try:
        client = _get_gspread_client()
        spreadsheet = client.open_by_key(SHEET_ID)
        sheet = spreadsheet.worksheet(sheet_name)

        try:
            return sheet.get_all_records()
        except Exception:
            # 중복 헤더 문제 발생 시 직접 파싱
            all_values = sheet.get_all_values()
            if len(all_values) < 2:
                return []
            headers = all_values[0]
            clean_headers = []
            for h in headers:
                if h and h.strip():
                    clean_headers.append(h.strip())
                else:
                    break
            data = []
            for row in all_values[1:]:
                if row and row[0]:
                    data.append(dict(zip(clean_headers, row[:len(clean_headers)])))
            return data
    except Exception as e:
        print(f"Sheet data fetch error ({sheet_name}): {e}")
        return []


def clear_sheets_cache():
    """시트 캐시 수동 삭제"""
    _cached_get_sheet_data.clear()


class SheetsAPI:
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.sheet_id = SHEET_ID
        self.script_url = os.environ.get('APPS_SCRIPT_URL', '')

        creds = None

        # 1순위: 환경변수 (Railway 배포용)
        gcp_json = os.environ.get('GCP_CREDENTIALS_JSON')
        if gcp_json:
            try:
                creds_dict = json.loads(gcp_json)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, self.scope)
            except Exception as e:
                print(f"환경변수 인증 실패: {e}")

        # 2순위: Streamlit Secrets
        if not creds:
            try:
                if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
                    creds_dict = dict(st.secrets["gcp_service_account"])
                    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, self.scope)
                    self.script_url = st.secrets.get("apps_script_url", self.script_url)
            except Exception:
                pass

        # 3순위: 로컬 credentials.json 파일
        if not creds:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(base_dir)
            root_dir = os.path.dirname(project_dir)

            possible_paths = [
                os.path.join(project_dir, 'credentials', 'credentials.json'),
                os.path.join(root_dir, 'credentials', 'credentials.json')
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    creds = ServiceAccountCredentials.from_json_keyfile_name(path, self.scope)
                    break

        if not creds:
            raise Exception("인증 정보를 찾을 수 없습니다. 환경변수 GCP_CREDENTIALS_JSON을 설정하세요.")

        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(self.sheet_id)
        self.apps_script = AppsScriptClient(self.script_url)
    
    def get_sheet(self, name: str):
        """시트 가져오기"""
        return self.spreadsheet.worksheet(name)
        
    # ===== Members =====
    
    def get_members(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """성도 목록 조회 (5분 캐시)"""
        data = _cached_get_sheet_data('Members')
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
        """부서 목록 (5분 캐시)"""
        data = _cached_get_sheet_data('_Departments')
        return pd.DataFrame(data)

    def get_groups(self, dept_id: Optional[str] = None) -> pd.DataFrame:
        """목장 목록 (5분 캐시)"""
        data = _cached_get_sheet_data('_Groups')
        df = pd.DataFrame(data)
        if dept_id and not df.empty:
            df = df[df['dept_id'] == dept_id]
        return df
    
    def get_faith_events(self, member_id: str) -> pd.DataFrame:
        """신앙이력 조회"""
        sheet = self.get_sheet('FaithEvents')
        df = pd.DataFrame(sheet.get_all_records())
        return df[df['member_id'] == member_id]

    # ===== 대시보드용 집계 함수 =====

    def get_department_attendance(self, date: str) -> List[Dict]:
        """
        부서별 출석 현황
        Returns: [{'dept_id': '1', 'name': '장년부', 'emoji': '👨‍👩‍👧', 'css_class': 'adults',
                   'total': 108, 'present': 85, 'rate': 78.7}, ...]
        """
        # 이모지/CSS 클래스 매핑 (부서명 기반)
        style_mapping = {
            '장년부': {'emoji': '👨‍👩‍👧', 'css_class': 'adults'},
            '청년부': {'emoji': '🎓', 'css_class': 'youth'},
            '청소년부': {'emoji': '🎒', 'css_class': 'teens'},
            '어린이부': {'emoji': '🧒', 'css_class': 'children'},
        }
        default_style = {'emoji': '👥', 'css_class': 'default'}

        # 부서 목록 조회 (DB에서)
        departments = self.get_departments()
        if departments.empty:
            return []

        # 재적 성도 조회
        members = self.get_members({'status': '재적'})
        if members.empty:
            return []

        # 출석 데이터 조회
        year = int(date[:4])
        attendance = self.get_attendance(year, date=date)

        results = []
        for _, dept in departments.iterrows():
            dept_id = str(dept.get('dept_id', ''))
            dept_name = dept.get('dept_name', '')

            if not dept_id:
                continue

            # 해당 부서 성도 필터
            dept_members = members[members['dept_id'].astype(str) == dept_id]
            total = len(dept_members)

            if total == 0:
                continue

            # 출석자 수 (attend_type '1' 또는 '2')
            if not attendance.empty:
                dept_attendance = attendance[
                    attendance['member_id'].isin(dept_members['member_id'].tolist())
                ]
                present = len(dept_attendance[
                    dept_attendance['attend_type'].astype(str).isin(['1', '2'])
                ])
            else:
                present = 0

            # 스타일 매핑
            style = style_mapping.get(dept_name, default_style)

            results.append({
                'dept_id': dept_id,
                'name': dept_name,
                'emoji': style['emoji'],
                'css_class': style['css_class'],
                'total': total,
                'present': present,
                'rate': round((present / total) * 100, 1) if total > 0 else 0
            })

        return results

    def get_mokjang_attendance(self, date: str) -> List[Dict]:
        """
        목장별 출석 현황
        Returns: [{'group_id': '1', 'name': '네팔 목장', 'emoji': '🇳🇵', 'css_class': 'nepal',
                   'total': 12, 'present': 11, 'rate': 91.7}, ...]
        """
        # 이모지/CSS 클래스 매핑 (목장명 기반)
        style_mapping = {
            '네팔 목장': {'emoji': '🇳🇵', 'css_class': 'nepal'},
            '러시아 목장': {'emoji': '🇷🇺', 'css_class': 'russia'},
            '필리핀 목장': {'emoji': '🇵🇭', 'css_class': 'philippines'},
            '태국 목장': {'emoji': '🇹🇭', 'css_class': 'thailand'},
            '베냉 목장': {'emoji': '🇧🇯', 'css_class': 'benin'},
            '콩고 목장': {'emoji': '🇨🇩', 'css_class': 'congo'},
            '칠레 목장': {'emoji': '🇨🇱', 'css_class': 'chile'},
            '철원 목장': {'emoji': '🏔️', 'css_class': 'cheorwon'},
        }
        default_style = {'emoji': '🏠', 'css_class': 'default'}

        # 목장 목록 조회 (DB에서)
        groups = self.get_groups()
        if groups.empty:
            return []

        # 재적 성도 조회
        members = self.get_members({'status': '재적'})
        if members.empty:
            return []

        # 출석 데이터 조회
        year = int(date[:4])
        attendance = self.get_attendance(year, date=date)

        results = []
        for _, group in groups.iterrows():
            group_id = str(group.get('group_id', ''))
            group_name = group.get('group_name', '')

            if not group_id:
                continue

            # 해당 목장 성도 필터
            group_members = members[members['group_id'].astype(str) == group_id]
            total = len(group_members)

            if total == 0:
                continue

            # 출석자 수
            if not attendance.empty:
                group_attendance = attendance[
                    attendance['member_id'].isin(group_members['member_id'].tolist())
                ]
                present = len(group_attendance[
                    group_attendance['attend_type'].astype(str).isin(['1', '2'])
                ])
            else:
                present = 0

            # 스타일 매핑
            style = style_mapping.get(group_name, default_style)

            results.append({
                'group_id': group_id,
                'name': group_name,
                'emoji': style['emoji'],
                'css_class': style['css_class'],
                'total': total,
                'present': present,
                'rate': round((present / total) * 100, 1) if total > 0 else 0
            })

        return results

    def get_new_members_this_month(self) -> Dict:
        """
        이번 달 신규 등록 성도 수
        Returns: {'count': 3, 'last_month_count': 5}
        """
        members = self.get_members({'status': '재적'})
        if members.empty:
            return {'count': 0, 'last_month_count': 0}

        now = pd.Timestamp.now()
        this_month_start = now.replace(day=1).strftime('%Y-%m-%d')

        last_month = now - pd.DateOffset(months=1)
        last_month_start = last_month.replace(day=1).strftime('%Y-%m-%d')
        last_month_end = (now.replace(day=1) - pd.Timedelta(days=1)).strftime('%Y-%m-%d')

        # 이번 달 신규
        this_month_new = members[members['created_at'] >= this_month_start]

        # 지난 달 신규
        last_month_new = members[
            (members['created_at'] >= last_month_start) &
            (members['created_at'] <= last_month_end)
        ]

        return {
            'count': len(this_month_new),
            'last_month_count': len(last_month_new)
        }

    def get_3week_absent_members(self) -> List[Dict]:
        """
        3주 연속 결석 성도 목록
        Returns: [{'member_id': 'M001', 'name': '홍길동', 'weeks_absent': 3}, ...]
        """
        now = pd.Timestamp.now()
        # 지난 일요일
        days_since_sunday = (now.weekday() + 1) % 7
        last_sunday = now - pd.Timedelta(days=days_since_sunday)

        members = self.get_members({'status': '재적'})
        if members.empty:
            return []

        # 최근 3주 일요일 날짜들
        sundays = [
            (last_sunday - pd.Timedelta(weeks=i)).strftime('%Y-%m-%d')
            for i in range(3)
        ]

        year = int(sundays[0][:4])
        absent_candidates = {}

        for member_id in members['member_id'].tolist():
            absent_count = 0
            for sunday in sundays:
                attendance = self.get_attendance(year, date=sunday, member_ids=[member_id])
                if attendance.empty:
                    absent_count += 1
                elif not attendance[attendance['attend_type'].astype(str).isin(['1', '2'])].empty:
                    break  # 출석했으면 패스
                else:
                    absent_count += 1

            if absent_count >= 3:
                member_info = members[members['member_id'] == member_id].iloc[0]
                absent_candidates[member_id] = {
                    'member_id': member_id,
                    'name': member_info['name'],
                    'weeks_absent': absent_count
                }

        return list(absent_candidates.values())

    def get_birthdays_this_week(self) -> List[Dict]:
        """
        이번 주 생일 성도 목록
        Returns: [{'member_id': 'M001', 'name': '홍길동', 'birth_date': '12/15'}, ...]
        """
        members = self.get_members({'status': '재적'})
        if members.empty:
            return []

        now = pd.Timestamp.now()
        # 이번 주 시작(월요일)과 끝(일요일)
        week_start = now - pd.Timedelta(days=now.weekday())
        week_end = week_start + pd.Timedelta(days=6)

        # 이번 주의 월-일 범위
        week_dates = [
            (week_start + pd.Timedelta(days=i)).strftime('%m-%d')
            for i in range(7)
        ]

        birthdays = []
        for _, member in members.iterrows():
            birth_date = member.get('birth_date', '')
            if not birth_date or pd.isna(birth_date):
                continue

            try:
                # birth_date가 YYYY-MM-DD 형식이라고 가정
                birth_mm_dd = str(birth_date)[5:10]  # MM-DD 부분 추출
                if birth_mm_dd in week_dates:
                    birthdays.append({
                        'member_id': member['member_id'],
                        'name': member['name'],
                        'birth_date': birth_mm_dd.replace('-', '/')
                    })
            except:
                continue

        return birthdays
