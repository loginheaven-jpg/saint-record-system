"""
Members 시트의 family_id를 CSV '가장' 컬럼 기반으로 업데이트하는 스크립트
같은 '가장' 값을 가진 성도들은 같은 family_id를 가짐
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

    raise Exception(f"credentials.json을 찾을 수 없습니다. 확인된 경로: {possible_paths}")


def load_csv_data():
    """CSV 파일 로드"""
    csv_path = r'c:\dev\yebom\2025출석부(목자용) - 교인명부.csv'
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"CSV 로드 완료: {len(df)} 행")
    return df


def update_members_family_id(dry_run=True):
    """
    Members 시트의 family_id 업데이트

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

    # CSV에서 이름 -> 가장 매핑 생성
    name_to_gajang = {}
    for _, row in csv_df.iterrows():
        name = str(row['이름']).strip()
        gajang = str(row['가장']).strip() if pd.notna(row['가장']) else ''
        if name and gajang:
            name_to_gajang[name] = gajang

    print(f"\nCSV 이름-가장 매핑: {len(name_to_gajang)} 개")

    # 고유 가장명에 family_id 할당
    unique_gajang = sorted(set(name_to_gajang.values()))
    gajang_to_family_id = {g: f"F{i+1:03d}" for i, g in enumerate(unique_gajang)}

    print(f"고유 가정(가장) 수: {len(unique_gajang)}")
    print(f"\n가정 ID 샘플:")
    for g, fid in list(gajang_to_family_id.items())[:10]:
        print(f"  {g} -> {fid}")

    # 업데이트할 항목 찾기
    updates = []
    not_found = []

    headers = members_sheet.row_values(1)
    family_id_col = headers.index('family_id') + 1 if 'family_id' in headers else None

    if not family_id_col:
        print("ERROR: family_id 컬럼을 찾을 수 없습니다!")
        return

    print(f"\nfamily_id 컬럼 위치: {family_id_col}")

    for idx, row in members_df.iterrows():
        member_name = str(row.get('name', '')).strip()
        current_family_id = str(row.get('family_id', '')).strip()
        row_num = idx + 2  # 헤더가 1행이므로 데이터는 2행부터

        if not member_name:
            continue

        # CSV에서 가장 찾기
        if member_name in name_to_gajang:
            gajang = name_to_gajang[member_name]
            new_family_id = gajang_to_family_id.get(gajang)

            if new_family_id:
                if current_family_id != new_family_id:
                    updates.append({
                        'row': row_num,
                        'name': member_name,
                        'gajang': gajang,
                        'old_family_id': current_family_id,
                        'new_family_id': new_family_id
                    })
        else:
            not_found.append(member_name)

    # 결과 출력
    print(f"\n=== 업데이트 대상: {len(updates)} 건 ===")
    for u in updates[:30]:  # 처음 30개만 출력
        print(f"  [{u['row']}] {u['name']}: 가장={u['gajang']} -> {u['new_family_id']} (기존: {u['old_family_id']})")
    if len(updates) > 30:
        print(f"  ... 외 {len(updates) - 30}건")

    if not_found:
        print(f"\n=== CSV에 없는 성도: {len(not_found)} 명 ===")
        for name in not_found[:10]:
            print(f"  {name}")
        if len(not_found) > 10:
            print(f"  ... 외 {len(not_found) - 10}명")

    # 가정별 구성원 확인
    print(f"\n=== 가정별 구성원 (2명 이상인 가정) ===")
    family_members = {}
    for u in updates:
        fid = u['new_family_id']
        gajang = u['gajang']
        if fid not in family_members:
            family_members[fid] = {'gajang': gajang, 'members': []}
        family_members[fid]['members'].append(u['name'])

    multi_member_families = [(fid, data) for fid, data in family_members.items() if len(data['members']) > 1]
    for fid, data in sorted(multi_member_families)[:15]:
        print(f"  {fid} (가장: {data['gajang']}): {', '.join(data['members'])}")
    if len(multi_member_families) > 15:
        print(f"  ... 외 {len(multi_member_families) - 15}개 가정")

    # 실제 업데이트 (배치 방식)
    if not dry_run and updates:
        print(f"\n=== 실제 업데이트 시작 (배치 방식) ===")

        # 배치 업데이트를 위한 데이터 준비
        batch_data = []
        for u in updates:
            cell_address = gspread.utils.rowcol_to_a1(u['row'], family_id_col)
            batch_data.append({
                'range': f"Members!{cell_address}",
                'values': [[u['new_family_id']]]
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
    parser = argparse.ArgumentParser(description='Members family_id 업데이트')
    parser.add_argument('--execute', action='store_true', help='실제 업데이트 실행')
    args = parser.parse_args()

    update_members_family_id(dry_run=not args.execute)
