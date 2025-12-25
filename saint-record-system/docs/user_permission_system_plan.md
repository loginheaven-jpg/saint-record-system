# 사용자 권한 시스템 구현 계획서

> **최종 결정사항** (2024-12 확정)
> - 권한 레벨: 원안 그대로 4단계
> - 인증 방식: 이메일 + 비밀번호
> - 생년월일: 주민번호 → 6자리로 변경
> - 목원 열람: 동일 목장 모든 정보 열람 가능
> - 데이터베이스: Google Sheets → **Supabase 전환**

---

## 1. 권한 레벨 정의

| 레벨 | 코드 | 권한 범위 |
|------|------|----------|
| **수퍼어드민** | `super_admin` | 전권 + 관리자 권한 부여/해제 |
| **관리자** | `admin` | 권한부여 외 모든 권한 (성도/출석/목장 관리) |
| **목자** | `shepherd` | 본인 목장 목원 정보 열람/수정, 출석 변경 |
| **목원** | `member` | 동일 목장 정보 열람, 본인 정보만 수정 |

### 1.1 페이지별 접근 권한

| 페이지 | super_admin | admin | shepherd | member |
|--------|:-----------:|:-----:|:--------:|:------:|
| 대시보드 | ✅ | ✅ | ✅ | ✅ |
| 출석입력 | ✅ 전체 | ✅ 전체 | ✅ 본인목장 | ❌ |
| 성도관리 | ✅ 전체 | ✅ 전체 | ✅ 본인목장 | ✅ 열람만 |
| 목장관리 | ✅ | ✅ | ❌ | ❌ |
| 통계분석 | ✅ | ✅ | ✅ 본인목장 | ❌ |
| 권한관리 | ✅ | ❌ | ❌ | ❌ |

---

## 2. 데이터베이스 스키마 (Supabase)

### 2.1 users 테이블 (신규)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    birth_date VARCHAR(6) NOT NULL,  -- YYMMDD 형식
    phone VARCHAR(20) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    member_id VARCHAR(50) REFERENCES members(member_id),  -- 성도 테이블 연결
    group_id VARCHAR(50) REFERENCES groups(group_id),     -- 소속 목장
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,

    CONSTRAINT valid_role CHECK (role IN ('super_admin', 'admin', 'shepherd', 'member'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_member_id ON users(member_id);
CREATE INDEX idx_users_group_id ON users(group_id);
```

### 2.2 user_registration_requests 테이블 (신규)

```sql
CREATE TABLE user_registration_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    birth_date VARCHAR(6) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    matched_member_id VARCHAR(50),  -- 자동매칭된 성도 ID
    requested_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP,
    reviewed_by UUID REFERENCES users(id),
    assigned_role VARCHAR(20),
    rejection_reason TEXT,

    CONSTRAINT valid_status CHECK (status IN ('pending', 'approved', 'rejected'))
);

CREATE INDEX idx_requests_status ON user_registration_requests(status);
```

### 2.3 기존 테이블 마이그레이션

| Google Sheets | Supabase 테이블명 | 주요 변경 |
|---------------|------------------|----------|
| members | members | member_id를 PK로 유지 |
| departments | departments | - |
| groups | groups | - |
| attendance | attendance | - |

```sql
-- members 테이블 (기존 구조 유지 + 컬럼 추가)
CREATE TABLE members (
    member_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    birth_date DATE,
    gender VARCHAR(10),
    phone VARCHAR(20),
    address TEXT,
    department_id VARCHAR(50),
    group_id VARCHAR(50),
    family_id VARCHAR(50),
    relationship VARCHAR(50),
    church_role VARCHAR(50),
    group_role VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- departments 테이블
CREATE TABLE departments (
    department_id VARCHAR(50) PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL
);

-- groups 테이블
CREATE TABLE groups (
    group_id VARCHAR(50) PRIMARY KEY,
    group_name VARCHAR(100) NOT NULL,
    department_id VARCHAR(50) REFERENCES departments(department_id),
    leader_member_id VARCHAR(50) REFERENCES members(member_id)
);

-- attendance 테이블
CREATE TABLE attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id VARCHAR(50) REFERENCES members(member_id),
    attend_date DATE NOT NULL,
    attend_type INTEGER NOT NULL,  -- 0: 결석, 1: 출석, 2: 온라인
    year INTEGER NOT NULL,
    week_no INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    UNIQUE(member_id, year, week_no)
);

CREATE INDEX idx_attendance_date ON attendance(year, week_no);
CREATE INDEX idx_attendance_member ON attendance(member_id);
```

---

## 3. Row Level Security (RLS) 정책

### 3.1 members 테이블 RLS

```sql
-- RLS 활성화
ALTER TABLE members ENABLE ROW LEVEL SECURITY;

-- 수퍼어드민/관리자: 전체 접근
CREATE POLICY "admin_full_access" ON members
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role IN ('super_admin', 'admin')
    )
);

