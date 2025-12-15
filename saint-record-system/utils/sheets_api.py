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


@st.cache_data(ttl=86400, show_spinner=False)  # 24시간 캐시 (어드민 수동 새로고침 시 클리어)
def _cached_get_sheet_data(sheet_name: str) -> List[Dict]:
    """시트 데이터 캐시 (24시간 TTL) - Members, Departments, Groups"""
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
    _cached_get_attendance_data.clear()


@st.cache_data(ttl=86400, show_spinner=False)  # 24시간 캐시 (어드민 수동 새로고침 시 클리어)
def _cached_get_attendance_data(year: int) -> List[Dict]:
    """출석 시트 데이터 캐시 (24시간 TTL) - 전체 연도 출석 데이터"""
    sheet_name = f'Attendance_{year}'
    try:
        client = _get_gspread_client()
        spreadsheet = client.open_by_key(SHEET_ID)
        sheet = spreadsheet.worksheet(sheet_name)
        return sheet.get_all_records()
    except Exception as e:
        print(f"Attendance data fetch error ({sheet_name}): {e}")
        return []


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
            if filters.get('member_type'):
                types = filters['member_type']
                if isinstance(types, list):
                    df = df[df['member_type'].isin(types)]
                else:
                    df = df[df['member_type'] == types]
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
        """출석 조회 (5분 캐시 활용 - API 429 에러 방지)"""
        # 캐시된 데이터 사용
        data = _cached_get_attendance_data(year)
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

    def toggle_attendance(self, member_id: str, attend_date: str) -> Dict:
        """
        출석 상태 토글 (출석 ↔ 결석)
        대시보드에서 클릭으로 출석 수정할 때 사용

        Args:
            member_id: 성도 ID
            attend_date: 출석 날짜 (YYYY-MM-DD)

        Returns:
            {'success': True, 'new_status': '1' or '0', 'action': 'created' or 'updated' or 'deleted'}
        """
        from datetime import datetime
        from .enums import AttendType

        year = int(attend_date[:4])
        date_obj = datetime.strptime(attend_date, '%Y-%m-%d')
        # 주차 계산 (ISO week number)
        week_no = date_obj.isocalendar()[1]

        sheet_name = f'Attendance_{year}'

        try:
            sheet = self.get_sheet(sheet_name)
        except:
            # 시트 없으면 생성
            sheet = self.spreadsheet.add_worksheet(sheet_name, 10000, 10)
            headers = ['attend_id', 'member_id', 'attend_date',
                      'attend_type', 'year', 'week_no']
            sheet.append_row(headers)

        # 현재 출석 상태 조회
        all_data = sheet.get_all_records()
        existing_row = None
        existing_row_num = None

        for i, row in enumerate(all_data):
            if row.get('member_id') == member_id and row.get('attend_date') == attend_date:
                existing_row = row
                existing_row_num = i + 2  # 헤더가 1행
                break

        if existing_row:
            current_status = str(existing_row.get('attend_type', '0'))
            if current_status in ('1', '2'):  # 출석/온라인 → 결석
                # 행 삭제 (결석은 레코드 없음으로 처리)
                sheet.delete_rows(existing_row_num)
                # 캐시 클리어
                _cached_get_attendance_data.clear()
                return {'success': True, 'new_status': '0', 'action': 'deleted'}
            else:  # 결석 → 출석
                # attend_type을 1로 업데이트
                sheet.update_cell(existing_row_num, 4, '1')  # attend_type 컬럼
                _cached_get_attendance_data.clear()
                return {'success': True, 'new_status': '1', 'action': 'updated'}
        else:
            # 레코드 없음 = 결석 → 출석으로 생성
            attend_id = f"AT{year}_W{week_no:02d}_{member_id}"
            new_row = [
                attend_id,
                member_id,
                attend_date,
                '1',  # 출석
                year,
                week_no
            ]
            sheet.append_row(new_row)
            _cached_get_attendance_data.clear()
            return {'success': True, 'new_status': '1', 'action': 'created'}

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

        # 출석 성도 조회 (status='출석'인 성도만 - 대시보드 분모 기준)
        members = self.get_members({'status': '출석'})
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

        # 출석 성도 조회 (status='출석'인 성도만 - 대시보드 분모 기준)
        members = self.get_members({'status': '출석'})
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
        이번 달 신규 등록 성도 수 (출석 중인 재적교인 기준)
        Returns: {'count': 3, 'last_month_count': 5}
        """
        members = self.get_members({
            'status': '출석',
            'member_type': ['등록교인', '회원교인']
        })
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
        3주 연속 결석 성도 목록 (출석 중인 재적교인 기준)
        Returns: [{'member_id': 'M001', 'name': '홍길동', 'weeks_absent': 3}, ...]
        """
        now = pd.Timestamp.now()
        # 지난 일요일
        days_since_sunday = (now.weekday() + 1) % 7
        last_sunday = now - pd.Timedelta(days=days_since_sunday)

        members = self.get_members({
            'status': '출석',
            'member_type': ['등록교인', '회원교인']
        })
        if members.empty:
            return []

        # 최근 3주 일요일 날짜들
        sundays = [
            (last_sunday - pd.Timedelta(weeks=i)).strftime('%Y-%m-%d')
            for i in range(3)
        ]

        absent_candidates = {}

        for member_id in members['member_id'].tolist():
            absent_count = 0
            for sunday in sundays:
                # 각 주마다 연도 추출 (연도 경계 처리)
                year = int(sunday[:4])
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
        이번 주 생일 성도 목록 (출석 중인 재적교인 기준)
        Returns: [{'member_id': 'M001', 'name': '홍길동', 'birth_date': '12/15'}, ...]
        """
        members = self.get_members({
            'status': '출석',
            'member_type': ['등록교인', '회원교인']
        })
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

    # ============================================================
    # 새 API 메서드 (dashboard_v3.html 기반 UI용)
    # ============================================================

    def get_8week_dept_attendance(self) -> List[Dict]:
        """
        8주간 부서별 출석 데이터 (스택 바 차트용)
        Returns: [
            {"week": "1월 5일", "adults": 89, "youth": 52, "teens": 18, "children": 34},
            ...
        ]
        """
        now = pd.Timestamp.now()
        # 지난 일요일 계산
        days_since_sunday = (now.weekday() + 1) % 7
        last_sunday = now - pd.Timedelta(days=days_since_sunday)

        # 부서 ID → CSS 클래스 매핑
        dept_name_to_key = {
            '장년부': 'adults',
            '청년부': 'youth',
            '청소년부': 'teens',
            '어린이부': 'children'
        }

        # 부서 목록 조회
        departments = self.get_departments()
        if departments.empty:
            return []

        # 출석 성도 조회 (status='출석'인 성도만 - 대시보드 분모 기준)
        members = self.get_members({'status': '출석'})
        if members.empty:
            return []

        results = []

        # 8주 역순 (오래된 것부터)
        for i in range(7, -1, -1):
            sunday = last_sunday - pd.Timedelta(weeks=i)
            sunday_str = sunday.strftime('%Y-%m-%d')
            week_label = sunday.strftime('%m월 %d일').replace(' 0', ' ').lstrip('0')

            year = int(sunday_str[:4])
            attendance = self.get_attendance(year, date=sunday_str)

            week_data = {'week': week_label, 'adults': 0, 'youth': 0, 'teens': 0, 'children': 0}

            for _, dept in departments.iterrows():
                dept_id = str(dept.get('dept_id', ''))
                dept_name = dept.get('dept_name', '')
                dept_key = dept_name_to_key.get(dept_name)

                if not dept_key:
                    continue

                # 해당 부서 성도 필터
                dept_members = members[members['dept_id'].astype(str) == dept_id]
                member_ids = dept_members['member_id'].tolist()

                # 출석자 수
                if not attendance.empty and member_ids:
                    dept_attendance = attendance[attendance['member_id'].isin(member_ids)]
                    present = len(dept_attendance[
                        dept_attendance['attend_type'].astype(str).isin(['1', '2'])
                    ])
                else:
                    present = 0

                week_data[dept_key] = present

            results.append(week_data)

        return results

    def get_dept_stats(self, base_date: Optional[str] = None) -> List[Dict]:
        """
        부서별 통계 (부서 카드용)

        Args:
            base_date: 기준 날짜 (YYYY-MM-DD, 일요일). None이면 오늘 기준 최근 일요일

        Returns: [
            {
                "dept_id": "1",
                "name": "장년부",
                "emoji": "👴",
                "css_class": "adults",
                "groups_count": 12,
                "members_count": 89,
                "attendance_rate": 78
            },
            ...
        ]
        """
        # 스타일 매핑
        style_mapping = {
            '장년부': {'emoji': '👴', 'css_class': 'adults'},
            '청년부': {'emoji': '👨', 'css_class': 'youth'},
            '청소년부': {'emoji': '👦', 'css_class': 'teens'},
            '어린이부': {'emoji': '👧', 'css_class': 'children'},
        }
        default_style = {'emoji': '👥', 'css_class': 'default'}

        # 부서 목록
        departments = self.get_departments()
        if departments.empty:
            return []

        # 목장 목록
        groups = self.get_groups()

        # 출석 성도 (대시보드 기준)
        members = self.get_members({'status': '출석'})

        # 기준 날짜 설정 (선택한 날짜 또는 오늘 기준 최근 일요일)
        if base_date:
            last_sunday_str = base_date
        else:
            now = pd.Timestamp.now()
            days_since_sunday = (now.weekday() + 1) % 7
            last_sunday = now - pd.Timedelta(days=days_since_sunday)
            last_sunday_str = last_sunday.strftime('%Y-%m-%d')

        year = int(last_sunday_str[:4])
        attendance = self.get_attendance(year, date=last_sunday_str)

        results = []

        for _, dept in departments.iterrows():
            dept_id = str(dept.get('dept_id', ''))
            dept_name = dept.get('dept_name', '')

            if not dept_id:
                continue

            # 스타일
            style = style_mapping.get(dept_name, default_style)

            # 목장 수
            if not groups.empty:
                dept_groups = groups[groups['dept_id'].astype(str) == dept_id]
                groups_count = len(dept_groups)
            else:
                groups_count = 0

            # 성도 수
            if not members.empty:
                dept_members = members[members['dept_id'].astype(str) == dept_id]
                members_count = len(dept_members)
                member_ids = dept_members['member_id'].tolist()
            else:
                members_count = 0
                member_ids = []

            # 출석률
            if members_count > 0 and not attendance.empty and member_ids:
                dept_attendance = attendance[attendance['member_id'].isin(member_ids)]
                present = len(dept_attendance[
                    dept_attendance['attend_type'].astype(str).isin(['1', '2'])
                ])
                attendance_rate = int((present / members_count) * 100)
            else:
                attendance_rate = 0

            results.append({
                'dept_id': dept_id,
                'name': dept_name,
                'emoji': style['emoji'],
                'css_class': style['css_class'],
                'groups_count': groups_count,
                'members_count': members_count,
                'attendance_rate': attendance_rate
            })

        return results

    def get_dept_attendance_trend(self, dept_id: str, base_date: Optional[str] = None) -> List[int]:
        """
        부서별 8주 출석률 트렌드 (팝오버 미니차트용)

        Args:
            dept_id: 부서 ID
            base_date: 기준 날짜 (YYYY-MM-DD, 일요일). None이면 오늘 기준 최근 일요일

        Returns: [80, 82, 76, 79, 81, 78, 80, 83]  # 8주 출석률 % (과거→최근)
        """
        # 기준 날짜 설정
        if base_date:
            last_sunday = pd.Timestamp(base_date)
        else:
            now = pd.Timestamp.now()
            days_since_sunday = (now.weekday() + 1) % 7
            last_sunday = now - pd.Timedelta(days=days_since_sunday)

        # 출석 성도 (대시보드 기준)
        members = self.get_members({'status': '출석'})
        if members.empty:
            return [0] * 8

        # 해당 부서 성도
        dept_members = members[members['dept_id'].astype(str) == str(dept_id)]
        total = len(dept_members)
        if total == 0:
            return [0] * 8

        member_ids = dept_members['member_id'].tolist()

        results = []

        for i in range(7, -1, -1):
            sunday = last_sunday - pd.Timedelta(weeks=i)
            sunday_str = sunday.strftime('%Y-%m-%d')
            year = int(sunday_str[:4])

            attendance = self.get_attendance(year, date=sunday_str)

            if not attendance.empty:
                dept_attendance = attendance[attendance['member_id'].isin(member_ids)]
                present = len(dept_attendance[
                    dept_attendance['attend_type'].astype(str).isin(['1', '2'])
                ])
                rate = int((present / total) * 100)
            else:
                rate = 0

            results.append(rate)

        return results

    def get_groups_by_dept(self, dept_id: str) -> List[Dict]:
        """
        부서별 목장 목록 (목장 그리드용)
        Returns: [{"group_id": "1", "name": "네팔 목장", "members_count": 13}, ...]
        """
        groups = self.get_groups(dept_id)
        if groups.empty:
            return []

        # 출석 성도 (대시보드 기준)
        members = self.get_members({'status': '출석'})

        results = []
        for _, group in groups.iterrows():
            group_id = str(group.get('group_id', ''))
            group_name = group.get('group_name', '')

            if not group_id:
                continue

            # 성도 수
            if not members.empty:
                group_members = members[members['group_id'].astype(str) == group_id]
                members_count = len(group_members)
            else:
                members_count = 0

            results.append({
                'group_id': group_id,
                'name': group_name,
                'members_count': members_count
            })

        return results

    def get_dept_attendance_table(self, dept_id: str, base_date: str, group_id: Optional[str] = None) -> Dict:
        """
        부서별 8주 출석 테이블 데이터 (출석 현황 테이블용)

        Args:
            dept_id: 부서 ID
            base_date: 기준 날짜 (YYYY-MM-DD, 일요일)
            group_id: 목장 ID (선택, None이면 부서 전체)

        Returns: {
            "weeks": ["12/7", "11/30", ...],  # 8주 날짜
            "members": [
                {"member_id": "M001", "name": "홍길동", "group_name": "네팔 목장", "attendance": [1, 1, 0, ...]},
                ...
            ]
        }
        """
        base = pd.Timestamp(base_date)

        # 8주 일요일 날짜 계산 (과거 → 최근, 선택 날짜가 우측에 표시)
        weeks = []
        for i in range(7, -1, -1):  # 7주 전부터 선택 날짜까지
            sunday = base - pd.Timedelta(weeks=i)
            weeks.append({
                'date': sunday.strftime('%Y-%m-%d'),
                'label': sunday.strftime('%m/%d').lstrip('0').replace('/0', '/')
            })

        # 출석 성도 조회
        members = self.get_members({'status': '출석'})
        if members.empty:
            return {'weeks': [w['label'] for w in weeks], 'members': []}

        # 부서 필터
        dept_members = members[members['dept_id'].astype(str) == str(dept_id)]

        # 목장 필터 (선택적)
        if group_id:
            dept_members = dept_members[dept_members['group_id'].astype(str) == str(group_id)]

        if dept_members.empty:
            return {'weeks': [w['label'] for w in weeks], 'members': []}

        # 목장 정보 조회
        groups = self.get_groups(dept_id)
        group_map = {}
        if not groups.empty:
            for _, g in groups.iterrows():
                group_map[str(g.get('group_id', ''))] = g.get('group_name', '')

        # 각 주차별 출석 데이터 조회
        attendance_by_week = {}
        for week in weeks:
            year = int(week['date'][:4])
            attendance = self.get_attendance(year, date=week['date'])
            attendance_by_week[week['date']] = attendance

        # 멤버별 출석 현황 집계
        result_members = []
        for _, member in dept_members.iterrows():
            member_id = member.get('member_id', '')
            name = member.get('name', '')
            group_id_val = str(member.get('group_id', ''))
            group_name = group_map.get(group_id_val, '-')

            # 8주 출석 상태
            attendance_list = []
            for week in weeks:
                att_df = attendance_by_week[week['date']]
                if att_df.empty:
                    attendance_list.append(0)
                else:
                    member_att = att_df[att_df['member_id'] == member_id]
                    if member_att.empty:
                        attendance_list.append(0)
                    elif member_att['attend_type'].astype(str).isin(['1', '2']).any():
                        attendance_list.append(1)
                    else:
                        attendance_list.append(0)

            result_members.append({
                'member_id': member_id,
                'name': name,
                'group_name': group_name,
                'attendance': attendance_list
            })

        # 이름순 정렬
        result_members.sort(key=lambda x: x['name'])

        return {
            'weeks': [w['label'] for w in weeks],
            'week_dates': [w['date'] for w in weeks],  # 전체 날짜 (YYYY-MM-DD) - 편집용
            'members': result_members
        }
