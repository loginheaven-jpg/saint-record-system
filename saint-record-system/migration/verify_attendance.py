"""
Attendance_2025 시트의 member_id 검증 및 출석 데이터 구조 확인
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets 설정
SHEET_ID = '1cDfZiWbbpV8Z9NwAauG3SAriarJ1HL9xXMkZMJhC5Jo'
SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]


def get_credentials():
    """인증 정보 가져오기"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(base_dir)

    possible_paths = [
        os.path.join(project_dir, 'credentials', 'credentials.json'),
        os.path.join(os.path.dirname(project_dir), 'credentials', 'credentials.json'),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return ServiceAccountCredentials.from_json_keyfile_name(path, SCOPE)

    raise Exception(f"credentials.json을 찾을 수 없습니다.")


def verify_attendance():
    """Attendance_2025 시트 검증"""
    # 인증
    creds = get_credentials()
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)

    # Attendance_2025 시트 확인
    try:
        attendance_sheet = spreadsheet.worksheet('Attendance_2025')
        attendance_data = attendance_sheet.get_all_records()
        attendance_df = pd.DataFrame(attendance_data)
        print(f"Attendance_2025 시트 로드 완료: {len(attendance_df)} 행")
        print(f"컬럼: {list(attendance_df.columns)}")

        if not attendance_df.empty:
            print(f"\n샘플 데이터 (처음 5행):")
            print(attendance_df.head())

            # member_id 컬럼 분석
            if 'member_id' in attendance_df.columns:
                unique_members = attendance_df['member_id'].nunique()
                print(f"\n고유 member_id 수: {unique_members}")

                # Members 시트와 비교
                members_sheet = spreadsheet.worksheet('Members')
                members_data = members_sheet.get_all_records()
                members_df = pd.DataFrame(members_data)

                # member_id 매칭 확인
                attendance_member_ids = set(attendance_df['member_id'].unique())
                members_member_ids = set(members_df['member_id'].unique())

                matched = attendance_member_ids & members_member_ids
                not_in_members = attendance_member_ids - members_member_ids

                print(f"\nMembers와 매칭: {len(matched)}명")
                print(f"Members에 없음: {len(not_in_members)}명")

                if not_in_members:
                    print(f"  없는 ID: {list(not_in_members)[:10]}")
            else:
                print("\n[경고] member_id 컬럼이 없습니다!")

    except gspread.exceptions.WorksheetNotFound:
        print("Attendance_2025 시트가 없습니다. 생성이 필요합니다.")
        return

    # CSV 출석 데이터 확인
    csv_path = r'c:\dev\yebom\2025출석부(목자용) - 출석부.csv'
    csv_df = pd.read_csv(csv_path, encoding='utf-8', header=7)  # 8번째 행이 헤더
    print(f"\n\n=== CSV 출석 데이터 ===")
    print(f"CSV 로드 완료: {len(csv_df)} 행")
    print(f"컬럼: {list(csv_df.columns)[:10]}...")  # 처음 10개 컬럼만

    # 유효한 출석 데이터 수 (성명이 있는 행)
    valid_rows = csv_df[csv_df['성명'].notna() & (csv_df['성명'] != '')]
    print(f"유효한 출석 데이터: {len(valid_rows)} 행")

    # 샘플
    print(f"\n샘플 데이터:")
    print(valid_rows[['세대', '목장', '성명', '년계']].head(10))


if __name__ == '__main__':
    verify_attendance()
