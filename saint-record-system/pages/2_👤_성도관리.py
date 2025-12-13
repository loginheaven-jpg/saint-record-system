import streamlit as st
import pandas as pd
from datetime import date
from utils.ui import load_custom_css
from utils.sheets_api import SheetsAPI
from utils.enums import MemberStatus, MemberType, ChurchRole, GroupRole
from utils.validators import MemberCreate, MemberUpdate

st.set_page_config(page_title="성도 관리", page_icon="👤", layout="wide")
load_custom_css()

# 추가 CSS
st.markdown("""
<style>
/* 페이지 헤더 */
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 32px;
    padding: 0 4px;
}
.page-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    font-weight: 600;
    color: #2C3E50;
    margin: 0 0 8px 0;
}
.page-header p {
    font-size: 14px;
    color: #6B7B8C;
    margin: 0;
}

/* 필터 카드 */
.filter-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
    margin-bottom: 24px;
}

/* 성도 카드 */
.member-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.3s ease;
    cursor: pointer;
}
.member-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(44, 62, 80, 0.1);
}

.member-avatar {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    background: linear-gradient(135deg, #C9A962 0%, #D4B87A 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 600;
    color: white;
    flex-shrink: 0;
}

.member-info {
    flex: 1;
}
.member-name {
    font-size: 16px;
    font-weight: 600;
    color: #2C3E50;
    margin-bottom: 4px;
}
.member-meta {
    font-size: 13px;
    color: #6B7B8C;
}

.member-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.badge-active {
    background: rgba(74, 155, 127, 0.12);
    color: #4A9B7F;
}
.badge-inactive {
    background: rgba(232, 152, 94, 0.12);
    color: #E8985E;
}

/* 폼 스타일 */
.form-card {
    background: white;
    border-radius: 24px;
    padding: 32px;
    box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
}
.form-title {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 600;
    color: #2C3E50;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.form-section {
    margin-bottom: 24px;
}
.form-section-title {
    font-size: 14px;
    font-weight: 600;
    color: #8B7355;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* 버튼 스타일 */
.btn-primary {
    background: linear-gradient(135deg, #C9A962 0%, #D4B87A 100%);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}
.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(201, 169, 98, 0.3);
}

.btn-secondary {
    background: #F8F6F3;
    color: #2C3E50;
    border: none;
    padding: 12px 24px;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}
.btn-secondary:hover {
    background: #F5EFE0;
}

/* 통계 카드 */
.mini-stat {
    background: #F8F6F3;
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
}
.mini-stat-value {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 700;
    color: #2C3E50;
}
.mini-stat-label {
    font-size: 12px;
    color: #6B7B8C;
    margin-top: 4px;
}

/* 탭 스타일 개선 */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #F8F6F3;
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: white;
    box-shadow: 0 2px 8px rgba(44, 62, 80, 0.08);
}
</style>
""", unsafe_allow_html=True)

# API 초기화
@st.cache_resource
def get_api():
    return SheetsAPI()

try:
    api = get_api()
    db_connected = True
except Exception as e:
    db_connected = False
    st.error(f"데이터베이스 연결 실패: {e}")

# 부서/목장 데이터 로드
@st.cache_data(ttl=300)
def load_departments():
    if db_connected:
        return api.get_departments()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_groups():
    if db_connected:
        return api.get_groups()
    return pd.DataFrame()

# 성도 목록 로드
def load_members(filters=None):
    if db_connected:
        return api.get_members(filters)
    return pd.DataFrame()

# 헤더
st.markdown("""
<div class="page-header">
    <div>
        <h1>성도 관리</h1>
        <p>성도 정보를 조회하고 관리합니다</p>
    </div>
</div>
""", unsafe_allow_html=True)

