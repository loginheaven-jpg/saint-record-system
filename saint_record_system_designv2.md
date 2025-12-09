# 성도기록부 시스템 설계서 (Saint Record System)
> **Version**: 1.1  
> **Date**: 2025-01-09  
> **Target**: Claude Code 구축용  
> **Changes**: 데이터 무결성, 동시성 처리, 인증, 검증 레이어 추가

---

## 1. 시스템 개요

### 1.1 목적
예봄교회의 교적부와 출석부를 통합한 **성도기록부 시스템** 구축. 현재 Google Sheets로 분산 관리되는 데이터를 구조화하고, 사용하기 쉬운 웹 인터페이스를 제공한다.

### 1.2 핵심 요구사항
| 구분 | 요구사항 |
|------|----------|
| 데이터 저장 | Google Sheets (기존 환경 유지, 비용 $0) |
| 사용자 인터페이스 | 웹앱 (출석 입력, 교적 관리, 검색/조회) |
| 확장성 | 향후 PostgreSQL 마이그레이션 가능한 구조 |
| 사용자 | 목자 (출석 입력), 교적 담당자 (교적 관리), 일반 (조회) |
| 데이터 무결성 | ID 충돌 방지, 중복 출석 방지, FK 정합성 검증 |
| 인증 | 비밀번호 보호 (Phase 1) |

### 1.3 현재 데이터 현황
- **성도 수**: 약 200명 (장년부 108, 청년부 36, 청소년부 23, 어린이부 32)
- **조직 구조**: 4개 부서, 15+ 목장
- **데이터 소스**: `2025출석부_목자용_.xlsx` (22개 시트)

### 1.4 설계 원칙
```
┌─────────────────────────────────────────────────────────────────┐
│                       핵심 설계 원칙                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 마이그레이션 준비 (Migration Ready)                         │
│     - 모든 비즈니스 로직은 Python에서 처리                       │
│     - Google Sheets 수식은 View 시트에만 허용                   │
│     - Pydantic 모델로 타입 안전성 확보                          │
│                                                                 │
│  2. 데이터 무결성 (Data Integrity)                              │
│     - ID 생성은 Apps Script에서 락 처리                         │
│     - 출석 저장은 Upsert 패턴 (삭제 후 삽입)                    │
│     - FK 참조 검증 후 저장                                      │
│                                                                 │
│  3. 단순성 (Simplicity)                                         │
│     - 최소 기능으로 시작, 점진적 확장                           │
│     - 복잡한 기능보다 안정적인 기본 기능                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 시스템 아키텍처

### 2.1 Phase 1: Google Sheets 기반 (현재 구축)

```
┌─────────────────────────────────────────────────────────────────┐
│                      시스템 아키텍처 (Phase 1)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [사용자]                                                       │
│   목자 / 교적담당자 / 일반성도                                    │
│          │                                                      │
│          ▼                                                      │
│   ┌──────────────────────────────────────┐                      │
│   │     🔐 Authentication Layer          │                      │
│   │     (Password Protection)            │                      │
│   └──────────────────────────────────────┘                      │
│                        │                                        │
│                        ▼                                        │
│   ┌──────────────────────────────────────┐                      │
│   │     Frontend (Streamlit Python)      │                      │
│   │  ┌──────────┐ ┌──────────┐ ┌──────┐ │                      │
│   │  │ 출석입력  │ │ 교적관리  │ │ 검색 │ │                      │
│   │  └──────────┘ └──────────┘ └──────┘ │                      │
│   │  ┌──────────┐ ┌──────────┐ ┌──────┐ │                      │
│   │  │ 대시보드  │ │ 보고서   │ │ 통계 │ │                      │
│   │  └──────────┘ └──────────┘ └──────┘ │                      │
│   └──────────────────────────────────────┘                      │
│                        │                                        │
│                        ▼                                        │
│   ┌──────────────────────────────────────┐                      │
│   │      ✅ Validation Layer             │                      │
│   │      (Pydantic Models)               │                      │
│   └──────────────────────────────────────┘                      │
│                        │                                        │
│                        ▼                                        │
│   ┌──────────────────────────────────────┐                      │
│   │      Backend API Layer               │                      │
│   │  ┌────────────────────────────────┐ │                      │
│   │  │ Google Apps Script             │ │                      │
│   │  │ - ID 생성 (Lock 처리)          │ │                      │
│   │  │ - 트랜잭션성 작업              │ │                      │
│   │  └────────────────────────────────┘ │                      │
│   │  ┌────────────────────────────────┐ │                      │
│   │  │ Python (gspread)               │ │                      │
│   │  │ - CRUD 작업                    │ │                      │
│   │  │ - 데이터 집계/통계             │ │                      │
│   │  └────────────────────────────────┘ │                      │
│   └──────────────────────────────────────┘                      │
│                        │                                        │
│                        ▼                                        │
│   ┌──────────────────────────────────────┐                      │
│   │         Google Sheets (DB)           │                      │
│   │  ┌────────┐ ┌────────┐ ┌──────────┐ │                      │
│   │  │Members │ │Families│ │Attendance│ │                      │
│   │  └────────┘ └────────┘ └──────────┘ │                      │
│   │  ┌────────┐ ┌────────┐ ┌──────────┐ │                      │
│   │  │_Seqs   │ │_Codes  │ │FaithEvts │ │                      │
│   │  └────────┘ └────────┘ └──────────┘ │                      │
│   └──────────────────────────────────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 기술 스택

| 레이어 | 기술 | 선정 이유 |
|--------|------|----------|
| Frontend | **Streamlit (Python)** | 빠른 개발, 데이터 중심 UI |
| Validation | **Pydantic** | 타입 안전성, 마이그레이션 준비 |
| Backend API | **Google Apps Script** | ID 생성 락 처리, Sheets 직접 연동 |
| Data Access | **gspread + Pandas** | Python 네이티브, 데이터 처리 |
| Database | **Google Sheets** | 비용 $0, 직접 편집 가능 |
| Hosting | **Streamlit Cloud** | 무료 호스팅 |

### 2.3 Phase 2: DB 마이그레이션 (향후)

