import streamlit as st
import pandas as pd
from utils.ui import load_custom_css
from utils.sheets_api import SheetsAPI
from utils.enums import MemberStatus, ChurchRole, GroupRole, BaptismStatus
from utils.sidebar import render_shared_sidebar

st.set_page_config(page_title="검색", page_icon="🔍", layout="wide")
load_custom_css()
render_shared_sidebar("search")

# 추가 CSS
st.markdown("""
<style>
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 19px;
    padding: 0 4px;
}
.page-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 600;
    color: #2C3E50;
    margin: 0 0 4px 0;
}
.page-header p {
    font-size: 13px;
    color: #6B7B8C;
    margin: 0;
}

/* 검색 결과 카드 */
.search-result {
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(44, 62, 80, 0.06);
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.2s ease;
}
.search-result:hover {
    box-shadow: 0 4px 16px rgba(44, 62, 80, 0.1);
    transform: translateX(4px);
}
.result-avatar {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 600;
    color: white;
    flex-shrink: 0;
}
.result-avatar.male { background: linear-gradient(135deg, #3498db 0%, #5faee3 100%); }
.result-avatar.female { background: linear-gradient(135deg, #e91e63 0%, #f06292 100%); }
.result-info { flex: 1; }
.result-name {
    font-size: 16px;
    font-weight: 600;
    color: #2C3E50;
    margin-bottom: 4px;
}
.result-detail {
    font-size: 13px;
    color: #6B7B8C;
}
.result-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    margin-left: 8px;
}
.badge-active { background: #E8F5E9; color: #2E7D32; }
.badge-inactive { background: #FFF3E0; color: #E65100; }

/* 검색 박스 */
.search-box {
    background: linear-gradient(135deg, #2C3E50 0%, #3d5a73 100%);
    border-radius: 20px;
    padding: 24px 32px;
    margin-bottom: 19px;
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

# 데이터 로드
@st.cache_data(ttl=300)
def load_members():
    if db_connected:
        return api.get_members()
    return pd.DataFrame()

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

# 페이지 헤더
st.markdown("""
<div class="page-header">
    <div>
        <h1>🔍 검색</h1>
        <p>성도 정보를 검색합니다</p>
    </div>
</div>
""", unsafe_allow_html=True)

if db_connected:
    with st.spinner("📊 데이터를 불러오는 중..."):
        members = load_members()
        departments = load_departments()
        groups = load_groups()

    # 부서/목장 이름 매핑
    dept_map = {}
    group_map = {}
    if not departments.empty:
        for _, d in departments.iterrows():
            dept_map[str(d.get('dept_id', ''))] = d.get('dept_name', '')
    if not groups.empty:
        for _, g in groups.iterrows():
            group_map[str(g.get('group_id', ''))] = g.get('group_name', '')

    # 검색 옵션
    st.markdown("### 검색 조건")

    col1, col2, col3 = st.columns(3)
    with col1:
        search_name = st.text_input("이름", placeholder="성도 이름 입력")
    with col2:
        search_phone = st.text_input("전화번호", placeholder="전화번호 입력")
    with col3:
        status_options = ['전체'] + [s.value for s in MemberStatus]
        search_status = st.selectbox("상태", status_options)

    col1, col2, col3 = st.columns(3)
    with col1:
        dept_options = ['전체']
        if not departments.empty:
            dept_options += departments['dept_name'].tolist()
        search_dept = st.selectbox("부서", dept_options)
    with col2:
        group_options = ['전체']
        if not groups.empty:
            group_options += groups['group_name'].tolist()
        search_group = st.selectbox("목장", group_options)
    with col3:
        role_options = ['전체'] + [r.value for r in ChurchRole]
        search_role = st.selectbox("직분", role_options)

    # 검색 버튼
    if st.button("🔍 검색", use_container_width=True, type="primary"):
        st.session_state.search_executed = True

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # 검색 결과
    if st.session_state.get('search_executed', False) or search_name or search_phone:
        if not members.empty:
            results = members.copy()

            # 필터 적용
            if search_name:
                results = results[results['name'].str.contains(search_name, case=False, na=False)]
            if search_phone:
                results = results[results['phone'].str.contains(search_phone, case=False, na=False)]
            if search_status != '전체':
                results = results[results['status'] == search_status]
            if search_dept != '전체' and not departments.empty:
                dept_row = departments[departments['dept_name'] == search_dept]
                if not dept_row.empty:
                    results = results[results['dept_id'] == dept_row.iloc[0]['dept_id']]
            if search_group != '전체' and not groups.empty:
                group_row = groups[groups['group_name'] == search_group]
                if not group_row.empty:
                    results = results[results['group_id'] == group_row.iloc[0]['group_id']]
            if search_role != '전체':
                results = results[results['church_role'] == search_role]

            st.markdown(f"### 검색 결과 ({len(results)}건)")

            if not results.empty:
                for _, member in results.iterrows():
                    name = member.get('name', '?')
                    gender = member.get('gender', '')
                    phone = member.get('phone', '-')
                    status = member.get('status', '-')
                    church_role = member.get('church_role', '-')
                    dept_name = dept_map.get(str(member.get('dept_id', '')), '-')
                    group_name = group_map.get(str(member.get('group_id', '')), '-')

                    avatar_class = 'male' if gender == '남' else 'female'
                    initial = name[0] if name else '?'
                    badge_class = 'badge-active' if status == '재적' else 'badge-inactive'

                    st.markdown(f"""
                    <div class="search-result">
                        <div class="result-avatar {avatar_class}">{initial}</div>
                        <div class="result-info">
                            <div class="result-name">
                                {name}
                                <span class="result-badge {badge_class}">{status}</span>
                            </div>
                            <div class="result-detail">
                                {church_role} · {dept_name} · {group_name} · {phone}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("검색 결과가 없습니다.")
        else:
            st.info("등록된 성도가 없습니다.")
    else:
        st.info("검색 조건을 입력하고 검색 버튼을 클릭하세요.")
else:
    st.warning("데이터베이스에 연결할 수 없습니다.")