if db_connected:
    # 로딩 표시
    with st.spinner("📊 데이터를 불러오는 중..."):
        departments = load_departments()
        groups = load_groups()

    # 세션 상태 초기화
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'list'
    if 'selected_member' not in st.session_state:
        st.session_state.selected_member = None
    if 'show_form' not in st.session_state:
        st.session_state.show_form = False

    # 탭
    tab1, tab2 = st.tabs(["📋 성도 목록", "➕ 성도 등록"])

    with tab1:
        # 필터 영역
        col1, col2, col3, col4 = st.columns([2, 2, 2, 3])

        with col1:
            status_options = ['전체'] + [s.value for s in MemberStatus]
            selected_status = st.selectbox("상태", status_options, key="filter_status")

        with col2:
            dept_options = ['전체']
            if not departments.empty:
                dept_options += departments['dept_name'].tolist()
            selected_dept = st.selectbox("부서", dept_options, key="filter_dept")

        with col3:
            group_options = ['전체']
            if not groups.empty:
                if selected_dept != '전체':
                    dept_row = departments[departments['dept_name'] == selected_dept]
                    if not dept_row.empty:
                        dept_id = dept_row.iloc[0]['dept_id']
                        filtered_groups = groups[groups['dept_id'] == dept_id]
                        group_options += filtered_groups['group_name'].tolist()
                else:
                    group_options += groups['group_name'].tolist()
            selected_group = st.selectbox("목장", group_options, key="filter_group")

        with col4:
            search_term = st.text_input("🔍 이름 검색", placeholder="성도 이름을 입력하세요", key="search_name")

        # 필터 적용
        filters = {}
        if selected_status != '전체':
            filters['status'] = selected_status
        if selected_dept != '전체' and not departments.empty:
            dept_row = departments[departments['dept_name'] == selected_dept]
            if not dept_row.empty:
                filters['dept_id'] = dept_row.iloc[0]['dept_id']
        if selected_group != '전체' and not groups.empty:
            group_row = groups[groups['group_name'] == selected_group]
            if not group_row.empty:
                filters['group_id'] = group_row.iloc[0]['group_id']
        if search_term:
            filters['search'] = search_term

        # 성도 목록 로드
        members = load_members(filters if filters else None)

        # 통계 표시
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        stat_cols = st.columns(4)

        total_count = len(members) if not members.empty else 0
        active_count = len(members[members['status'] == '재적']) if not members.empty and 'status' in members.columns else 0

        with stat_cols[0]:
            st.markdown(f"""
            <div class="mini-stat">
                <div class="mini-stat-value">{total_count}</div>
                <div class="mini-stat-label">검색 결과</div>
            </div>
            """, unsafe_allow_html=True)

        with stat_cols[1]:
            st.markdown(f"""
            <div class="mini-stat">
                <div class="mini-stat-value">{active_count}</div>
                <div class="mini-stat-label">재적 성도</div>
            </div>
            """, unsafe_allow_html=True)

        with stat_cols[2]:
            st.markdown(f"""
            <div class="mini-stat">
                <div class="mini-stat-value">{len(departments) if not departments.empty else 0}</div>
                <div class="mini-stat-label">부서</div>
            </div>
            """, unsafe_allow_html=True)

        with stat_cols[3]:
            st.markdown(f"""
            <div class="mini-stat">
                <div class="mini-stat-value">{len(groups) if not groups.empty else 0}</div>
                <div class="mini-stat-label">목장</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # 성도 목록 표시
        if not members.empty:
            for idx, member in members.iterrows():
                # 부서/목장 이름 가져오기
                dept_name = ""
                group_name = ""
                if not departments.empty and 'dept_id' in member:
                    dept_match = departments[departments['dept_id'] == member.get('dept_id', '')]
                    if not dept_match.empty:
                        dept_name = dept_match.iloc[0]['dept_name']
                if not groups.empty and 'group_id' in member:
                    group_match = groups[groups['group_id'] == member.get('group_id', '')]
                    if not group_match.empty:
                        group_name = group_match.iloc[0]['group_name']

                # 상태에 따른 배지 스타일
                status = member.get('status', '재적')
                badge_class = 'badge-active' if status == '재적' else 'badge-inactive'

                # 이름 첫 글자
                name = member.get('name', '?')
                initial = name[0] if name else '?'

                # 성별 아이콘
                gender = member.get('gender', '')
                gender_icon = '👨' if gender == '남' else '👩' if gender == '여' else ''

                col1, col2 = st.columns([6, 1])

                with col1:
                    st.markdown(f"""
                    <div class="member-card">
                        <div class="member-avatar">{initial}</div>
                        <div class="member-info">
                            <div class="member-name">{gender_icon} {name}</div>
                            <div class="member-meta">
                                {dept_name} · {group_name} · {member.get('church_role', '')}
                            </div>
                        </div>
                        <div class="member-badge {badge_class}">{status}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if st.button("상세", key=f"detail_{member.get('member_id', idx)}"):
                        st.session_state.selected_member = member.to_dict()
                        st.session_state.show_form = True
                        st.rerun()
        else:
            st.info("조건에 맞는 성도가 없습니다.")

        # 성도 상세 정보 모달
        if st.session_state.show_form and st.session_state.selected_member:
            st.markdown("---")
            member = st.session_state.selected_member

            st.markdown(f"""
            <div class="form-card">
                <div class="form-title">
                    <span style="font-size: 28px;">👤</span>
                    {member.get('name', '')} 상세 정보
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("edit_member_form"):
                st.markdown('<div class="form-section-title">기본 정보</div>', unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)

                with col1:
                    edit_name = st.text_input("이름", value=member.get('name', ''))
                with col2:
                    gender_options = ['남', '여']
                    current_gender = member.get('gender', '남')
                    edit_gender = st.selectbox("성별", gender_options,
                        index=gender_options.index(current_gender) if current_gender in gender_options else 0)
                with col3:
                    edit_phone = st.text_input("연락처", value=member.get('phone', ''))

                col1, col2 = st.columns(2)
                with col1:
                    edit_birth = st.date_input("생년월일",
                        value=pd.to_datetime(member.get('birth_date')) if member.get('birth_date') else None)
                with col2:
                    edit_address = st.text_input("주소", value=member.get('address', ''))

                st.markdown('<div class="form-section-title">교회 정보</div>', unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)

                with col1:
                    dept_names = departments['dept_name'].tolist() if not departments.empty else []
                    current_dept = ""
                    if not departments.empty and member.get('dept_id'):
                        dept_match = departments[departments['dept_id'] == member.get('dept_id')]
                        if not dept_match.empty:
                            current_dept = dept_match.iloc[0]['dept_name']
                    edit_dept = st.selectbox("부서", dept_names,
                        index=dept_names.index(current_dept) if current_dept in dept_names else 0)

                with col2:
                    group_names = groups['group_name'].tolist() if not groups.empty else []
                    current_group = ""
                    if not groups.empty and member.get('group_id'):
                        group_match = groups[groups['group_id'] == member.get('group_id')]
                        if not group_match.empty:
                            current_group = group_match.iloc[0]['group_name']
                    edit_group = st.selectbox("목장", group_names,
                        index=group_names.index(current_group) if current_group in group_names else 0)

                with col3:
                    role_options = [r.value for r in ChurchRole]
                    current_role = member.get('church_role', '성도')
                    edit_role = st.selectbox("직분", role_options,
                        index=role_options.index(current_role) if current_role in role_options else 0)

                col1, col2, col3 = st.columns(3)
                with col1:
                    group_role_options = [r.value for r in GroupRole]
                    current_group_role = member.get('group_role', '목원')
                    edit_group_role = st.selectbox("목장 직분", group_role_options,
                        index=group_role_options.index(current_group_role) if current_group_role in group_role_options else 0)

                with col2:
                    status_opts = [s.value for s in MemberStatus]
                    current_status = member.get('status', '재적')
                    edit_status = st.selectbox("상태", status_opts,
                        index=status_opts.index(current_status) if current_status in status_opts else 0)

                with col3:
                    type_opts = [t.value for t in MemberType]
                    current_type = member.get('member_type', '등록교인')
                    edit_type = st.selectbox("교인 구분", type_opts,
                        index=type_opts.index(current_type) if current_type in type_opts else 0)

                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    submitted = st.form_submit_button("💾 저장", use_container_width=True)
                with col2:
                    if st.form_submit_button("닫기", use_container_width=True):
                        st.session_state.show_form = False
                        st.session_state.selected_member = None
                        st.rerun()

                if submitted:
                    # dept_id, group_id 찾기
                    new_dept_id = ""
                    new_group_id = ""
                    if not departments.empty:
                        dept_match = departments[departments['dept_name'] == edit_dept]
                        if not dept_match.empty:
                            new_dept_id = dept_match.iloc[0]['dept_id']
                    if not groups.empty:
                        group_match = groups[groups['group_name'] == edit_group]
                        if not group_match.empty:
                            new_group_id = group_match.iloc[0]['group_id']

                    update_data = MemberUpdate(
                        name=edit_name,
                        gender=edit_gender,
                        phone=edit_phone,
                        birth_date=edit_birth if edit_birth else None,
                        address=edit_address,
                        dept_id=new_dept_id,
                        group_id=new_group_id,
                        church_role=edit_role,
                        group_role=edit_group_role,
                        status=edit_status,
                        member_type=edit_type
                    )

                    result = api.update_member(member.get('member_id'), update_data)
                    if result.get('success'):
                        st.success("저장되었습니다!")
                        st.session_state.show_form = False
                        st.session_state.selected_member = None
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"저장 실패: {result.get('error')}")

    with tab2:
        # 성도 등록 폼
        st.markdown("""
        <div class="form-card">
            <div class="form-title">
                <span style="font-size: 28px;">➕</span>
                새 성도 등록
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("new_member_form"):
            st.markdown('<div class="form-section-title">기본 정보</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)

            with col1:
                new_name = st.text_input("이름 *", placeholder="홍길동")
            with col2:
                new_gender = st.selectbox("성별 *", ['남', '여'])
            with col3:
                new_phone = st.text_input("연락처 *", placeholder="010-1234-5678")

            col1, col2 = st.columns(2)
            with col1:
                new_birth = st.date_input("생년월일", value=None)
            with col2:
                new_address = st.text_input("주소", placeholder="서울시 ...")

            st.markdown('<div class="form-section-title">교회 정보</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)

            with col1:
                dept_names = departments['dept_name'].tolist() if not departments.empty else []
                new_dept = st.selectbox("부서 *", dept_names) if dept_names else st.text_input("부서 *")

            with col2:
                group_names = groups['group_name'].tolist() if not groups.empty else []
                new_group = st.selectbox("목장 *", group_names) if group_names else st.text_input("목장 *")

            with col3:
                new_role = st.selectbox("직분", [r.value for r in ChurchRole], index=7)  # 성도

            col1, col2, col3 = st.columns(3)
            with col1:
                new_group_role = st.selectbox("목장 직분", [r.value for r in GroupRole], index=2)  # 목원
            with col2:
                new_status = st.selectbox("상태", [s.value for s in MemberStatus], index=0)  # 재적
            with col3:
                new_type = st.selectbox("교인 구분", [t.value for t in MemberType], index=1)  # 등록교인

            submitted = st.form_submit_button("✅ 등록하기", use_container_width=True)

            if submitted:
                if not new_name or not new_phone:
                    st.error("이름과 연락처는 필수입니다.")
                else:
                    # dept_id, group_id 찾기
                    new_dept_id = ""
                    new_group_id = ""
                    if not departments.empty:
                        dept_match = departments[departments['dept_name'] == new_dept]
                        if not dept_match.empty:
                            new_dept_id = dept_match.iloc[0]['dept_id']
                    if not groups.empty:
                        group_match = groups[groups['group_name'] == new_group]
                        if not group_match.empty:
                            new_group_id = group_match.iloc[0]['group_id']

                    try:
                        member_data = MemberCreate(
                            name=new_name,
                            gender=new_gender,
                            phone=new_phone,
                            birth_date=new_birth if new_birth else None,
                            address=new_address if new_address else None,
                            dept_id=new_dept_id,
                            group_id=new_group_id,
                            church_role=new_role,
                            group_role=new_group_role,
                            status=new_status,
                            member_type=new_type
                        )

                        result = api.create_member(member_data)
                        if result.get('success'):
                            st.success(f"등록 완료! (ID: {result.get('member_id')})")
                            st.cache_data.clear()
                        else:
                            st.error(f"등록 실패: {result.get('error')}")
                    except Exception as e:
                        st.error(f"오류: {e}")

else:
    st.warning("데이터베이스에 연결할 수 없습니다. 설정을 확인해주세요.")