-- 목자: 본인 목장만
CREATE POLICY "shepherd_group_access" ON members
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role = 'shepherd'
        AND users.group_id = members.group_id
    )
);

-- 목원: 동일 목장 열람 + 본인만 수정
CREATE POLICY "member_read_group" ON members
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role = 'member'
        AND users.group_id = members.group_id
    )
);

CREATE POLICY "member_update_self" ON members
FOR UPDATE
USING (
    EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role = 'member'
        AND users.member_id = members.member_id
    )
);
```

### 3.2 attendance 테이블 RLS

```sql
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;

-- 수퍼어드민/관리자: 전체 접근
CREATE POLICY "admin_full_access" ON attendance
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role IN ('super_admin', 'admin')
    )
);

-- 목자: 본인 목장만
CREATE POLICY "shepherd_group_access" ON attendance
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM users u
        JOIN members m ON m.member_id = attendance.member_id
        WHERE u.id = auth.uid()
        AND u.role = 'shepherd'
        AND u.group_id = m.group_id
    )
);

-- 목원: 열람 불가
-- (정책 없음 = 접근 거부)
```

---

## 4. 인증 시스템 설계

### 4.1 Supabase Auth 활용

```python
# utils/supabase_client.py

from supabase import create_client
import streamlit as st

@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)
```

### 4.2 AuthManager 클래스

```python
# utils/auth.py

from dataclasses import dataclass
from typing import Optional
from enum import Enum

class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SHEPHERD = "shepherd"
    MEMBER = "member"

@dataclass
class CurrentUser:
    id: str
    email: str
    name: str
    role: UserRole
    member_id: Optional[str]
    group_id: Optional[str]

    def is_admin_or_above(self) -> bool:
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]

    def can_access_group(self, group_id: str) -> bool:
        if self.is_admin_or_above():
            return True
        return self.group_id == group_id

    def can_edit_member(self, member_id: str) -> bool:
        if self.is_admin_or_above():
            return True
        if self.role == UserRole.SHEPHERD:
            # 목자는 본인 목장 전체 수정 가능 (별도 체크 필요)
            return True
        # 목원은 본인만
        return self.member_id == member_id

