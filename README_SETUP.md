# 초기 설정 가이드

## 1. Google Cloud Credentials 설정
데이터 마이그레이션 및 시스템 정상 작동을 위해 Google Sheets API 권한이 필요합니다.

1. **Google Cloud Console 접속**
   - [Google Cloud Console](https://console.cloud.google.com/)
   - 새 프로젝트 생성 (예: Yebom Saint System)

2. **API 활성화**
   - "Google Sheets API" 검색 및 활성화
   - "Google Drive API" 검색 및 활성화

3. **Service Account 생성**
   - "IAM 및 관리자" > "서비스 계정" > "서비스 계정 만들기"
   - 이름 입력 후 완료
   - 생성된 서비스 계정 클릭 > "키" 탭 > "키 추가" > "새 키 만들기" > "JSON"
   - 다운로드된 파일을 `credentials.json`으로 이름 변경

4. **파일 위치**
   - `credentials.json` 파일을 `g:\내 드라이브\g_dev\#yebom\credentials\` 폴더에 복사해주세요.
     (폴더가 없으면 생성해주세요)

5. **Google Sheet 공유**
   - 사용할 구글 시트를 엽니다.
   - [공유] 버튼 클릭
   - `credentials.json` 안의 `client_email` 주소(예: `xxx@xxx.iam.gserviceaccount.com`)를 추가하고 **편집자** 권한을 부여합니다.

## 2. 데이터 마이그레이션 실행
1. 터미널을 엽니다.
2. 다음 명령어를 실행합니다:
   ```powershell
   cd 'g:\내 드라이브\g_dev\#yebom'
   python saint-record-system/migration/migrate_data.py
   ```

## 3. 앱 실행
1. 앱 실행:
   ```powershell
   cd 'g:\내 드라이브\g_dev\#yebom\saint-record-system'
   streamlit run app.py
   ```