```
┌─────────────────────────────────────────────────────────────────┐
│                 향후 마이그레이션 경로 (Phase 2)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [Phase 1 → Phase 2 전환 시점]                                  │
│   - 성도 수 500명 이상                                           │
│   - 동시 접속 10명 이상 필요                                      │
│   - 복잡한 통계/분석 요구                                        │
│                                                                 │
│   [Phase 2 아키텍처]                                             │
│   ┌──────────────────┐    ┌──────────────────┐                 │
│   │ Streamlit/React  │───▶│ FastAPI          │                 │
│   │   (Frontend)     │    │ (Backend)        │                 │
│   │   코드 재사용    │    │ Pydantic 재사용  │                 │
│   └──────────────────┘    └────────┬─────────┘                 │
│                                    │                            │
│                                    ▼                            │
│                          ┌──────────────────┐                   │
│                          │   PostgreSQL     │                   │
│                          │  (Railway/Supabase)                  │
│                          │  동일 스키마     │                   │
│                          └──────────────────┘                   │
│                                                                 │
│   [마이그레이션 이점]                                            │
│   - Pydantic 모델 그대로 사용                                    │
│   - 비즈니스 로직 Python에 있으므로 이식 용이                    │
│   - Sheets 수식 의존성 없음                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 데이터 구조 설계

### 3.1 Google Sheets 시트 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                    Google Sheets 구조                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📁 [시스템 시트] (수정 금지)                                    │
│      ├── _Sequences      : ID 시퀀스 관리 ⭐ NEW                │
│      ├── _Departments    : 부서 마스터                          │
│      ├── _Groups         : 목장 마스터                          │
│      ├── _Families       : 가정 마스터                          │
│      └── _Codes          : 코드 테이블 (직분, 상태 등)           │
│                                                                 │
│  📁 [핵심 데이터] (앱을 통해서만 수정)                           │
│      ├── Members         : 성도 정보 (교적)                     │
│      ├── FaithEvents     : 신앙이력 (등록, 세례, 삶공부 등)      │
│      └── Affiliations    : 조직 소속 이력                       │
│                                                                 │
│  📁 [출석 데이터] (연도별 분리)                                  │
│      ├── Attendance_2025 : 2025년 출석 기록                     │
│      └── Attendance_YYYY : 연도별 분리 (성능 최적화)            │
│                                                                 │
│  📁 [뷰 시트] (QUERY 함수, 읽기 전용)                           │
│      ├── View_장년부     : 장년부 명부                          │
│      ├── View_청년부     : 청년부 명부                          │
│      ├── View_회원교인   : 회원교인 명부 (공동의회용)            │
│      └── View_장기결석   : 3주 이상 결석자                       │
│                                                                 │
│  ⚠️ 주의: View 시트는 디버깅/관리자 확인용                      │
│          앱은 반드시 원본 테이블에서 읽고 Python으로 집계        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    SEQUENCES ||--|| SYSTEM : "manages"
    DEPARTMENTS ||--|{ GROUPS : "has"
    DEPARTMENTS ||--|{ MEMBERS : "belongs_to"
    GROUPS ||--|{ MEMBERS : "belongs_to"
    FAMILIES ||--|{ MEMBERS : "has"
    MEMBERS ||--o{ ATTENDANCE : "has"
    MEMBERS ||--o{ FAITH_EVENTS : "has"
    MEMBERS ||--o{ AFFILIATIONS : "has_history"

    SEQUENCES {
        string seq_name PK "member_id, family_id, etc"
        int last_value "마지막 발급 번호"
        string prefix "M, F, G, etc"
        int padding "5 (M00001)"
    }

    DEPARTMENTS {
        string dept_id PK "D01, D02, D03, D04"
        string name "장년부, 청년부, 청소년부, 어린이부"
        int sort_order "정렬순서"
    }

    GROUPS {
        string group_id PK "G01_01, G01_02..."
        string dept_id FK "소속 부서"
        string name "네팔, 러시아, 베트남1..."
        string leader_id FK "목자 성도ID"
    }

    FAMILIES {
        string family_id PK "F0001, F0002..."
        string family_name "가장 이름 기준"
        string head_id FK "가장 성도ID"
    }

    MEMBERS {
        string member_id PK "M00001, M00002..."
        string name "성명"
        string family_id FK "가정ID"
        string dept_id FK "현재 부서"
        string group_id FK "현재 목장"
        string gender "M/F"
        date birth_date "생년월일"
        string lunar_solar "Y양력/N음력"
        string phone "휴대전화"
        string address "주소"
        string church_role "교회직분"
        string group_role "목장직분"
        string member_type "회원교인/등록교인/기타"
        string status "재적/전출/사망/장기장결"
        string photo_url "사진URL(선택)"
        date created_at "등록일"
        date updated_at "수정일"
    }

    FAITH_EVENTS {
        string event_id PK "E00001_01..."
        string member_id FK "성도ID"
        string event_type "registration/baptism/life_study..."
        date event_date "이벤트일자"
        string officiant "집례자"
        string certificate_no "발급번호"
        string notes "비고"
    }

    AFFILIATIONS {
        string affil_id PK "A00001..."
        string member_id FK "성도ID"
        string dept_id FK "부서ID"
        string group_id FK "목장ID"
        date start_date "시작일"
        date end_date "종료일(NULL=현재)"
        string reason "변경사유"
    }

    ATTENDANCE {
        string attend_id PK "AT2025_W01_M00001"
        string member_id FK "성도ID"
        date attend_date "출석일자"
        string attend_type "1/0/2 (출석/결석/온라인)"
        int year "연도"
        int week_no "주차"
    }
```

### 3.3 시트별 컬럼 상세 정의

#### 3.3.1 _Sequences (시퀀스 관리) ⭐ NEW

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| seq_name | String | member_id | 시퀀스 이름 (PK) |
| last_value | Number | 215 | 마지막 발급 번호 |
| prefix | String | M | ID 접두어 |
| padding | Number | 5 | 자릿수 (M00001) |

**초기 데이터:**
```
seq_name    | last_value | prefix | padding
------------|------------|--------|--------
member_id   | 0          | M      | 5
family_id   | 0          | F      | 4
event_id    | 0          | E      | 5
affil_id    | 0          | A      | 5
```

**ID 생성 규칙:**
- `member_id`: M + 5자리 (M00001 ~ M99999)
- `family_id`: F + 4자리 (F0001 ~ F9999)
- `attend_id`: AT + 연도 + _W + 주차 + _ + member_id (예: AT2025_W01_M00001)
  - 출석 ID는 복합키로 시퀀스 불필요

#### 3.3.2 _Departments (부서 마스터)

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| dept_id | String | D01 | 부서 ID (PK) |
| name | String | 장년부 | 부서명 |
| sort_order | Number | 1 | 정렬 순서 |

**초기 데이터:**
```
dept_id | name     | sort_order
--------|----------|------------
D01     | 장년부   | 1
D02     | 청년부   | 2
D03     | 청소년부 | 3
D04     | 어린이부 | 4
```

#### 3.3.3 _Groups (목장 마스터)

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| group_id | String | G01_01 | 목장 ID (PK) |
| dept_id | String | D01 | 소속 부서 (FK) |
| name | String | 네팔 | 목장명 |
| leader_id | String | M00012 | 목자 성도ID (FK) |

**초기 데이터 (예시):**
```
group_id | dept_id | name     | leader_id
---------|---------|----------|----------
G01_01   | D01     | 네팔     | M00012
G01_02   | D01     | 러시아   | M00025
G01_03   | D01     | 필리핀   | M00038
G01_04   | D01     | 태국     | M00045
G01_05   | D01     | 베냉     | M00052
G01_06   | D01     | 콩고     | M00060
G01_07   | D01     | 칠레     | M00068
G01_08   | D01     | 철원     | M00075
G02_01   | D02     | 베트남1  | M00100
G02_02   | D02     | 베트남2  | M00110
G02_03   | D02     | 아나니아 | M00120
G02_04   | D02     | 카메룬   | M00130
G03_01   | D03     | 청소년   | M00150
G04_01   | D04     | 화평반   | M00160
G04_02   | D04     | 기쁨반   | M00165
G04_03   | D04     | 사랑반   | M00170
```

#### 3.3.4 _Codes (코드 테이블)

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| code_type | String | CHURCH_ROLE | 코드 유형 |
| code | String | R01 | 코드값 |
| name | String | 담임목사 | 코드명 |
| sort_order | Number | 1 | 정렬순서 |