class AuthManager:
    def __init__(self, supabase_client):
        self.client = supabase_client

    def login(self, email: str, password: str) -> tuple[bool, str]:
        """로그인 시도. (성공여부, 메시지) 반환"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return True, "로그인 성공"
        except Exception as e:
            return False, str(e)

    def logout(self):
        """로그아웃"""
        self.client.auth.sign_out()
        if 'current_user' in st.session_state:
            del st.session_state['current_user']

    def get_current_user(self) -> Optional[CurrentUser]:
        """현재 로그인된 사용자 정보"""
        session = self.client.auth.get_session()
        if not session:
            return None

        user_id = session.user.id
        user_data = self.client.table('users').select('*').eq('id', user_id).single().execute()

        if not user_data.data:
            return None

        return CurrentUser(
            id=user_data.data['id'],
            email=user_data.data['email'],
            name=user_data.data['name'],
            role=UserRole(user_data.data['role']),
            member_id=user_data.data.get('member_id'),
            group_id=user_data.data.get('group_id')
        )

    def register(self, email: str, password: str, name: str,
                 birth_date: str, phone: str) -> tuple[bool, str]:
        """회원가입 요청"""
        # 1. 이메일 중복 체크
        existing = self.client.table('users').select('id').eq('email', email).execute()
        if existing.data:
            return False, "이미 등록된 이메일입니다."

        pending = self.client.table('user_registration_requests').select('id').eq('email', email).eq('status', 'pending').execute()
        if pending.data:
            return False, "이미 승인 대기 중인 요청이 있습니다."

        # 2. 성도 자동 매칭 시도
        matched_member = self._find_matching_member(name, phone)

        # 3. 비밀번호 해시
        import bcrypt
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # 4. 자동 승인 또는 대기 등록
        if matched_member:
            # 기존 성도 매칭 → 자동 승인
            self._create_user_direct(email, password_hash, name, birth_date, phone, matched_member)
            return True, "기존 성도 정보와 매칭되어 자동 승인되었습니다. 로그인해주세요."
        else:
            # 미매칭 → 대기 상태
            self._create_registration_request(email, password_hash, name, birth_date, phone)
            return True, "가입 요청이 접수되었습니다. 관리자 승인 후 이용 가능합니다."

    def _find_matching_member(self, name: str, phone: str):
        """이름 + 전화번호로 기존 성도 매칭"""
        # 전화번호 정규화 (하이픈 제거)
        normalized_phone = phone.replace('-', '').replace(' ', '')

        result = self.client.table('members').select('*').eq('name', name).execute()

        for member in result.data:
            member_phone = (member.get('phone') or '').replace('-', '').replace(' ', '')
            if member_phone == normalized_phone:
                return member

        return None

    def _create_user_direct(self, email, password_hash, name, birth_date, phone, matched_member):
        """매칭된 성도로 직접 사용자 생성"""
        # 목장 역할 확인하여 권한 결정
        role = 'member'
        if matched_member.get('group_role') == '목자':
            role = 'shepherd'

        self.client.table('users').insert({
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'birth_date': birth_date,
            'phone': phone,
            'role': role,
            'member_id': matched_member['member_id'],
            'group_id': matched_member.get('group_id'),
            'is_active': True
        }).execute()

    def _create_registration_request(self, email, password_hash, name, birth_date, phone):
        """승인 대기 요청 생성"""
        self.client.table('user_registration_requests').insert({
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'birth_date': birth_date,
            'phone': phone,
            'status': 'pending'
        }).execute()
```

---

## 5. 권한 데코레이터

```python
# utils/permissions.py

import streamlit as st
from functools import wraps
from utils.auth import UserRole, AuthManager
from utils.supabase_client import get_supabase_client

def require_login(func):
    """로그인 필수 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'current_user' not in st.session_state or not st.session_state.current_user:
            st.warning("로그인이 필요합니다.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def require_role(*allowed_roles: UserRole):
    """특정 역할 필수 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = st.session_state.get('current_user')
            if not user:
                st.warning("로그인이 필요합니다.")
                st.stop()

            if user.role not in allowed_roles:
                st.error("접근 권한이 없습니다.")
                st.stop()

            return func(*args, **kwargs)
        return wrapper
    return decorator

def filter_by_permission(data, group_id_column='group_id'):
    """현재 사용자 권한에 따라 데이터 필터링"""
    user = st.session_state.get('current_user')
    if not user:
        return data.iloc[0:0]  # 빈 DataFrame

    if user.is_admin_or_above():
        return data  # 전체 반환

    # 목자/목원: 본인 목장만
    if group_id_column in data.columns:
        return data[data[group_id_column] == user.group_id]

    return data
```

---

## 6. 페이지 인증 래퍼

```python
# utils/page_auth.py

import streamlit as st
from utils.auth import AuthManager, UserRole
from utils.supabase_client import get_supabase_client

def init_page_auth():
    """페이지 시작 시 인증 상태 확인"""
    if 'current_user' not in st.session_state:
        client = get_supabase_client()
        auth = AuthManager(client)
        user = auth.get_current_user()

        if user:
            st.session_state.current_user = user
        else:
            show_login_page()
            st.stop()

def show_login_page():
    """로그인/회원가입 UI"""
    st.title("교회 관리 시스템")

    tab1, tab2 = st.tabs(["로그인", "회원가입"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("이메일")
            password = st.text_input("비밀번호", type="password")
            submitted = st.form_submit_button("로그인", use_container_width=True)

            if submitted:
                client = get_supabase_client()
                auth = AuthManager(client)
                success, message = auth.login(email, password)

                if success:
                    st.session_state.current_user = auth.get_current_user()
                    st.rerun()
                else:
                    st.error(message)

    with tab2:
        with st.form("register_form"):
            email = st.text_input("이메일")
            password = st.text_input("비밀번호", type="password")
            password_confirm = st.text_input("비밀번호 확인", type="password")
            name = st.text_input("이름")
            birth_date = st.text_input("생년월일 (6자리)", placeholder="예: 850315")
            phone = st.text_input("전화번호", placeholder="예: 010-1234-5678")

            submitted = st.form_submit_button("가입 요청", use_container_width=True)

            if submitted:
                if password != password_confirm:
                    st.error("비밀번호가 일치하지 않습니다.")
                elif len(birth_date) != 6:
                    st.error("생년월일은 6자리로 입력해주세요.")
                else:
                    client = get_supabase_client()
                    auth = AuthManager(client)
                    success, message = auth.register(email, password, name, birth_date, phone)

                    if success:
                        st.success(message)
                    else:
                        st.error(message)

def require_page_role(*allowed_roles: UserRole):
    """페이지 레벨 권한 체크"""
    user = st.session_state.get('current_user')

    if not user:
        st.warning("로그인이 필요합니다.")
        st.stop()

    if user.role not in allowed_roles:
        st.error("이 페이지에 접근할 권한이 없습니다.")
        st.stop()
```

---

## 7. 가입 승인 워크플로우

### 7.1 승인 대기 관리 페이지

```python
# pages/7_🔐_권한관리.py (신규)

import streamlit as st
from utils.page_auth import init_page_auth, require_page_role
from utils.auth import UserRole, AuthManager
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="권한 관리", page_icon="🔐", layout="wide")
init_page_auth()
require_page_role(UserRole.SUPER_ADMIN)

st.title("권한 관리")

client = get_supabase_client()
auth = AuthManager(client)

# 탭 구성
tab1, tab2 = st.tabs(["가입 승인 대기", "사용자 관리"])

with tab1:
    st.subheader("승인 대기 목록")

    pending = client.table('user_registration_requests') \
        .select('*') \
        .eq('status', 'pending') \
        .order('requested_at', desc=True) \
        .execute()

    if pending.data:
        for req in pending.data:
            with st.expander(f"📋 {req['name']} ({req['email']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**이름:** {req['name']}")
                    st.write(f"**이메일:** {req['email']}")
                    st.write(f"**생년월일:** {req['birth_date']}")
                with col2:
                    st.write(f"**전화번호:** {req['phone']}")
                    st.write(f"**요청일시:** {req['requested_at']}")

                # 승인 처리
                col_role, col_approve, col_reject = st.columns([2, 1, 1])
                with col_role:
                    assigned_role = st.selectbox(
                        "권한 레벨",
                        options=['member', 'shepherd', 'admin'],
                        format_func=lambda x: {'member': '목원', 'shepherd': '목자', 'admin': '관리자'}[x],
                        key=f"role_{req['id']}"
                    )
                with col_approve:
                    if st.button("승인", key=f"approve_{req['id']}", type="primary"):
                        # 사용자 생성 + 요청 상태 변경
                        st.success("승인 완료")
                        st.rerun()
                with col_reject:
                    if st.button("거절", key=f"reject_{req['id']}"):
                        # 요청 상태 변경
                        st.warning("거절 처리됨")
                        st.rerun()
    else:
        st.info("승인 대기 중인 요청이 없습니다.")

with tab2:
    st.subheader("사용자 목록")

    users = client.table('users') \
        .select('*, members(name)') \
        .order('created_at', desc=True) \
        .execute()

    if users.data:
        for user in users.data:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                role_badge = {
                    'super_admin': '🔴 수퍼어드민',
                    'admin': '🟠 관리자',
                    'shepherd': '🟢 목자',
                    'member': '🔵 목원'
                }
                st.write(f"{role_badge.get(user['role'], '?')} **{user['name']}** ({user['email']})")
            with col2:
                # 권한 변경 (super_admin만)
                if user['role'] != 'super_admin':
                    new_role = st.selectbox(
                        "권한",
                        options=['member', 'shepherd', 'admin'],
                        index=['member', 'shepherd', 'admin'].index(user['role']) if user['role'] in ['member', 'shepherd', 'admin'] else 0,
                        key=f"change_{user['id']}",
                        label_visibility="collapsed"
                    )
            with col3:
                if st.button("저장", key=f"save_{user['id']}"):
                    st.success("변경 완료")
```

---

## 8. 마이그레이션 계획

### 8.1 Google Sheets → Supabase 데이터 이전

```python
# migration/migrate_to_supabase.py

import pandas as pd
from utils.sheets_api import SheetsAPI
from supabase import create_client

def migrate_all_data():
    """전체 데이터 마이그레이션"""
    sheets = SheetsAPI()
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # 1. departments 이전
    print("Migrating departments...")
    departments = sheets.get_departments()
    for _, row in departments.iterrows():
        supabase.table('departments').upsert({
            'department_id': row['department_id'],
            'department_name': row['department_name']
        }).execute()

    # 2. groups 이전
    print("Migrating groups...")
    groups = sheets.get_groups()
    for _, row in groups.iterrows():
        supabase.table('groups').upsert({
            'group_id': row['group_id'],
            'group_name': row['group_name'],
            'department_id': row.get('department_id'),
            'leader_member_id': row.get('leader_member_id')
        }).execute()

    # 3. members 이전
    print("Migrating members...")
    members = sheets.get_members({})
    for _, row in members.iterrows():
        supabase.table('members').upsert({
            'member_id': row['member_id'],
            'name': row['name'],
            'birth_date': row.get('birth_date'),
            'gender': row.get('gender'),
            'phone': row.get('phone'),
            'address': row.get('address'),
            'department_id': row.get('department_id'),
            'group_id': row.get('group_id'),
            'family_id': row.get('family_id'),
            'relationship': row.get('relationship'),
            'church_role': row.get('church_role'),
            'group_role': row.get('group_role'),
            'status': row.get('status', 'active')
        }).execute()

    # 4. attendance 이전
    print("Migrating attendance...")
    for year in [2024, 2025]:
        for week in range(1, 53):
            attendance = sheets.get_attendance(year, week_no=week)
            for _, row in attendance.iterrows():
                supabase.table('attendance').upsert({
                    'member_id': row['member_id'],
                    'attend_date': row['attend_date'],
                    'attend_type': int(row['attend_type']),
                    'year': year,
                    'week_no': week
                }).execute()

    print("Migration complete!")

if __name__ == "__main__":
    migrate_all_data()
```

### 8.2 초기 수퍼어드민 생성

```sql
-- 최초 수퍼어드민 계정 수동 생성
INSERT INTO users (email, password_hash, name, birth_date, phone, role, is_active)
VALUES (
    'admin@church.org',
    '$2b$12$...hashed_password...',  -- bcrypt 해시
    '관리자',
    '000101',
    '010-0000-0000',
    'super_admin',
    TRUE
);
```

---

## 9. 파일 수정 목록

### 9.1 신규 생성 파일

| 파일 경로 | 용도 |
|----------|------|
| `utils/supabase_client.py` | Supabase 클라이언트 초기화 |
| `utils/auth.py` | AuthManager, CurrentUser, UserRole |
| `utils/permissions.py` | 권한 데코레이터 |
| `utils/page_auth.py` | 페이지 인증 래퍼 |
| `utils/supabase_api.py` | SupabaseAPI (SheetsAPI 대체) |
| `components/login.py` | 로그인/회원가입 UI 컴포넌트 |
| `pages/7_🔐_권한관리.py` | 가입 승인, 권한 변경 |
| `migration/migrate_to_supabase.py` | 데이터 마이그레이션 스크립트 |

### 9.2 수정 필요 파일

| 파일 경로 | 수정 내용 |
|----------|----------|
| `app.py` | 인증 체크 추가, SupabaseAPI 사용 |
| `pages/1_📋_출석입력.py` | 권한 체크, 목장 필터링 |
| `pages/2_👤_성도관리.py` | 권한 체크, 수정 제한 |
| `pages/4_📊_통계분석.py` | 권한별 데이터 필터링 |
| `utils/sidebar.py` | 권한별 메뉴 표시 |
| `utils/enums.py` | UserRole 추가 |
| `utils/validators.py` | User, RegistrationRequest 모델 추가 |
| `.streamlit/secrets.toml` | Supabase 연결 정보 추가 |

---

## 10. 구현 단계 (Phase)

### Phase 1: 인프라 구축
- [ ] Supabase 프로젝트 생성
- [ ] 테이블 스키마 생성 (SQL 실행)
- [ ] RLS 정책 설정
- [ ] `.streamlit/secrets.toml` 설정
- [ ] `utils/supabase_client.py` 작성

### Phase 2: 인증 시스템
- [ ] `utils/auth.py` 작성
- [ ] `utils/page_auth.py` 작성
- [ ] `components/login.py` 작성
- [ ] 로그인/회원가입 UI 테스트

### Phase 3: 데이터 API 전환
- [ ] `utils/supabase_api.py` 작성 (SheetsAPI 인터페이스 유지)
- [ ] 기존 SheetsAPI 호출부 → SupabaseAPI로 교체
- [ ] 단위 테스트

### Phase 4: 데이터 마이그레이션
- [ ] 마이그레이션 스크립트 작성
- [ ] 테스트 환경에서 마이그레이션 실행
- [ ] 데이터 정합성 검증
- [ ] 프로덕션 마이그레이션

### Phase 5: 권한 적용
- [ ] `utils/permissions.py` 작성
- [ ] 각 페이지에 권한 체크 추가
- [ ] 사이드바 메뉴 권한 필터링
- [ ] 통합 테스트

### Phase 6: 관리 기능
- [ ] `pages/7_🔐_권한관리.py` 작성
- [ ] 가입 승인 워크플로우 테스트
- [ ] 권한 변경 기능 테스트

### Phase 7: 마무리
- [ ] 초기 수퍼어드민 계정 생성
- [ ] 전체 시나리오 테스트
- [ ] 문서화
- [ ] 배포

---

## 11. 위험 요소 및 대응

| 위험 | 영향 | 대응 방안 |
|------|------|----------|
| Supabase 무료 한도 초과 | 서비스 중단 | 사용량 모니터링, 필요시 유료 전환 |
| 마이그레이션 데이터 손실 | 데이터 무결성 | 백업 후 진행, 롤백 계획 수립 |
| 성도 매칭 오류 | 잘못된 권한 부여 | 관리자 수동 검토 프로세스 유지 |
| 비밀번호 분실 | 사용자 불편 | 비밀번호 재설정 기능 추가 (Phase 7) |
| 동시 접속 제한 | 성능 저하 | Connection pooling 적용 |

---

## 12. 테스트 시나리오

### 12.1 인증 테스트
- [ ] 신규 가입 → 기존 성도 매칭 → 자동 승인
- [ ] 신규 가입 → 미매칭 → 대기 상태
- [ ] 수퍼어드민 승인 → 사용자 활성화
- [ ] 로그인/로그아웃
- [ ] 세션 만료 후 재로그인

### 12.2 권한 테스트
| 시나리오 | super_admin | admin | shepherd | member |
|----------|:-----------:|:-----:|:--------:|:------:|
| 대시보드 접근 | ✅ | ✅ | ✅ | ✅ |
| 전체 성도 조회 | ✅ | ✅ | ❌ | ❌ |
| 본인 목장 성도 조회 | ✅ | ✅ | ✅ | ✅ |
| 타 목장 성도 수정 | ✅ | ✅ | ❌ | ❌ |
| 본인 목장 출석 입력 | ✅ | ✅ | ✅ | ❌ |
| 권한 관리 페이지 | ✅ | ❌ | ❌ | ❌ |

---

## 부록: 이전 계획 (완료)

### A. 출석입력 페이지 개선 ✅ (v3.34)
- 목장선택 → 날짜카드 → 통계바 → 출석리스트 순서로 변경
- 주차 네비게이션 추가 (◀ ▶)
- 아바타 제거
- 헤더 메시지 변경

### B. 성도관리 + 가정관리 통합 ✅ (v3.35)
- 가정 구성원 테이블 통합
- 나이 계산, 관계 배지 추가
- 보기/수정 모드 분리
- 가정관리 페이지 숨김 처리
