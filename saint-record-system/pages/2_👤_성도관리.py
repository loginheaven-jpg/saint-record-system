import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date
from utils.ui import load_custom_css
from utils.sheets_api import SheetsAPI
from utils.enums import MemberStatus, MemberType, ChurchRole, GroupRole, Relationship, BaptismStatus
from utils.validators import MemberCreate, MemberUpdate
from utils.sidebar import render_shared_sidebar

st.set_page_config(page_title="성도 관리", page_icon="👤", layout="wide")
load_custom_css()
render_shared_sidebar("members")

# CSS
st.markdown("""
<style>
/* 페이지 헤더 */
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

/* 테이블 컨테이너 */
.table-container {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    overflow-x: auto;
    margin-bottom: 19px;
}

/* 엑셀 스타일 테이블 */
.member-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    min-width: 1400px;
}
.member-table thead {
    background: #F8F6F3;
    position: sticky;
    top: 0;
    z-index: 10;
}
.member-table th {
    padding: 12px 10px;
    text-align: left;
    font-weight: 600;
    color: #2C3E50;
    white-space: nowrap;
    border-bottom: 2px solid #E0E0E0;
    border-right: 1px solid #E8E4DF;
}
.member-table th:last-child { border-right: none; }
.member-table tbody tr {
    border-bottom: 1px solid #E8E4DF;
    transition: background-color 0.2s;
    cursor: pointer;
}
.member-table tbody tr:hover {
    background-color: #FFFBF0;
}
.member-table td {
    padding: 10px;
    border-right: 1px solid #E8E4DF;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 150px;
}
.member-table td:last-child { border-right: none; }
.member-table th:first-child,
.member-table td:first-child {
    position: sticky;
    left: 0;
    background: white;
    z-index: 9;
    font-weight: 600;
    border-right: 2px solid #C9A962;
    min-width: 80px;
}
.member-table thead th:first-child {
    background: #F8F6F3;
    z-index: 11;
}
.member-table tbody tr:hover td:first-child {
    background-color: #FFFBF0;
}

/* 배지 */
.badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
}
.badge-head { background: #C9A962; color: white; }
.badge-spouse { background: #556B82; color: white; }
.badge-child { background: #6B8E23; color: white; }
.badge-parent { background: #E8985E; color: white; }
.badge-other { background: #999; color: white; }
.badge-active { background: #E8F5E9; color: #2E7D32; }
.badge-inactive { background: #FFF3E0; color: #E65100; }

/* 상세 정보 카드 */
.detail-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 2px 20px rgba(44, 62, 80, 0.08);
    margin-bottom: 20px;
    border-left: 4px solid #C9A962;
}
.detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 2px solid #C9A962;
}
.detail-title {
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 600;
    color: #2C3E50;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-title {
    font-size: 14px;
    font-weight: 600;
    color: #8B7355;
    margin: 20px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #E8E4DF;
}

/* 통계 미니카드 */
.mini-stat {
    background: #F8F6F3;
    border-radius: 10px;
    padding: 12px 16px;
    text-align: center;
}
.mini-stat-value {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 700;
    color: #2C3E50;
}
.mini-stat-label {
    font-size: 11px;
    color: #6B7B8C;
    margin-top: 2px;
}

/* 가정 구성원 테이블 */
.family-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    background: white;
    border-radius: 10px;
    overflow: hidden;
}
.family-table th {
    background: #F8F6F3;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
    color: #2C3E50;
    border-bottom: 2px solid #E0E0E0;
}
.family-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #E8E4DF;
}
.family-table tbody tr:hover {
    background: #FFFBF0;
}

/* 탭 스타일 */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #F8F6F3;
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 13px;
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

# 데이터 로드
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

def load_members(filters=None):
    if db_connected:
        return api.get_members(filters)
    return pd.DataFrame()

# 관계 배지 클래스
def get_relationship_badge(rel):
    badge_map = {
        '가장': 'badge-head',
        '아내': 'badge-spouse',
        '아들': 'badge-child',
        '딸': 'badge-child',
        '부친': 'badge-parent',
        '모친': 'badge-parent',
    }
    return badge_map.get(rel, 'badge-other')

# 나이 계산
def calculate_age(birth_date):
    if not birth_date:
        return '-'
    try:
        if isinstance(birth_date, str):
            birth = pd.to_datetime(birth_date).date()
        else:
            birth = birth_date
        today = date.today()
        age = today.year - birth.year
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1
        return age
    except:
        return '-'

# 페이지 헤더
st.markdown("""
<div class="page-header">
    <div>
        <h1>성도 관리</h1>
        <p>성도 정보를 조회하고 관리합니다. 성도를 선택하면 상세 정보와 가정 구성원을 확인할 수 있습니다.</p>
    </div>
</div>
""", unsafe_allow_html=True)

if db_connected:
    with st.spinner("데이터를 불러오는 중..."):
        departments = load_departments()
        groups = load_groups()

    # 세션 상태
    if 'selected_member' not in st.session_state:
        st.session_state.selected_member = None
    if 'show_detail' not in st.session_state:
        st.session_state.show_detail = False
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

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
            search_term = st.text_input("🔍 이름 검색", placeholder="성도 이름", key="search_name")

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

        members = load_members(filters if filters else None)

        # 통계
        stat_cols = st.columns(4)
        total_count = len(members) if not members.empty else 0
        active_count = len(members[members['status'] == '재적']) if not members.empty and 'status' in members.columns else 0

        with stat_cols[0]:
            st.markdown(f'<div class="mini-stat"><div class="mini-stat-value">{total_count}</div><div class="mini-stat-label">검색 결과</div></div>', unsafe_allow_html=True)
        with stat_cols[1]:
            st.markdown(f'<div class="mini-stat"><div class="mini-stat-value">{active_count}</div><div class="mini-stat-label">재적 성도</div></div>', unsafe_allow_html=True)
        with stat_cols[2]:
            st.markdown(f'<div class="mini-stat"><div class="mini-stat-value">{len(departments) if not departments.empty else 0}</div><div class="mini-stat-label">부서</div></div>', unsafe_allow_html=True)
        with stat_cols[3]:
            st.markdown(f'<div class="mini-stat"><div class="mini-stat-value">{len(groups) if not groups.empty else 0}</div><div class="mini-stat-label">목장</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # 성도 선택
        if not members.empty:
            member_names = members['name'].tolist()
            member_ids = members['member_id'].tolist()

            col_sel1, col_sel2 = st.columns([4, 1])

            with col_sel1:
                selected_idx = st.selectbox(
                    "📝 성도 선택",
                    range(len(member_names)),
                    format_func=lambda x: member_names[x],
                    key="select_member_top"
                )

            with col_sel2:
                if st.button("📋 상세보기", key="view_detail_btn", type="primary", use_container_width=True):
                    member_row = members[members['member_id'] == member_ids[selected_idx]].iloc[0]
                    st.session_state.selected_member = member_row.to_dict()
                    st.session_state.show_detail = True
                    st.session_state.edit_mode = False
                    st.rerun()

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # 상세 정보 표시
        if st.session_state.show_detail and st.session_state.selected_member:
            member = st.session_state.selected_member

            # 부서/목장 이름 조회
            dept_name = ""
            group_name = ""
            if not departments.empty and member.get('dept_id'):
                dept_match = departments[departments['dept_id'] == member.get('dept_id')]
                if not dept_match.empty:
                    dept_name = dept_match.iloc[0]['dept_name']
            if not groups.empty and member.get('group_id'):
                group_match = groups[groups['group_id'] == member.get('group_id')]
                if not group_match.empty:
                    group_name = group_match.iloc[0]['group_name']

            st.markdown(f"""
            <div class="detail-card">
                <div class="detail-header">
                    <div class="detail-title">
                        <span style="font-size:24px;">👤</span>
                        {member.get('name', '')} 상세 정보
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.edit_mode:
                # 수정 모드
                with st.form("edit_member_form"):
                    st.markdown('<div class="section-title">📋 기본 정보</div>', unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        edit_name = st.text_input("이름 *", value=member.get('name', ''))
                    with c2:
                        rel_options = [r.value for r in Relationship]
                        current_rel = member.get('relationship', '기타')
                        edit_relationship = st.selectbox("관계", rel_options,
                            index=rel_options.index(current_rel) if current_rel in rel_options else len(rel_options)-1)
                    with c3:
                        edit_birth = st.date_input("생년월일",
                            value=pd.to_datetime(member.get('birth_date')) if member.get('birth_date') else None)
                    with c4:
                        lunar_options = ['양력', '음력']
                        current_lunar = '음력' if member.get('lunar_solar') == 'N' else '양력'
                        edit_lunar = st.selectbox("양/음력", lunar_options,
                            index=lunar_options.index(current_lunar))

                    st.markdown('<div class="section-title">📞 연락처</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        edit_phone = st.text_input("전화번호", value=member.get('phone', ''))
                    with c2:
                        edit_address = st.text_input("주소", value=member.get('address', ''))

                    st.markdown('<div class="section-title">⛪ 교회 정보</div>', unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        edit_register = st.date_input("교회등록일",
                            value=pd.to_datetime(member.get('register_date')) if member.get('register_date') else None)
                    with c2:
                        baptism_options = [b.value for b in BaptismStatus]
                        current_baptism = member.get('baptism_status', '기타')
                        edit_baptism = st.selectbox("신급", baptism_options,
                            index=baptism_options.index(current_baptism) if current_baptism in baptism_options else len(baptism_options)-1)
                    with c3:
                        role_options = [r.value for r in ChurchRole]
                        current_role = member.get('church_role', '성도')
                        edit_role = st.selectbox("직분", role_options,
                            index=role_options.index(current_role) if current_role in role_options else len(role_options)-1)
                    with c4:
                        type_opts = [t.value for t in MemberType]
                        current_type = member.get('member_type', '등록교인')
                        edit_type = st.selectbox("교인 구분", type_opts,
                            index=type_opts.index(current_type) if current_type in type_opts else 1)

                    st.markdown('<div class="section-title">🏘️ 부서 및 목장</div>', unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        dept_names = departments['dept_name'].tolist() if not departments.empty else []
                        edit_dept = st.selectbox("소속부", dept_names,
                            index=dept_names.index(dept_name) if dept_name in dept_names else 0)
                    with c2:
                        group_names_list = groups['group_name'].tolist() if not groups.empty else []
                        edit_group = st.selectbox("소속목장", group_names_list,
                            index=group_names_list.index(group_name) if group_name in group_names_list else 0)
                    with c3:
                        group_role_options = [r.value for r in GroupRole]
                        current_group_role = member.get('group_role', '목원')
                        edit_group_role = st.selectbox("목장직분", group_role_options,
                            index=group_role_options.index(current_group_role) if current_group_role in group_role_options else len(group_role_options)-1)
                    with c4:
                        status_opts = [s.value for s in MemberStatus]
                        current_status = member.get('status', '재적')
                        edit_status = st.selectbox("상태", status_opts,
                            index=status_opts.index(current_status) if current_status in status_opts else 0)

                    gender_options = ['남', '여']
                    current_gender = member.get('gender', '남')
                    edit_gender = st.selectbox("성별", gender_options,
                        index=gender_options.index(current_gender) if current_gender in gender_options else 0)

                    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
                    btn_c1, btn_c2, btn_c3 = st.columns([1, 1, 4])
                    with btn_c1:
                        submitted = st.form_submit_button("💾 저장", use_container_width=True, type="primary")
                    with btn_c2:
                        if st.form_submit_button("취소", use_container_width=True):
                            st.session_state.edit_mode = False
                            st.rerun()

                    if submitted:
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
                            lunar_solar='N' if edit_lunar == '음력' else 'Y',
                            address=edit_address,
                            dept_id=new_dept_id,
                            group_id=new_group_id,
                            church_role=edit_role,
                            group_role=edit_group_role,
                            status=edit_status,
                            member_type=edit_type,
                            relationship=edit_relationship,
                            baptism_status=edit_baptism,
                            register_date=edit_register if edit_register else None
                        )

                        result = api.update_member(member.get('member_id'), update_data)
                        if result.get('success'):
                            st.success("저장되었습니다!")
                            st.session_state.edit_mode = False
                            st.session_state.show_detail = False
                            st.session_state.selected_member = None
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"저장 실패: {result.get('error')}")

            else:
                # 보기 모드 - 정보 표시
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="section-title">📋 기본 정보</div>', unsafe_allow_html=True)
                    info_html = f"""
                    <table style="width:100%;font-size:13px;">
                        <tr><td style="color:#6B7B8C;padding:6px 0;">이름</td><td style="font-weight:600;">{member.get('name', '-')}</td></tr>
                        <tr><td style="color:#6B7B8C;padding:6px 0;">관계</td><td>{member.get('relationship', '-')}</td></tr>
                        <tr><td style="color:#6B7B8C;padding:6px 0;">생년월일</td><td>{str(member.get('birth_date', '-'))[:10] if member.get('birth_date') else '-'}</td></tr>
                        <tr><td style="color:#6B7B8C;padding:6px 0;">전화번호</td><td>{member.get('phone', '-')}</td></tr>
                        <tr><td style="color:#6B7B8C;padding:6px 0;">주소</td><td>{member.get('address', '-') or '-'}</td></tr>
                    </table>
                    """
                    st.markdown(info_html, unsafe_allow_html=True)

                with col2:
                    st.markdown('<div class="section-title">⛪ 교회 정보</div>', unsafe_allow_html=True)
                    church_html = f"""
                    <table style="width:100%;font-size:13px;">
                        <tr><td style="color:#6B7B8C;padding:6px 0;">소속부</td><td style="font-weight:600;">{dept_name or '-'}</td></tr>
                        <tr><td style="color:#6B7B8C;padding:6px 0;">소속목장</td><td>{group_name or '-'}</td></tr>
                        <tr><td style="color:#6B7B8C;padding:6px 0;">직분</td><td>{member.get('church_role', '-')}</td></tr>
                        <tr><td style="color:#6B7B8C;padding:6px 0;">신급</td><td>{member.get('baptism_status', '-')}</td></tr>
                        <tr><td style="color:#6B7B8C;padding:6px 0;">상태</td><td>{member.get('status', '-')}</td></tr>
                    </table>
                    """
                    st.markdown(church_html, unsafe_allow_html=True)

                # 버튼
                st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
                btn_c1, btn_c2, btn_c3 = st.columns([1, 1, 4])
                with btn_c1:
                    if st.button("✏️ 수정", use_container_width=True, type="primary"):
                        st.session_state.edit_mode = True
                        st.rerun()
                with btn_c2:
                    if st.button("닫기", use_container_width=True):
                        st.session_state.show_detail = False
                        st.session_state.selected_member = None
                        st.rerun()

                # === 같은 가정 구성원 표시 ===
                family_id = member.get('family_id')
                if family_id and not pd.isna(family_id):
                    # 전체 멤버에서 같은 가정 조회
                    all_members = load_members()
                    family_members = all_members[all_members['family_id'] == family_id]

                    if len(family_members) > 0:
                        st.markdown('<div class="section-title">👨‍👩‍👧 같은 가정 구성원</div>', unsafe_allow_html=True)

                        # 관계 순서 정렬
                        relation_order = {'가장': 0, '아내': 1, '아들': 2, '딸': 3, '손자': 4, '손녀': 5, '부친': 6, '모친': 7}

                        # 테이블 생성
                        family_rows = []
                        for _, fm in family_members.iterrows():
                            # 부서/목장 이름 조회
                            fm_dept = ""
                            fm_group = ""
                            if not departments.empty and fm.get('dept_id'):
                                fm_dept_match = departments[departments['dept_id'] == fm.get('dept_id')]
                                if not fm_dept_match.empty:
                                    fm_dept = fm_dept_match.iloc[0]['dept_name']
                            if not groups.empty and fm.get('group_id'):
                                fm_group_match = groups[groups['group_id'] == fm.get('group_id')]
                                if not fm_group_match.empty:
                                    fm_group = fm_group_match.iloc[0]['group_name']

                            family_rows.append({
                                'sort_key': relation_order.get(fm.get('relationship', '기타'), 99),
                                'name': fm.get('name', '-'),
                                'age': calculate_age(fm.get('birth_date')),
                                'relationship': fm.get('relationship', '-'),
                                'dept': fm_dept or '-',
                                'group': fm_group or '-',
                                'is_current': fm.get('member_id') == member.get('member_id')
                            })

                        # 정렬
                        family_rows.sort(key=lambda x: x['sort_key'])

                        # 테이블 HTML
                        table_html = """
                        <table class="family-table">
                            <thead>
                                <tr>
                                    <th>이름</th>
                                    <th>나이</th>
                                    <th>관계</th>
                                    <th>부서</th>
                                    <th>목장</th>
                                </tr>
                            </thead>
                            <tbody>
                        """
                        for row in family_rows:
                            rel = row['relationship']
                            badge_class = get_relationship_badge(rel)
                            badge_html = f'<span class="badge {badge_class}">{rel}</span>'
                            if rel == '가장':
                                badge_html = f'<span class="badge {badge_class}">👑 {rel}</span>'

                            highlight = 'background:#FFFBF0;' if row['is_current'] else ''
                            name_style = 'font-weight:700;' if row['is_current'] else ''

                            table_html += f"""
                            <tr style="{highlight}">
                                <td style="{name_style}">{row['name']}</td>
                                <td>{row['age']}</td>
                                <td>{badge_html}</td>
                                <td>{row['dept']}</td>
                                <td>{row['group']}</td>
                            </tr>
                            """

                        table_html += "</tbody></table>"
                        st.markdown(table_html, unsafe_allow_html=True)

        # 테이블 표시
        if not members.empty:
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

            dept_map = {}
            group_map = {}
            if not departments.empty:
                for _, d in departments.iterrows():
                    dept_map[str(d.get('dept_id', ''))] = d.get('dept_name', '')
            if not groups.empty:
                for _, g in groups.iterrows():
                    group_map[str(g.get('group_id', ''))] = g.get('group_name', '')

            table_html = """
            <div class="scroll-wrapper">
            <div class="table-container">
            <table class="member-table">
            <thead>
                <tr>
                    <th>이름</th>
                    <th>관계</th>
                    <th>생년월일</th>
                    <th>양/음</th>
                    <th>전화번호</th>
                    <th>주소</th>
                    <th>등록일</th>
                    <th>신급</th>
                    <th>직분</th>
                    <th>소속부</th>
                    <th>소속목장</th>
                    <th>목장직분</th>
                    <th>교인</th>
                    <th>상태</th>
                </tr>
            </thead>
            <tbody>
            """

            for idx, row_member in members.iterrows():
                name = row_member.get('name', '-')
                relationship = row_member.get('relationship', '-')
                birth_date = str(row_member.get('birth_date', '-'))[:10] if row_member.get('birth_date') else '-'
                lunar = '음' if row_member.get('lunar_solar') == 'N' else '양'
                phone = row_member.get('phone', '-')
                address_raw = row_member.get('address', '')
                address = str(address_raw) if pd.notna(address_raw) and address_raw else '-'
                register_date = str(row_member.get('register_date', '-'))[:10] if row_member.get('register_date') else '-'
                baptism = row_member.get('baptism_status', '-') or '-'
                church_role = row_member.get('church_role', '-')
                dept_name_row = dept_map.get(str(row_member.get('dept_id', '')), '-')
                group_name_row = group_map.get(str(row_member.get('group_id', '')), '-')
                group_role = row_member.get('group_role', '-')
                member_type = row_member.get('member_type', '-')
                status = row_member.get('status', '-')

                rel_badge_class = get_relationship_badge(relationship)
                rel_html = f'<span class="badge {rel_badge_class}">{relationship}</span>' if relationship and relationship != '-' else '-'

                status_badge = 'badge-active' if status == '재적' else 'badge-inactive'
                status_html = f'<span class="badge {status_badge}">{status}</span>'

                table_html += f"""
                <tr>
                    <td><strong>{name}</strong></td>
                    <td>{rel_html}</td>
                    <td>{birth_date}</td>
                    <td>{lunar}</td>
                    <td>{phone}</td>
                    <td>{address[:20]}{'...' if len(str(address)) > 20 else ''}</td>
                    <td>{register_date}</td>
                    <td>{baptism}</td>
                    <td>{church_role}</td>
                    <td>{dept_name_row}</td>
                    <td>{group_name_row}</td>
                    <td>{group_role}</td>
                    <td>{member_type}</td>
                    <td>{status_html}</td>
                </tr>
                """

            table_html += "</tbody></table></div></div>"

            table_css = """
            <style>
            * { box-sizing: border-box; }
            html, body { margin: 0; padding: 0; font-family: 'Noto Sans KR', sans-serif; width: 100%; height: 100%; overflow: hidden; }
            .scroll-wrapper { width: 100%; height: 100%; overflow-x: auto; overflow-y: auto; -webkit-overflow-scrolling: touch; }
            .scroll-wrapper::-webkit-scrollbar { height: 10px; width: 8px; }
            .scroll-wrapper::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
            .scroll-wrapper::-webkit-scrollbar-thumb { background: #C9A962; border-radius: 4px; }
            .table-container { background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); display: inline-block; min-width: 100%; }
            .member-table { border-collapse: collapse; font-size: 12px; min-width: 1400px; width: max-content; }
            .member-table thead { background: #F8F6F3; position: sticky; top: 0; z-index: 10; }
            .member-table th { padding: 12px 10px; text-align: left; font-weight: 600; color: #2C3E50; white-space: nowrap; border-bottom: 2px solid #E0E0E0; border-right: 1px solid #E8E4DF; }
            .member-table th:last-child { border-right: none; }
            .member-table tbody tr { border-bottom: 1px solid #E8E4DF; transition: background-color 0.2s; cursor: pointer; }
            .member-table tbody tr:hover { background-color: #FFFBF0; }
            .member-table td { padding: 10px; border-right: 1px solid #E8E4DF; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 150px; }
            .member-table td:last-child { border-right: none; }
            .member-table th:first-child, .member-table td:first-child { position: sticky; left: 0; background: white; z-index: 9; font-weight: 600; border-right: 2px solid #C9A962; min-width: 80px; }
            .member-table thead th:first-child { background: #F8F6F3; z-index: 11; }
            .member-table tbody tr:hover td:first-child { background-color: #FFFBF0; }
            .badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; white-space: nowrap; }
            .badge-head { background: #C9A962; color: white; }
            .badge-spouse { background: #556B82; color: white; }
            .badge-child { background: #6B8E23; color: white; }
            .badge-parent { background: #E8985E; color: white; }
            .badge-other { background: #999; color: white; }
            .badge-active { background: #E8F5E9; color: #2E7D32; }
            .badge-inactive { background: #FFF3E0; color: #E65100; }
            </style>
            """
            full_html = table_css + table_html
            row_count = len(members)
            table_height = min(600, 50 + row_count * 40)
            components.html(full_html, height=table_height, scrolling=True)
        else:
            st.info("조건에 맞는 성도가 없습니다.")

    with tab2:
        st.markdown("""
        <div class="detail-card">
            <div class="detail-header">
                <div class="detail-title">
                    <span style="font-size:24px;">➕</span>
                    새 성도 등록
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("new_member_form"):
            st.markdown('<div class="section-title">📋 기본 정보</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                new_name = st.text_input("이름 *", placeholder="홍길동")
            with c2:
                new_gender = st.selectbox("성별 *", ['남', '여'])
            with c3:
                new_relationship = st.selectbox("관계", [r.value for r in Relationship], index=10)
            with c4:
                new_birth = st.date_input("생년월일", value=None)

            c1, c2 = st.columns(2)
            with c1:
                new_lunar = st.selectbox("양/음력", ['양력', '음력'])
            with c2:
                new_phone = st.text_input("전화번호 *", placeholder="010-1234-5678")

            default_address = "" if new_relationship == "가장" else "가장과 동일"
            new_address = st.text_input("주소", value=default_address)

            st.markdown('<div class="section-title">⛪ 교회 정보</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                new_register = st.date_input("교회등록일", value=None)
            with c2:
                new_baptism = st.selectbox("신급", [b.value for b in BaptismStatus], index=4)
            with c3:
                new_role = st.selectbox("직분", [r.value for r in ChurchRole], index=7)
            with c4:
                new_type = st.selectbox("교인 구분", [t.value for t in MemberType], index=1)

            st.markdown('<div class="section-title">🏘️ 부서 및 목장</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                dept_names = departments['dept_name'].tolist() if not departments.empty else []
                new_dept = st.selectbox("소속부 *", dept_names) if dept_names else st.text_input("소속부 *")
            with c2:
                group_names = groups['group_name'].tolist() if not groups.empty else []
                new_group = st.selectbox("소속목장 *", group_names) if group_names else st.text_input("소속목장 *")
            with c3:
                new_group_role = st.selectbox("목장직분", [r.value for r in GroupRole], index=3)
            with c4:
                new_status = st.selectbox("상태", [s.value for s in MemberStatus], index=0)

            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("✅ 등록하기", use_container_width=True, type="primary")

            if submitted:
                if not new_name or not new_phone:
                    st.error("이름과 연락처는 필수입니다.")
                else:
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
                            lunar_solar='N' if new_lunar == '음력' else 'Y',
                            address=new_address if new_address else None,
                            dept_id=new_dept_id,
                            group_id=new_group_id,
                            church_role=new_role,
                            group_role=new_group_role,
                            status=new_status,
                            member_type=new_type,
                            relationship=new_relationship,
                            baptism_status=new_baptism,
                            register_date=new_register if new_register else None
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