**코드 데이터:**
```
code_type    | code | name     | sort_order
-------------|------|----------|------------
CHURCH_ROLE  | R01  | 담임목사 | 1
CHURCH_ROLE  | R02  | 목사     | 2
CHURCH_ROLE  | R03  | 강도사   | 3
CHURCH_ROLE  | R04  | 장로     | 4
CHURCH_ROLE  | R05  | 권사     | 5
CHURCH_ROLE  | R06  | 안수집사 | 6
CHURCH_ROLE  | R07  | 집사     | 7
CHURCH_ROLE  | R08  | 성도     | 8
GROUP_ROLE   | G01  | 목자     | 1
GROUP_ROLE   | G02  | 목녀     | 2
GROUP_ROLE   | G03  | 목원     | 3
MEMBER_TYPE  | T01  | 회원교인 | 1
MEMBER_TYPE  | T02  | 등록교인 | 2
MEMBER_TYPE  | T03  | 기타     | 3
STATUS       | S01  | 재적     | 1
STATUS       | S02  | 전출     | 2
STATUS       | S03  | 사망     | 3
STATUS       | S04  | 장기장결 | 4
ATTEND_TYPE  | 1    | 출석     | 1
ATTEND_TYPE  | 0    | 결석     | 2
ATTEND_TYPE  | 2    | 온라인   | 3
EVENT_TYPE   | E01  | registration | 1
EVENT_TYPE   | E02  | newcomer     | 2
EVENT_TYPE   | E03  | baptism      | 3
EVENT_TYPE   | E04  | confirmation | 4
EVENT_TYPE   | E05  | life_study   | 5
EVENT_TYPE   | E06  | confirm_study| 6
EVENT_TYPE   | E07  | new_life     | 7
```

#### 3.3.5 Members (성도 정보)

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| member_id | String | M00001 | 성도 ID (PK) |
| name | String | 계창완 | 성명 |
| family_id | String | F0001 | 가정 ID (FK) |
| dept_id | String | D01 | 현재 부서 (FK) |
| group_id | String | G01_01 | 현재 목장 (FK) |
| gender | String | M | 성별 (M/F) |
| birth_date | Date | 1969-03-11 | 생년월일 |
| lunar_solar | String | Y | 양력Y/음력N |
| phone | String | 010-4090-1148 | 휴대전화 |
| address | String | 경기도 용인시... | 주소 |
| church_role | String | 성도 | 교회직분 |
| group_role | String | 목원 | 목장직분 |
| member_type | String | 회원교인 | 교인구분 |
| status | String | 재적 | 상태 |
| photo_url | String | (URL) | 사진 (선택) |
| created_at | Date | 2017-10-29 | 최초등록일 |
| updated_at | Date | 2025-01-05 | 최종수정일 |

#### 3.3.6 FaithEvents (신앙이력)

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| event_id | String | E00001 | 이벤트 ID (PK) |
| member_id | String | M00001 | 성도 ID (FK) |
| event_type | String | registration | 이벤트 유형 |
| event_date | Date | 2017-10-29 | 이벤트 일자 |
| officiant | String | 최병희 | 집례자 |
| certificate_no | String | 2021-01-01 | 발급번호 |
| notes | String | | 비고 |

**event_type 값:**
- `registration`: 등록
- `newcomer`: 새신자반 수료
- `baptism`: 세례/침례
- `confirmation`: 입교
- `infant_baptism`: 유아세례
- `life_study`: 생명의삶 수료
- `confirm_study`: 확신의삶 수료
- `new_life`: 새로운삶 수료
- `transfer_out`: 전출
- `transfer_in`: 전입

#### 3.3.7 Affiliations (조직 소속 이력)

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| affil_id | String | A00001 | 이력 ID (PK) |
| member_id | String | M00001 | 성도 ID (FK) |
| dept_id | String | D01 | 부서 ID (FK) |
| group_id | String | G01_01 | 목장 ID (FK) |
| start_date | Date | 2017-10-29 | 시작일 |
| end_date | Date | (NULL) | 종료일 |
| reason | String | 최초등록 | 변경사유 |

#### 3.3.8 Attendance_YYYY (출석 기록)

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| attend_id | String | AT2025_W01_M00001 | 출석 ID (PK, 복합키) |
| member_id | String | M00001 | 성도 ID (FK) |
| attend_date | Date | 2025-01-05 | 출석일 |
| attend_type | String | 1 | 1=출석, 0=결석, 2=온라인 |
| year | Number | 2025 | 연도 |
| week_no | Number | 1 | 주차 |

**attend_id 생성 규칙:**
- 형식: `AT{연도}_W{주차:02d}_{member_id}`
- 예시: `AT2025_W01_M00001`
- 복합키 역할로 중복 방지

---

## 4. 출석 코드 체계 ⭐ NEW

### 4.1 코드 정의

```
┌─────────────────────────────────────────────────────────────────┐
│                      출석 코드 체계                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [DB 저장값]     [의미]        [UI 표시]     [집계 시]          │
│  ─────────────────────────────────────────────────────────────  │
│     '1'          출석          출석 ✓        출석 인원에 포함   │
│     '0'          결석          결석 ✗        결석 인원에 포함   │
│     '2'          온라인        온라인 📱     출석 인원에 포함   │
│     NULL/빈값    미기록        -             집계 제외          │
│                                                                 │
│  [선택 이유]                                                    │
│  - 기존 Excel 데이터와 호환 (1, 0 유지)                         │
│  - 숫자로 집계 용이 (SUM 가능)                                  │
│  - PostgreSQL 마이그레이션 시 INTEGER로 변환 가능               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Python Enum 정의

```python
# utils/enums.py
from enum import Enum

class AttendType(str, Enum):
    """출석 유형"""
    PRESENT = '1'   # 출석
    ABSENT = '0'    # 결석
    ONLINE = '2'    # 온라인
    
    @property
    def display_name(self) -> str:
        """UI 표시용 한글명"""
        names = {
            '1': '출석',
            '0': '결석',
            '2': '온라인'
        }
        return names[self.value]
    
    @property
    def is_attended(self) -> bool:
        """출석으로 집계할지 여부"""
        return self.value in ('1', '2')
    
    @classmethod
    def from_display(cls, name: str) -> 'AttendType':
        """한글명에서 Enum으로 변환"""
        mapping = {
            '출석': cls.PRESENT,
            '결석': cls.ABSENT,
            '온라인': cls.ONLINE
        }
        return mapping.get(name, cls.ABSENT)


class MemberStatus(str, Enum):
    """성도 상태"""
    ACTIVE = '재적'
    TRANSFERRED = '전출'
    DECEASED = '사망'
    LONG_ABSENT = '장기장결'


class MemberType(str, Enum):
    """교인 구분"""
    FULL = '회원교인'
    REGISTERED = '등록교인'
    OTHER = '기타'


class ChurchRole(str, Enum):
    """교회 직분"""
    SENIOR_PASTOR = '담임목사'
    PASTOR = '목사'
    EVANGELIST = '강도사'
    ELDER = '장로'
    KWONSA = '권사'
    ORDAINED_DEACON = '안수집사'
    DEACON = '집사'
    MEMBER = '성도'


class GroupRole(str, Enum):
    """목장 직분"""
    LEADER = '목자'
    CO_LEADER = '목녀'
    MEMBER = '목원'
```

---

## 5. 회원교인 판정 로직

### 5.1 회원교인 조건
```
회원교인 = (세례 완료 AND 생명의삶 수료) 
          OR (2020년 가정교회 출범시 기존 회원)
```

### 5.2 Python 구현 (Sheets 수식 사용 안 함)

```python
# utils/business_logic.py
from typing import List, Set
import pandas as pd

