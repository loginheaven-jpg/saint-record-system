"""
Members 시트의 group_id를 CSV 데이터 기반으로 업데이트하는 스크립트
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

# CSV 목장명 -> group_id 매핑 (사용자가 입력한 _Groups 시트 기준)
MOKJANG_TO_GROUP_ID = {
    # 장년부 (D01)
    '네팔': 'G01',
    '러시아': 'G02',
    '사역자': 'G03',
    '여명': 'G04',
    '우즈벡': 'G05',
    '은혜': 'G06',
    '일본': 'G07',
    '철원': 'G08',
    '청송': 'G09',
    '태국': 'G10',
    '필리핀': 'G11',
    '할렐루야': 'G12',
    '할렐루야 ': 'G12',  # 공백 포함 버전
    # 청년부 (D02)
    '베트남1': 'G13',
    '베트남': 'G13',  # 베트남1과 동일 처리
    '베트남2': 'G14',
    '아나니아': 'G15',
    '카메룬': 'G16',
    # 청소년부 (D03)
    '청소년': 'G17',
    # 어린이부 (D04)
    '화평반': 'G18',
    '기쁨반': 'G19',
    '사랑반': 'G20',
    '친절반': 'G21',
    '신실반': 'G22',
    '선한반': 'G23',
    '인내2반': 'G24',
    '인내1반': 'G25',
}


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

    raise Exception(f"credentials.json을 찾을 수 없습니다. 확인된 경로: {possible_paths}")


def load_csv_data():
    """CSV 파일 로드"""
    csv_path = r'c:\dev\yebom\2025출석부(목자용) - 교인명부.csv'
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"CSV 로드 완료: {len(df)} 행")
    return df


def update_members_group_id(dry_run=True):
    """
    Members 시트의 group_id 업데이트

    Args:
        dry_run: True면 실제 업데이트 없이 결과만 출력
    """
    # 인증
    creds = get_credentials()
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)

    # Members 시트 가져오기
    members_sheet = spreadsheet.worksheet('Members')
    members_data = members_sheet.get_all_records()
    members_df = pd.DataFrame(members_data)

    print(f"Members 시트 로드 완료: {len(members_df)} 행")
    print(f"컬럼: {list(members_df.columns)}")

    # CSV 데이터 로드
    csv_df = load_csv_data()

    # CSV에서 이름 -> 목장 매핑 생성
    name_to_mokjang = {}
    for _, row in csv_df.iterrows():
        name = str(row['이름']).strip()
        mokjang = str(row['목장']).strip() if pd.notna(row['목장']) else ''
        if name and mokjang:
            name_to_mokjang[name] = mokjang

    print(f"\nCSV 이름-목장 매핑: {len(name_to_mokjang)} 개")

    # 업데이트할 항목 찾기
    updates = []
    not_found = []
    no_mapping = []

    headers = members_sheet.row_values(1)
    group_id_col = headers.index('group_id') + 1 if 'group_id' in headers else None

    if not group_id_col:
        print("ERROR: group_id 컬럼을 찾을 수 없습니다!")
        return

    print(f"group_id 컬럼 위치: {group_id_col}")

    for idx, row in members_df.iterrows():
        member_name = str(row.get('name', '')).strip()
        current_group_id = str(row.get('group_id', '')).strip()
        row_num = idx + 2  # 헤더가 1행이므로 데이터는 2행부터

        if not member_name:
            continue

        # CSV에서 목장 찾기
        if member_name in name_to_mokjang:
            mokjang = name_to_mokjang[member_name]
            new_group_id = MOKJANG_TO_GROUP_ID.get(mokjang)

            if new_group_id:
                if current_group_id != new_group_id:
                    updates.append({
                        'row': row_num,
                        'name': member_name,
                        'mokjang': mokjang,
                        'old_group_id': current_group_id,
                        'new_group_id': new_group_id
                    })
            else:
                no_mapping.append({
                    'name': member_name,
                    'mokjang': mokjang
                })
        else:
            not_found.append(member_name)

    # 결과 출력
    print(f"\n=== 업데이트 대상: {len(updates)} 건 ===")
    for u in updates[:20]:  # 처음 20개만 출력
        print(f"  [{u['row']}] {u['name']}: {u['mokjang']} -> {u['new_group_id']} (기존: {u['old_group_id']})")
    if len(updates) > 20:
        print(f"  ... 외 {len(updates) - 20}건")

    if no_mapping:
        print(f"\n=== 매핑 없는 목장: {len(no_mapping)} 건 ===")
        unique_mokjangs = set(item['mokjang'] for item in no_mapping)
        for m in unique_mokjangs:
            print(f"  '{m}'")

    if not_found:
        print(f"\n=== CSV에 없는 성도: {len(not_found)} 명 ===")
        for name in not_found[:10]:
            print(f"  {name}")
        if len(not_found) > 10:
            print(f"  ... 외 {len(not_found) - 10}명")

    # 실제 업데이트 (배치 방식)
    if not dry_run and updates:
        print(f"\n=== 실제 업데이트 시작 (배치 방식) ===")

        # 배치 업데이트를 위한 데이터 준비
        batch_data = []
        for u in updates:
            cell_address = gspread.utils.rowcol_to_a1(u['row'], group_id_col)
            batch_data.append({
                'range': f"Members!{cell_address}",
                'values': [[u['new_group_id']]]
            })

        # 배치 업데이트 실행 (한 번에 최대 50개씩, 딜레이 추가)
        import time
        batch_size = 50
        for i in range(0, len(batch_data), batch_size):
            batch_chunk = batch_data[i:i+batch_size]
            try:
                members_sheet.spreadsheet.values_batch_update(
                    body={
                        'valueInputOption': 'RAW',
                        'data': batch_chunk
                    }
                )
                print(f"  {min(i+batch_size, len(updates))}/{len(updates)} 완료...")
                time.sleep(2)  # API 속도 제한 방지
            except Exception as e:
                print(f"  에러 발생: {e}")
                print(f"  10초 대기 후 재시도...")
                time.sleep(10)
                members_sheet.spreadsheet.values_batch_update(
                    body={
                        'valueInputOption': 'RAW',
                        'data': batch_chunk
                    }
                )
                print(f"  {min(i+batch_size, len(updates))}/{len(updates)} 완료 (재시도)")

        print(f"총 {len(updates)}건 업데이트 완료!")
    elif dry_run:
        print(f"\n[DRY RUN 모드] 실제 업데이트를 하려면 dry_run=False로 실행하세요.")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Members group_id 업데이트')
    parser.add_argument('--execute', action='store_true', help='실제 업데이트 실행')
    args = parser.parse_args()

    update_members_group_id(dry_run=not args.execute)