def get_eligible_full_members(
    members_df: pd.DataFrame,
    faith_events_df: pd.DataFrame
) -> Set[str]:
    """
    회원교인 자격이 있는 성도 ID 목록 반환
    
    조건:
    1. 세례 완료 AND 생명의삶 수료
    2. 또는 2020년 가정교회 출범시 기존 회원 (member_type이 이미 '회원교인')
    """
    # 이미 회원교인인 성도 (기존 회원)
    existing_full = set(
        members_df[members_df['member_type'] == '회원교인']['member_id']
    )
    
    # 세례받은 성도
    baptized = set(
        faith_events_df[faith_events_df['event_type'] == 'baptism']['member_id']
    )
    
    # 생명의삶 수료한 성도
    life_study = set(
        faith_events_df[faith_events_df['event_type'] == 'life_study']['member_id']
    )
    
    # 신규 자격자: 세례 AND 생명의삶
    new_eligible = baptized & life_study
    
    # 전체 회원교인 자격자
    return existing_full | new_eligible


def update_member_types(
    sheets_api,
    members_df: pd.DataFrame,
    faith_events_df: pd.DataFrame
) -> int:
    """
    회원교인 자격 자동 업데이트
    Returns: 업데이트된 성도 수
    """
    eligible = get_eligible_full_members(members_df, faith_events_df)
    
    updated_count = 0
    for _, member in members_df.iterrows():
        member_id = member['member_id']
        current_type = member['member_type']
        
        should_be_full = member_id in eligible
        is_full = current_type == '회원교인'
        
        if should_be_full and not is_full:
            sheets_api.update_member(member_id, {'member_type': '회원교인'})
            updated_count += 1
    
    return updated_count
```

---

## 6. 데이터 무결성 ⭐ NEW

### 6.1 ID 생성 (Apps Script - Lock 사용)

```javascript
// apps_script/Code.gs

/**
 * 새로운 ID 생성 (동시성 안전)
 * @param {string} seqName - 시퀀스 이름 (member_id, family_id 등)
 * @returns {string} 새로운 ID
 */
function generateId(seqName) {
  const lock = LockService.getScriptLock();
  
  try {
    // 30초 대기 후 락 획득 실패 시 예외
    lock.waitLock(30000);
    
    const sheet = SpreadsheetApp.getActiveSpreadsheet()
                    .getSheetByName('_Sequences');
    const data = sheet.getDataRange().getValues();
    
    // 헤더: seq_name, last_value, prefix, padding
    let rowIndex = -1;
    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === seqName) {
        rowIndex = i;
        break;
      }
    }
    
    if (rowIndex === -1) {
      throw new Error('Unknown sequence: ' + seqName);
    }
    
    const lastValue = data[rowIndex][1];
    const prefix = data[rowIndex][2];
    const padding = data[rowIndex][3];
    
    // 새 값 계산
    const newValue = lastValue + 1;
    
    // 시트 업데이트
    sheet.getRange(rowIndex + 1, 2).setValue(newValue);
    
    // ID 생성
    const newId = prefix + String(newValue).padStart(padding, '0');
    
    return newId;
    
  } finally {
    lock.releaseLock();
  }
}

/**
 * 성도 ID 생성
 */
function generateMemberId() {
  return generateId('member_id');
}

/**
 * 가정 ID 생성
 */
function generateFamilyId() {
  return generateId('family_id');
}

/**
 * 신앙이력 ID 생성
 */
function generateEventId() {
  return generateId('event_id');
}

/**
 * Web API 엔드포인트
 */
function doGet(e) {
  const action = e.parameter.action;
  
  let result;
  
  switch(action) {
    case 'generateMemberId':
      result = { success: true, id: generateMemberId() };
      break;
    case 'generateFamilyId':
      result = { success: true, id: generateFamilyId() };
      break;
    case 'generateEventId':
      result = { success: true, id: generateEventId() };
      break;
    default:
      result = { success: false, error: 'Unknown action' };
  }
  
  return ContentService
    .createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}
```

### 6.2 출석 저장 (Upsert 패턴) ⭐ NEW

```python
# utils/sheets_api.py (일부)

def save_attendance(self, records: List[Dict]) -> Dict:
    """
    출석 저장 (Upsert 패턴: 삭제 후 삽입)
    
    Args:
        records: 출석 레코드 리스트
            - member_id: 성도 ID
            - attend_date: 출석일
            - attend_type: '1'/'0'/'2'
            - year: 연도
            - week_no: 주차
    
    Returns:
        {'success': bool, 'inserted': int, 'deleted': int}
    """
    if not records:
        return {'success': False, 'error': 'No records provided'}
    
    year = records[0]['year']
    week_no = records[0]['week_no']
    member_ids = [r['member_id'] for r in records]
    
    sheet_name = f'Attendance_{year}'
    sheet = self.get_sheet(sheet_name)
    
    # 1. 기존 데이터 조회
    all_data = sheet.get_all_records()
    
    # 2. 삭제할 행 찾기 (해당 주차 + 해당 성도들)
    rows_to_delete = []
    for i, row in enumerate(all_data):
        if (row.get('week_no') == week_no and 
            row.get('member_id') in member_ids):
            rows_to_delete.append(i + 2)  # 헤더(1) + 0-index 보정
    
    # 3. 역순으로 삭제 (인덱스 밀림 방지)
    deleted_count = 0
    for row_num in sorted(rows_to_delete, reverse=True):
        sheet.delete_rows(row_num)
        deleted_count += 1
    
    # 4. 새 데이터 삽입
    inserted_count = 0
    for record in records:
        attend_id = f"AT{year}_W{week_no:02d}_{record['member_id']}"
        row = [
            attend_id,
            record['member_id'],
            record['attend_date'],
            record['attend_type'],
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
```

### 6.3 FK 참조 검증

```python
# utils/validators.py

from pydantic import BaseModel, validator, root_validator
from typing import Optional
from datetime import date
from enum import Enum

class AttendType(str, Enum):
    PRESENT = '1'
    ABSENT = '0'
    ONLINE = '2'


class MemberCreate(BaseModel):
    """성도 생성 시 검증"""
    name: str
    dept_id: str
    group_id: str
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    church_role: str = '성도'
    group_role: str = '목원'
    member_type: str = '등록교인'
    status: str = '재적'
    
    @validator('name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('이름은 필수입니다')
        return v.strip()
    
    @validator('gender')
    def valid_gender(cls, v):
        if v and v not in ('M', 'F'):
            raise ValueError('성별은 M 또는 F여야 합니다')
        return v
    
    @root_validator
    def group_belongs_to_dept(cls, values):
        """목장이 부서에 속하는지 검증"""
        dept_id = values.get('dept_id')
        group_id = values.get('group_id')
        
        if dept_id and group_id:
            # group_id 형식: G01_01 (G + 부서번호 + _ + 목장번호)
            # dept_id 형식: D01
            expected_prefix = f"G{dept_id[1:]}_"
            if not group_id.startswith(expected_prefix):
                raise ValueError(
                    f'목장 {group_id}은(는) 부서 {dept_id}에 속하지 않습니다'
                )
        
        return values


class MemberUpdate(BaseModel):
    """성도 수정 시 검증"""
    name: Optional[str] = None
    dept_id: Optional[str] = None
    group_id: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    church_role: Optional[str] = None
    group_role: Optional[str] = None
    member_type: Optional[str] = None
    status: Optional[str] = None
    
    @validator('name')
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('이름은 비어있을 수 없습니다')
        return v.strip() if v else v


class AttendanceCreate(BaseModel):
    """출석 생성 시 검증"""
    member_id: str
    attend_date: date
    attend_type: AttendType
    year: int
    week_no: int
    
    @validator('member_id')
    def valid_member_id(cls, v):
        if not v.startswith('M') or len(v) != 6:
            raise ValueError('유효하지 않은 성도 ID입니다')
        return v
    
    @validator('week_no')
    def valid_week_no(cls, v):
        if not 1 <= v <= 53:
            raise ValueError('주차는 1~53 사이여야 합니다')
        return v


class FaithEventCreate(BaseModel):
    """신앙이력 생성 시 검증"""
    member_id: str
    event_type: str
    event_date: date
    officiant: Optional[str] = None
    certificate_no: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('event_type')
    def valid_event_type(cls, v):
        valid_types = [
            'registration', 'newcomer', 'baptism', 'confirmation',
            'infant_baptism', 'life_study', 'confirm_study', 
            'new_life', 'transfer_out', 'transfer_in'
        ]
        if v not in valid_types:
            raise ValueError(f'유효하지 않은 이벤트 유형입니다: {v}')
        return v
```

---

## 7. 인증 (Authentication) ⭐ NEW

### 7.1 Phase 1: 단순 비밀번호 보호

```python
# utils/auth.py

import streamlit as st
import hmac

def check_password() -> bool:
    """
    비밀번호 인증 체크
    
    Returns:
        True if authenticated, False otherwise
    """
    
    def password_entered():
        """비밀번호 입력 콜백"""
        if hmac.compare_digest(
            st.session_state["password"],
            st.secrets["app_password"]
        ):
            st.session_state["authenticated"] = True
            del st.session_state["password"]  # 비밀번호 세션에서 제거
        else:
            st.session_state["authenticated"] = False

    # 이미 인증된 경우
    if st.session_state.get("authenticated", False):
        return True
    
    # 로그인 폼 표시
    st.title("🔐 성도기록부 로그인")
    st.text_input(
        "비밀번호를 입력하세요",
        type="password",
        key="password",
        on_change=password_entered
    )
    
    if "authenticated" in st.session_state and not st.session_state["authenticated"]:
        st.error("😕 비밀번호가 틀렸습니다")
    
    return False


def logout():
    """로그아웃"""
    st.session_state["authenticated"] = False


def require_auth(func):
    """
    인증 필요 데코레이터
    
    Usage:
        @require_auth
        def main():
            st.write("Protected content")
    """
    def wrapper(*args, **kwargs):
        if check_password():
            return func(*args, **kwargs)
        else:
            st.stop()
    return wrapper
```

### 7.2 사용 예시

```python
# app.py

import streamlit as st
from utils.auth import check_password, logout

st.set_page_config(
    page_title="성도기록부",
    page_icon="⛪",
    layout="wide"
)

# 인증 체크
if not check_password():
    st.stop()

# 인증 후 메인 컨텐츠
st.sidebar.title("⛪ 성도기록부")

# 로그아웃 버튼
if st.sidebar.button("로그아웃"):
    logout()
    st.rerun()

st.sidebar.markdown("---")

# 메인 대시보드
st.title("📊 대시보드")
# ... 나머지 코드
```

### 7.3 Secrets 설정

```toml
# .streamlit/secrets.toml (로컬 개발용)

app_password = "your_secure_password_here"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

---

## 8. 사용자 인터페이스 설계

### 8.1 화면 구성

```
┌─────────────────────────────────────────────────────────────────┐
│                        성도기록부 시스템                         │
├─────────────────────────────────────────────────────────────────┤
│  [사이드바]              │  [메인 컨텐츠]                        │
│  ┌───────────────┐      │                                      │
│  │ 🔓 로그아웃    │      │  ┌────────────────────────────────┐ │
│  │ ───────────── │      │  │                                │ │
│  │ 🏠 대시보드    │      │  │     선택된 메뉴의 컨텐츠        │ │
│  │ 📋 출석 입력   │      │  │                                │ │
│  │ 👤 성도 관리   │      │  │                                │ │
│  │ 👨‍👩‍👧 가정 관리   │      │  │                                │ │
│  │ 🔍 검색       │      │  │                                │ │
│  │ 📊 통계/보고서 │      │  │                                │ │
│  │ ⚙️ 설정       │      │  │                                │ │
│  └───────────────┘      │  └────────────────────────────────┘ │
│                         │                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 화면별 상세

#### 8.2.1 대시보드 (Home)
```
┌─────────────────────────────────────────────────────────────────┐
│  대시보드                                           2025-01-05  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ 전체성도  │ │ 금주출석  │ │ 출석률   │ │ 신규등록  │          │
│  │   199    │ │   148    │ │  74.4%   │ │    2     │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                 │
│  [부서별 출석 현황]                    [최근 4주 출석 추이]      │
│  ┌─────────────────────┐            ┌─────────────────────┐   │
│  │ 장년부  85/108 79%  │            │     📊 Bar Chart    │   │
│  │ 청년부  27/36  75%  │            │                     │   │
│  │ 청소년부 14/23 61%  │            │                     │   │
│  │ 어린이부 22/32 69%  │            └─────────────────────┘   │
│  └─────────────────────┘                                       │
│                                                                 │
│  [알림]                                                         │
│  ⚠️ 3주 연속 결석: 김OO, 박OO 외 3명                            │
│  🎂 이번 주 생일: 이OO (1/7), 최OO (1/9)                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 8.2.2 출석 입력 (Attendance Input)
```
┌─────────────────────────────────────────────────────────────────┐
│  출석 입력                                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  날짜: [2025-01-05 ▼]   부서: [장년부 ▼]   목장: [네팔 ▼]       │
│                                                                 │
│  ⚠️ 이미 저장된 출석이 있습니다. 수정하면 기존 데이터를 덮어씁니다. │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ □ 전체선택                                               │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ ☑️ 계창완     목원    010-4090-1148    [출석▼]          │   │
│  │ ☑️ 김 건     목원    010-3295-5125    [출석▼]          │   │
│  │ ☑️ 김미연    목녀    010-9876-9133    [출석▼]          │   │
│  │ ☐ 박보현    목원    010-8297-0001    [결석▼]          │   │
│  │ ☑️ 신성아    목원    010-3045-5951    [온라인▼]        │   │
│  │ ...                                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [출석: 8]  [온라인: 1]  [결석: 2]  [합계: 11]                  │
│                                                                 │
│                              [취소]  [💾 저장]                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 8.2.3 성도 관리 (Member Management)
```
┌─────────────────────────────────────────────────────────────────┐
│  성도 관리                                    [+ 신규 등록]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  검색: [____________]  부서: [전체▼]  상태: [재적▼]  [검색]     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ID      이름    부서    목장   직분   구분     연락처    │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ M00001  계창완  장년부  네팔   성도   회원교인  010-4090 │   │
│  │ M00002  김 건  장년부  네팔   성도   회원교인  010-3295 │   │
│  │ M00003  김미연  장년부  네팔   권사   회원교인  010-9876 │   │
│  │ ...                                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [◀ 이전]  페이지 1/10  [다음 ▶]                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 8.2.4 성도 상세 (Member Detail)
```
┌─────────────────────────────────────────────────────────────────┐
│  성도 상세                                    [수정] [삭제]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────┐  이름: 계창완                                        │
│  │ 사진  │  생년월일: 1969-03-11 (양력, 56세)                   │
│  │      │  연락처: 010-4090-1148                               │
│  └──────┘  주소: 경기도 용인시 기흥구 이현로 30-7번길 102-1202  │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  [소속 정보]                                                    │
│  부서: 장년부    목장: 네팔    교회직분: 성도    목장직분: 목원  │
│  구분: 회원교인  상태: 재적    등록일: 2017-10-29               │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  [가정 정보]                                                    │
│  가정: 계창완 가정 (본인: 가장)                                 │
│  가족: (없음)                                                   │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  [신앙 이력]                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 2017-10-29  등록                                        │   │
│  │ 2020-10-15  생명의삶 수료                                │   │
│  │ 2022-01-17  새신자반 수료                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  [출석 이력] (최근 12주)                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1/5:✓  1/12:✓  1/19:✓  1/26:✗  2/2:✓  2/9:📱 ...       │   │
│  └─────────────────────────────────────────────────────────┘   │
│  출석률: 48/49 (98%)                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. API 설계

### 9.1 Apps Script API 엔드포인트

| Method | Action | Description |
|--------|--------|-------------|
| GET | generateMemberId | 새 성도 ID 생성 (락 처리) |
| GET | generateFamilyId | 새 가정 ID 생성 (락 처리) |
| GET | generateEventId | 새 이벤트 ID 생성 (락 처리) |

### 9.2 Python SheetsAPI 메서드

| Method | Description | Validation |
|--------|-------------|------------|
| get_members(filters) | 성도 목록 조회 | - |
| get_member_by_id(id) | 성도 상세 조회 | - |
| create_member(data) | 성도 등록 | MemberCreate |
| update_member(id, data) | 성도 수정 | MemberUpdate |
| delete_member(id) | 성도 삭제 (상태변경) | - |
| get_attendance(year, date) | 출석 조회 | - |
| save_attendance(records) | 출석 저장 (Upsert) | AttendanceCreate |
| get_faith_events(member_id) | 신앙이력 조회 | - |
| add_faith_event(data) | 신앙이력 추가 | FaithEventCreate |
| get_departments() | 부서 목록 | - |
| get_groups(dept_id) | 목장 목록 | - |

### 9.3 Apps Script 전체 코드

```javascript
// apps_script/Code.gs

/**
 * 새로운 ID 생성 (동시성 안전)
 */
function generateId(seqName) {
  const lock = LockService.getScriptLock();
  
  try {
    lock.waitLock(30000);
    
    const sheet = SpreadsheetApp.getActiveSpreadsheet()
                    .getSheetByName('_Sequences');
    const data = sheet.getDataRange().getValues();
    
    let rowIndex = -1;
    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === seqName) {
        rowIndex = i;
        break;
      }
    }
    
    if (rowIndex === -1) {
      throw new Error('Unknown sequence: ' + seqName);
    }
    
    const lastValue = data[rowIndex][1];
    const prefix = data[rowIndex][2];
    const padding = data[rowIndex][3];
    
    const newValue = lastValue + 1;
    sheet.getRange(rowIndex + 1, 2).setValue(newValue);
    
    const newId = prefix + String(newValue).padStart(padding, '0');
    
    return newId;
    
  } finally {
    lock.releaseLock();
  }
}

function generateMemberId() {
  return generateId('member_id');
}

function generateFamilyId() {
  return generateId('family_id');
}

function generateEventId() {
  return generateId('event_id');
}

function generateAffilId() {
  return generateId('affil_id');
}

/**
 * Web API 엔드포인트
 */
function doGet(e) {
  const action = e.parameter.action;
  
  let result;
  
  try {
    switch(action) {
      case 'generateMemberId':
        result = { success: true, id: generateMemberId() };
        break;
      case 'generateFamilyId':
        result = { success: true, id: generateFamilyId() };
        break;
      case 'generateEventId':
        result = { success: true, id: generateEventId() };
        break;
      case 'generateAffilId':
        result = { success: true, id: generateAffilId() };
        break;
      default:
        result = { success: false, error: 'Unknown action: ' + action };
    }
  } catch (error) {
    result = { success: false, error: error.message };
  }
  
  return ContentService
    .createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * 테스트 함수
 */
function testGenerateId() {
  Logger.log('Member ID: ' + generateMemberId());
  Logger.log('Family ID: ' + generateFamilyId());
}
```

---

## 10. 디렉토리 구조

```
saint-record-system/
├── README.md                    # 프로젝트 설명
├── requirements.txt             # Python 의존성
├── .streamlit/
│   ├── config.toml              # Streamlit 설정
│   └── secrets.toml             # 비밀번호, 인증정보 (gitignore)
├── app.py                       # Streamlit 메인 앱
├── pages/
│   ├── 1_📋_출석입력.py          # 출석 입력 페이지
│   ├── 2_👤_성도관리.py          # 성도 관리 페이지
│   ├── 3_👨‍👩‍👧_가정관리.py          # 가정 관리 페이지
│   ├── 4_🔍_검색.py              # 검색 페이지
│   ├── 5_📊_통계.py              # 통계/보고서 페이지
│   └── 6_⚙️_설정.py              # 설정 페이지
├── utils/
│   ├── __init__.py
│   ├── auth.py                  # 인증 모듈 ⭐ NEW
│   ├── enums.py                 # Enum 정의 ⭐ NEW
│   ├── validators.py            # Pydantic 검증 모델 ⭐ NEW
│   ├── sheets_api.py            # Google Sheets API 래퍼
│   ├── apps_script_client.py    # Apps Script API 클라이언트 ⭐ NEW
│   ├── data_processor.py        # 데이터 처리 유틸리티
│   └── business_logic.py        # 비즈니스 로직 ⭐ NEW
├── components/
│   ├── __init__.py
│   ├── member_card.py           # 성도 카드 컴포넌트
│   ├── attendance_grid.py       # 출석 그리드 컴포넌트
│   └── charts.py                # 차트 컴포넌트
├── migration/
│   ├── migrate_data.py          # 데이터 마이그레이션 스크립트
│   └── validate_data.py         # 데이터 검증 스크립트
├── apps_script/
│   ├── Code.gs                  # Google Apps Script 메인 (ID 생성)
│   └── appsscript.json          # Apps Script 설정
├── tests/                       # 테스트 코드 ⭐ NEW
│   ├── __init__.py
│   ├── test_validators.py
│   ├── test_sheets_api.py
│   └── test_business_logic.py
└── credentials/
    └── .gitkeep                 # credentials.json 위치 (gitignore)
```

---

## 11. 데이터 마이그레이션

### 11.1 마이그레이션 순서

```
┌─────────────────────────────────────────────────────────────────┐
│                    데이터 마이그레이션 순서                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: 시스템 시트 생성                                        │
│  ├── _Sequences 시트 생성 (ID 시퀀스) ⭐ NEW                    │
│  ├── _Departments 시트 생성 (4개 부서)                          │
│  ├── _Groups 시트 생성 (목장 목록)                              │
│  └── _Codes 시트 생성 (코드 테이블)                             │
│                                                                 │
│  Step 2: 가정 데이터 추출                                        │
│  └── 기존 시트의 '가장' 컬럼 → _Families 시트 생성              │
│                                                                 │
│  Step 3: 성도 데이터 통합                                        │
│  ├── 장년부 시트 → Members                                      │
│  ├── 청년부 시트 → Members                                      │
│  ├── 청소년부 시트 → Members                                    │
│  ├── 어린이부 시트 → Members                                    │
│  ├── 중복 제거 및 ID 생성                                       │
│  └── _Sequences.member_id.last_value 업데이트 ⭐ NEW            │
│                                                                 │
│  Step 4: 신앙이력 통합                                          │
│  ├── 각 시트의 등록일 → FaithEvents (registration)             │
│  ├── 새신자반 시트 → FaithEvents (newcomer)                    │
│  ├── 세례현황 시트 → FaithEvents (baptism)                     │
│  ├── 생명의삶 시트 → FaithEvents (life_study)                  │
│  ├── 확신의삶 시트 → FaithEvents (confirm_study)               │
│  └── 새로운삶 시트 → FaithEvents (new_life)                    │
│                                                                 │
│  Step 5: 출석 데이터 변환                                        │
│  ├── 출석부 시트 → Attendance_2025                             │
│  ├── 2024년 시트 → Attendance_2024                             │
│  ├── 2023년 시트 → Attendance_2023                             │
│  ├── 2022년/2021이전 시트 → Attendance_2022, Attendance_2021   │
│  └── attend_type: 1→'1', 0→'0', 온라인→'2' 변환 ⭐ NEW         │
│                                                                 │
│  Step 6: 검증                                                   │
│  ├── 성도 수 일치 확인                                          │
│  ├── 중복 데이터 확인                                           │
│  ├── FK 참조 무결성 확인 (Pydantic으로 검증) ⭐ NEW             │
│  └── 회원교인 자동 판정 실행                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 11.2 마이그레이션 스크립트

```python
# migration/migrate_data.py

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Dict, List
import sys
sys.path.append('..')
from utils.validators import MemberCreate, AttendanceCreate
from utils.enums import AttendType

class DataMigrator:
    def __init__(self, excel_path: str, sheet_url: str):
        self.excel_path = excel_path
        self.sheet_url = sheet_url
        self.client = self._connect_sheets()
        self.spreadsheet = self.client.open_by_url(sheet_url)
        self.errors = []
        
    def _connect_sheets(self):
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            '../credentials/credentials.json', scope
        )
        return gspread.authorize(creds)
    
    def migrate_all(self):
        """전체 마이그레이션 실행"""
        print("=== 데이터 마이그레이션 시작 ===")
        
        # Step 1: 시스템 시트
        print("\n[Step 1] 시스템 시트 생성...")
        self.create_sequences_sheet()
        self.create_departments_sheet()
        self.create_codes_sheet()
        
        # Step 2: 목장 데이터
        print("\n[Step 2] 목장 데이터 추출...")
        self.extract_groups()
        
        # Step 3: 성도 데이터
        print("\n[Step 3] 성도 데이터 통합...")
        member_count = self.migrate_members()
        print(f"  - {member_count}명 성도 마이그레이션 완료")
        
        # Step 4: 신앙이력
        print("\n[Step 4] 신앙이력 통합...")
        event_count = self.migrate_faith_events()
        print(f"  - {event_count}건 신앙이력 마이그레이션 완료")
        
        # Step 5: 출석 데이터
        print("\n[Step 5] 출석 데이터 변환...")
        attend_count = self.migrate_attendance()
        print(f"  - {attend_count}건 출석 마이그레이션 완료")
        
        # Step 6: 검증
        print("\n[Step 6] 데이터 검증...")
        self.validate_all()
        
        print("\n=== 마이그레이션 완료 ===")
        if self.errors:
            print(f"\n⚠️ {len(self.errors)}건의 오류 발생:")
            for err in self.errors[:10]:
                print(f"  - {err}")
    
    def create_sequences_sheet(self):
        """_Sequences 시트 생성"""
        try:
            sheet = self.spreadsheet.worksheet('_Sequences')
            sheet.clear()
        except:
            sheet = self.spreadsheet.add_worksheet('_Sequences', 10, 4)
        
        data = [
            ['seq_name', 'last_value', 'prefix', 'padding'],
            ['member_id', 0, 'M', 5],
            ['family_id', 0, 'F', 4],
            ['event_id', 0, 'E', 5],
            ['affil_id', 0, 'A', 5],
        ]
        sheet.update('A1:D5', data)
    
    def create_departments_sheet(self):
        """_Departments 시트 생성"""
        try:
            sheet = self.spreadsheet.worksheet('_Departments')
            sheet.clear()
        except:
            sheet = self.spreadsheet.add_worksheet('_Departments', 10, 3)
        
        data = [
            ['dept_id', 'name', 'sort_order'],
            ['D01', '장년부', 1],
            ['D02', '청년부', 2],
            ['D03', '청소년부', 3],
            ['D04', '어린이부', 4],
        ]
        sheet.update('A1:C5', data)
    
    def migrate_members(self) -> int:
        """성도 데이터 마이그레이션"""
        excel = pd.ExcelFile(self.excel_path)
        sheets_to_migrate = ['장년부', '청년부', '청소년부', '어린이부']
        dept_map = {
            '장년부': 'D01', '청년부': 'D02', 
            '청소년부': 'D03', '어린이부': 'D04'
        }
        
        all_members = []
        member_id = 1
        
        for sheet_name in sheets_to_migrate:
            if sheet_name not in excel.sheet_names:
                print(f"  ⚠️ '{sheet_name}' 시트 없음, 건너뜀")
                continue
            
            df = pd.read_excel(excel, sheet_name=sheet_name)
            
            for _, row in df.iterrows():
                name = str(row.get('이름', '')).strip()
                if not name or name == 'nan':
                    continue
                
                try:
                    member_data = {
                        'member_id': f'M{member_id:05d}',
                        'name': name,
                        'family_id': '',
                        'dept_id': dept_map[sheet_name],
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
                    self.errors.append(f"성도 '{name}' 처리 오류: {e}")
        
        # Google Sheets에 저장
        if all_members:
            try:
                sheet = self.spreadsheet.worksheet('Members')
                sheet.clear()
            except:
                sheet = self.spreadsheet.add_worksheet('Members', 1000, 20)
            
            headers = list(all_members[0].keys())
            rows = [headers] + [[m[h] for h in headers] for m in all_members]
            sheet.update(f'A1:T{len(rows)}', rows)
            
            # 시퀀스 업데이트
            seq_sheet = self.spreadsheet.worksheet('_Sequences')
            seq_sheet.update('B2', member_id - 1)
        
        return len(all_members)
    
    def migrate_attendance(self) -> int:
        """출석 데이터 마이그레이션"""
        excel = pd.ExcelFile(self.excel_path)
        
        if '출석부' not in excel.sheet_names:
            print("  ⚠️ '출석부' 시트 없음")
            return 0
        
        df = pd.read_excel(excel, sheet_name='출석부', header=7)
        
        # 성도 ID 매핑 (이름 → member_id)
        members_sheet = self.spreadsheet.worksheet('Members')
        members_data = members_sheet.get_all_records()
        name_to_id = {m['name']: m['member_id'] for m in members_data}
        
        attendance_records = []
        
        # 날짜 컬럼 찾기
        date_cols = [col for col in df.columns if isinstance(col, pd.Timestamp)]
        
        for _, row in df.iterrows():
            name = str(row.get('성명', '')).strip()
            if not name or name not in name_to_id:
                continue
            
            member_id = name_to_id[name]
            
            for date_col in date_cols:
                value = row[date_col]
                if pd.isna(value):
                    continue
                
                # 출석 유형 변환
                if value == 1:
                    attend_type = AttendType.PRESENT.value
                elif value == 0:
                    attend_type = AttendType.ABSENT.value
                else:
                    attend_type = AttendType.ONLINE.value
                
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
        
        # 연도별로 분리 저장
        if attendance_records:
            df_attend = pd.DataFrame(attendance_records)
            for year, group in df_attend.groupby('year'):
                sheet_name = f'Attendance_{year}'
                try:
                    sheet = self.spreadsheet.worksheet(sheet_name)
                    sheet.clear()
                except:
                    sheet = self.spreadsheet.add_worksheet(sheet_name, 10000, 10)
                
                records = group.to_dict('records')
                headers = list(records[0].keys())
                rows = [headers] + [[r[h] for h in headers] for r in records]
                sheet.update(f'A1:F{len(rows)}', rows)
        
        return len(attendance_records)
    
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
    
    def validate_all(self):
        """전체 데이터 검증"""
        # 성도 수 확인
        members_sheet = self.spreadsheet.worksheet('Members')
        member_count = len(members_sheet.get_all_records())
        print(f"  - Members: {member_count}명")
        
        # 중복 ID 확인
        members = members_sheet.get_all_records()
        ids = [m['member_id'] for m in members]
        duplicates = [id for id in ids if ids.count(id) > 1]
        if duplicates:
            print(f"  ⚠️ 중복 ID 발견: {set(duplicates)}")
        else:
            print("  ✓ 중복 ID 없음")


if __name__ == '__main__':
    migrator = DataMigrator(
        excel_path='../data/2025출석부_목자용_.xlsx',
        sheet_url='YOUR_GOOGLE_SHEET_URL'
    )
    migrator.migrate_all()
```

---

## 12. 구현 가이드 (Claude Code용)

### 12.1 구현 순서

```
┌─────────────────────────────────────────────────────────────────┐
│                      구현 순서                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: 기반 구축 (1주)                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. 프로젝트 구조 생성                                    │   │
│  │ 2. utils/enums.py - Enum 정의                           │   │
│  │ 3. utils/validators.py - Pydantic 모델                  │   │
│  │ 4. utils/auth.py - 인증 모듈                            │   │
│  │ 5. Google Sheets 생성 + Apps Script 배포                │   │
│  │ 6. utils/apps_script_client.py - ID 생성 클라이언트     │   │
│  │ 7. utils/sheets_api.py - 기본 CRUD                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Phase 2: 데이터 마이그레이션 (3일)                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. migration/migrate_data.py 실행                       │   │
│  │ 2. 데이터 검증                                          │   │
│  │ 3. _Sequences 값 조정                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Phase 3: 핵심 기능 (1주)                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. app.py - 대시보드 (인증 포함)                        │   │
│  │ 2. pages/1_출석입력.py - Upsert 패턴 적용               │   │
│  │ 3. pages/2_성도관리.py - CRUD + 검증                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Phase 4: 부가 기능 (1주)                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. pages/4_검색.py                                      │   │
│  │ 2. pages/5_통계.py                                      │   │
│  │ 3. 회원교인 자동 판정                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Phase 5: 배포 (2일)                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. Streamlit Cloud 배포                                 │   │
│  │ 2. Secrets 설정                                         │   │
│  │ 3. 테스트 및 피드백                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2 핵심 파일 구현

#### requirements.txt
```
streamlit>=1.28.0
pandas>=2.0.0
gspread>=5.10.0
oauth2client>=4.1.3
pydantic>=2.0.0
plotly>=5.15.0
openpyxl>=3.1.0
```

#### utils/apps_script_client.py
```python
"""Apps Script API 클라이언트 - ID 생성용"""

import requests
from typing import Optional

class AppsScriptClient:
    def __init__(self, script_url: str):
        """
        Args:
            script_url: Apps Script 웹앱 URL
        """
        self.script_url = script_url
    
    def generate_member_id(self) -> str:
        """새 성도 ID 생성"""
        return self._call_api('generateMemberId')
    
    def generate_family_id(self) -> str:
        """새 가정 ID 생성"""
        return self._call_api('generateFamilyId')
    
    def generate_event_id(self) -> str:
        """새 신앙이력 ID 생성"""
        return self._call_api('generateEventId')
    
    def _call_api(self, action: str) -> str:
        """Apps Script API 호출"""
        try:
            response = requests.get(
                self.script_url,
                params={'action': action},
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success'):
                return result['id']
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except requests.RequestException as e:
            raise Exception(f'Apps Script API 호출 실패: {e}')
```

#### utils/sheets_api.py (전체)
```python
"""Google Sheets API 래퍼"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from typing import List, Dict, Optional
import streamlit as st

from .validators import MemberCreate, MemberUpdate, AttendanceCreate
from .apps_script_client import AppsScriptClient


class SheetsAPI:
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Streamlit Secrets에서 인증 정보 로드
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            dict(creds_dict), self.scope
        )
        
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open(st.secrets["sheet_name"])
        
        # Apps Script 클라이언트
        self.apps_script = AppsScriptClient(st.secrets["apps_script_url"])
    
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
        member_ids: Optional[List[str]] = None
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
            sheet = self.spreadsheet.add_worksheet(sheet_name, 10000, 10)
            headers = ['attend_id', 'member_id', 'attend_date', 
                      'attend_type', 'year', 'week_no']
            sheet.append_row(headers)
        
        # 1. 기존 데이터 조회
        all_data = sheet.get_all_records()
        
        # 2. 삭제할 행 찾기
        rows_to_delete = []
        for i, row in enumerate(all_data):
            if (row.get('week_no') == week_no and 
                row.get('member_id') in member_ids):
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
```

---

## 13. 배포 가이드

### 13.1 Streamlit Cloud 배포

1. **GitHub 저장소 생성** 및 코드 푸시
2. **Streamlit Cloud** 접속 (https://share.streamlit.io)
3. **New app** 클릭
4. **GitHub 저장소** 연결
5. **Main file**: `app.py`
6. **Secrets** 설정

### 13.2 Secrets 설정

```toml
# Streamlit Cloud > App Settings > Secrets

app_password = "your_secure_password_here"
sheet_name = "성도기록부_시스템"
apps_script_url = "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

### 13.3 Apps Script 배포

1. Google Sheets에서 **확장 프로그램 > Apps Script**
2. `Code.gs` 코드 붙여넣기
3. **배포 > 새 배포**
4. **유형**: 웹 앱
5. **실행 권한**: 나 (본인 계정)
6. **액세스 권한**: 모든 사용자
7. **배포** → URL 복사 → Streamlit Secrets에 설정

---

## 14. 체크리스트

### 구축 전 준비
- [ ] Google Cloud 프로젝트 생성
- [ ] Google Sheets API 활성화
- [ ] Service Account 생성 및 키 다운로드
- [ ] 새 Google Sheets 생성 및 Service Account 공유
- [ ] Apps Script 배포 및 URL 확보

### 시스템 시트 생성
- [ ] _Sequences 시트 생성 (ID 시퀀스)
- [ ] _Departments 시트 생성 (4개 부서)
- [ ] _Groups 시트 생성 (목장 목록)
- [ ] _Codes 시트 생성 (코드 테이블)
- [ ] _Families 시트 생성

### 데이터 마이그레이션
- [ ] 기존 Excel 파일 백업
- [ ] Members 시트 생성 및 데이터 이관
- [ ] FaithEvents 시트 생성 및 데이터 이관
- [ ] Attendance_2025 시트 생성 및 데이터 이관
- [ ] _Sequences 값 업데이트
- [ ] 데이터 검증 (성도 수, 중복, FK 정합성)

### 앱 개발
- [ ] 프로젝트 구조 생성
- [ ] utils/enums.py 구현
- [ ] utils/validators.py 구현
- [ ] utils/auth.py 구현
- [ ] utils/apps_script_client.py 구현
- [ ] utils/sheets_api.py 구현
- [ ] app.py (대시보드 + 인증) 구현
- [ ] 출석 입력 페이지 구현 (Upsert 패턴)
- [ ] 성도 관리 페이지 구현
- [ ] 검색 페이지 구현
- [ ] 통계/보고서 페이지 구현

### 배포
- [ ] GitHub 저장소 생성
- [ ] Streamlit Cloud 배포
- [ ] Secrets 설정 (비밀번호, 인증정보, Apps Script URL)
- [ ] 테스트 및 검증

---

## 15. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2025-01-09 | 초기 설계서 작성 |
| 1.1 | 2025-01-09 | 리뷰 반영: ID 생성 락 처리, 출석 Upsert, 인증, 검증 레이어 추가 |

---

*Document Version: 1.1*  
*Last Updated: 2025-01-09*