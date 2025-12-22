import streamlit as st
import pandas as pd
from utils.ui import load_custom_css
from utils.sheets_api import SheetsAPI
from utils.enums import Relationship, MemberStatus
from utils.sidebar import render_shared_sidebar

st.set_page_config(page_title="가정 관리", page_icon="👨‍👩‍👧", layout="wide")
load_custom_css()
render_shared_sidebar("family")

# 세션 상태 초기화
if 'selected_family_id' not in st.session_state:
    st.session_state.selected_family_id = None
if 'selected_family_name' not in st.session_state:
    st.session_state.selected_family_name = None

# 추가 CSS
st.markdown("""
<style>
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
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

/* 가정 카드 */
.family-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px rgba(44, 62, 80, 0.08);
    border-left: 4px solid #C9A962;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
}
.family-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(44, 62, 80, 0.12);
    border-left-color: #B8945A;
}
.family-card .detail-link {
    position: absolute;
    top: 16px;
    right: 16px;
    font-size: 12px;
    color: #6B7B8C;
    background: #F8F6F3;
    padding: 4px 10px;
    border-radius: 12px;
    transition: all 0.2s;
}
.family-card:hover .detail-link {
    background: #C9A962;
    color: white;
}
.family-head {
    font-size: 18px;
    font-weight: 600;
    color: #2C3E50;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.family-members {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.member-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
    background: #F8F6F3;
    color: #2C3E50;
}
.member-tag.head { background: #C9A962; color: white; }
.member-tag.spouse { background: #556B82; color: white; }
.member-tag.child { background: #6B8E23; color: white; }
.member-tag.parent { background: #E8985E; color: white; }

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

/* 상세 화면 - 엑셀 스타일 테이블 */
.detail-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 2px solid #E8E4DF;
}
.detail-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 600;
    color: #2C3E50;
    margin: 0;
}
.detail-header .subtitle {
    font-size: 13px;
    color: #6B7B8C;
}

/* 테이블 컨테이너 */
.table-container {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    overflow-x: auto;
    margin-bottom: 2rem;
}

/* 엑셀 스타일 테이블 */
.family-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    min-width: 1200px;
}
.family-table thead {
    background: #F5F5F5;
    border-bottom: 2px solid #E0E0E0;
    position: sticky;
    top: 0;
    z-index: 10;
}
.family-table th {
    padding: 12px 10px;
    text-align: left;
    font-weight: 600;
    color: #2C3E50;
    white-space: nowrap;
    border-right: 1px solid #E0E0E0;
}
.family-table tbody tr {
    border-bottom: 1px solid #E0E0E0;
    transition: background-color 0.2s;
}
.family-table tbody tr:hover {
    background-color: #FFFBF0;
}
.family-table td {
    padding: 12px 10px;
    border-right: 1px solid #E0E0E0;
    white-space: nowrap;
}

/* 첫 번째 열 고정 */
.family-table th:first-child,
.family-table td:first-child {
    position: sticky;
    left: 0;
    background: white;
    z-index: 9;
    font-weight: 500;
    border-right: 2px solid #C9A962;
}
.family-table tbody tr:hover td:first-child {
    background-color: #FFFBF0;
}
.family-table thead th:first-child {
    background: #F5F5F5;
    z-index: 11;
}

/* 관계 배지 */
.rel-badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}
.rel-head { background: #C9A962; color: white; }
.rel-spouse { background: #556B82; color: white; }
.rel-child { background: #6B8E23; color: white; }
.rel-parent { background: #E8985E; color: white; }
.rel-other { background: #999; color: white; }

/* 상태 배지 */
.status-badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}
.status-active { background: #E8F5E9; color: #2E7D32; }
.status-inactive { background: #FFEBEE; color: #C62828; }
.status-leave { background: #FFF3E0; color: #E65100; }

/* 뒤로가기 버튼 */
.back-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: #F8F6F3;
    border: 1px solid #E8E4DF;
    border-radius: 8px;
    color: #2C3E50;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
}
.back-btn:hover {
    background: #E8E4DF;
}

/* 숨겨진 버튼 스타일 */
.hidden-btn {
    position: absolute;
    opacity: 0;
    pointer-events: none;
    height: 0;
    overflow: hidden;
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
def load_groups():
    if db_connected:
        return api.get_groups()
    return pd.DataFrame()

def get_member_tag_class(relationship):
    """관계에 따른 CSS 클래스 반환"""
    if relationship == '가장':
        return 'head'
    elif relationship in ['아내']:
        return 'spouse'
    elif relationship in ['아들', '딸', '손자', '손녀']:
        return 'child'
    elif relationship in ['부친', '모친']:
        return 'parent'
    return ''

def get_rel_badge_class(relationship):
    """관계에 따른 배지 CSS 클래스 반환"""
    if relationship == '가장':
        return 'rel-head'
    elif relationship in ['아내']:
        return 'rel-spouse'
    elif relationship in ['아들', '딸', '손자', '손녀']:
        return 'rel-child'
    elif relationship in ['부친', '모친']:
        return 'rel-parent'
    return 'rel-other'

def get_status_badge_class(status):
    """상태에 따른 배지 CSS 클래스 반환"""
    if status == '재적':
        return 'status-active'
    elif status in ['휴직', '장기결석']:
        return 'status-leave'
    elif status in ['별세', '전출']:
        return 'status-inactive'
    return ''

def render_family_list(members, families):
    """가정 목록 화면 렌더링"""
    # 페이지 헤더
    st.markdown("""
    <div class="page-header">
        <div>
            <h1>👨‍👩‍👧 가정 관리</h1>
            <p>가정별 구성원을 조회하고 관리합니다. 가정을 클릭하면 상세 정보를 볼 수 있습니다.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 통계
    total_families = len(families)
    total_members = len(members)
    avg_size = round(total_members / total_families, 1) if total_families > 0 else 0

    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.markdown(f'<div class="mini-stat"><div class="mini-stat-value">{total_families}</div><div class="mini-stat-label">총 가정 수</div></div>', unsafe_allow_html=True)
    with stat_cols[1]:
        st.markdown(f'<div class="mini-stat"><div class="mini-stat-value">{total_members}</div><div class="mini-stat-label">총 성도 수</div></div>', unsafe_allow_html=True)
    with stat_cols[2]:
        st.markdown(f'<div class="mini-stat"><div class="mini-stat-value">{avg_size}</div><div class="mini-stat-label">평균 가족 수</div></div>', unsafe_allow_html=True)
    with stat_cols[3]:
        active_count = len(members[members['status'] == '재적']) if 'status' in members.columns else 0
        st.markdown(f'<div class="mini-stat"><div class="mini-stat-value">{active_count}</div><div class="mini-stat-label">재적 성도</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # 검색
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 가장 이름 검색", placeholder="가장 이름으로 검색", label_visibility="collapsed")

    # 가정 카드 표시
    displayed_count = 0
    for family_id, family_members in families.items():
        # 가장 찾기
        head = None
        for m in family_members:
            if m.get('relationship') == '가장':
                head = m
                break

        if not head and family_members:
            head = family_members[0]

        head_name = head.get('name', '알 수 없음') if head else '알 수 없음'

        # 검색 필터
        if search_term and search_term.lower() not in head_name.lower():
            continue

        displayed_count += 1

        # 가족 구성원 정렬
        relation_order = {'가장': 0, '아내': 1, '아들': 2, '딸': 3, '손자': 4, '손녀': 5, '부친': 6, '모친': 7}
        sorted_members = sorted(family_members, key=lambda x: relation_order.get(x.get('relationship', '기타'), 99))

        # 카드 HTML 생성
        members_html = ""
        for m in sorted_members:
            name = m.get('name', '?')
            rel = m.get('relationship', '기타')
            tag_class = get_member_tag_class(rel)
            members_html += f'<span class="member-tag {tag_class}">{rel}: {name}</span>'

        # 카드 클릭 가능하게 (상세 버튼 내부 배치)
        st.markdown(f"""
        <div class="family-card" onclick="document.getElementById('family_btn_{family_id}').click();">
            <span class="detail-link">상세 →</span>
            <div class="family-head">
                🏠 {head_name} 가정 <span style="font-size:13px;color:#6B7B8C;font-weight:400;">({len(sorted_members)}명)</span>
            </div>
            <div class="family-members">
                {members_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 숨겨진 버튼 (클릭 이벤트용)
        st.markdown('<div class="hidden-btn">', unsafe_allow_html=True)
        if st.button("상세", key=f"family_btn_{family_id}"):
            st.session_state.selected_family_id = family_id
            st.session_state.selected_family_name = head_name
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if displayed_count == 0:
        st.info("검색 결과가 없습니다.")


def render_family_detail(family_id, family_members, head_name):
    """가정 상세 화면 렌더링 (엑셀 스타일 테이블)"""

    # 뒤로가기 버튼
    if st.button("← 가정 목록으로", key="back_btn"):
        st.session_state.selected_family_id = None
        st.session_state.selected_family_name = None
        st.rerun()

    st.markdown(f"""
    <div class="detail-header">
        <div>
            <h1>🏠 {head_name} 가정</h1>
            <span class="subtitle">가족 구성원 {len(family_members)}명의 상세 정보</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 가족 구성원 정렬
    relation_order = {'가장': 0, '아내': 1, '아들': 2, '딸': 3, '손자': 4, '손녀': 5, '부친': 6, '모친': 7}
    sorted_members = sorted(family_members, key=lambda x: relation_order.get(x.get('relationship', '기타'), 99))

    # 테이블 헤더
    header_cols = ["성명", "관계", "생년월일", "전화번호", "부서", "목장", "직분", "신급", "상태", "등록일"]

    # 테이블 HTML 생성 (한 줄로)
    rows_html = ""
    for member in sorted_members:
        rel = member.get('relationship', '기타')
        rel_class = get_rel_badge_class(rel)
        status = member.get('status', '재적')
        status_class = get_status_badge_class(status)

        # 생년월일 포맷
        birth = member.get('birth_date', '')
        if birth and isinstance(birth, str) and len(birth) >= 10:
            birth = birth[:10]

        # 등록일 포맷
        reg_date = member.get('register_date', '')
        if reg_date and isinstance(reg_date, str) and len(reg_date) >= 10:
            reg_date = reg_date[:10]

        rows_html += f'<tr><td><strong>{member.get("name", "-")}</strong></td><td><span class="rel-badge {rel_class}">{rel}</span></td><td>{birth or "-"}</td><td>{member.get("phone", "-") or "-"}</td><td>{member.get("dept_name", "-") or "-"}</td><td>{member.get("group_name", "-") or "-"}</td><td>{member.get("position", "-") or "-"}</td><td>{member.get("faith_level", "-") or "-"}</td><td><span class="status-badge {status_class}">{status}</span></td><td>{reg_date or "-"}</td></tr>'

    header_html = "".join([f"<th>{col}</th>" for col in header_cols])
    table_html = f'<div class="table-container"><table class="family-table"><thead><tr>{header_html}</tr></thead><tbody>{rows_html}</tbody></table></div>'
    st.markdown(table_html, unsafe_allow_html=True)

    # 가족 통계
    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    stat_cols = st.columns(4)
    with stat_cols[0]:
        active_count = len([m for m in sorted_members if m.get('status') == '재적'])
        st.markdown(f'<div class="mini-stat"><div class="mini-stat-value">{active_count}</div><div class="mini-stat-label">재적 인원</div></div>', unsafe_allow_html=True)
    with stat_cols[1]:
        position_count = len([m for m in sorted_members if m.get('position') and m.get('position') not in ['-', '', '없음']])
        st.markdown(f'<div class="mini-stat"><div class="mini-stat-value">{position_count}</div><div class="mini-stat-label">직분자</div></div>', unsafe_allow_html=True)
    with stat_cols[2]:
        baptized_count = len([m for m in sorted_members if m.get('faith_level') in ['세례', '입교']])
        st.markdown(f'<div class="mini-stat"><div class="mini-stat-value">{baptized_count}</div><div class="mini-stat-label">세례/입교</div></div>', unsafe_allow_html=True)
    with stat_cols[3]:
        st.markdown(f'<div class="mini-stat"><div class="mini-stat-value">{len(sorted_members)}</div><div class="mini-stat-label">총 가족 수</div></div>', unsafe_allow_html=True)


# ============================================================
# 메인 로직
# ============================================================
if db_connected:
    with st.spinner("📊 데이터를 불러오는 중..."):
        members = load_members()
        groups = load_groups()

    if not members.empty:
        # 가정 그룹핑 (family_id 기준)
        families = {}

        for _, member in members.iterrows():
            family_id = member.get('family_id', '')
            if not family_id or pd.isna(family_id):
                if member.get('relationship') == '가장':
                    family_id = member.get('member_id')
                else:
                    continue

            if family_id not in families:
                families[family_id] = []
            families[family_id].append(member.to_dict())

        # 선택된 가정이 있으면 상세 화면, 없으면 목록 화면
        if st.session_state.selected_family_id:
            family_id = st.session_state.selected_family_id
            if family_id in families:
                render_family_detail(
                    family_id,
                    families[family_id],
                    st.session_state.selected_family_name or "가정"
                )
            else:
                st.error("해당 가정을 찾을 수 없습니다.")
                st.session_state.selected_family_id = None
                st.rerun()
        else:
            render_family_list(members, families)
    else:
        st.info("등록된 성도가 없습니다.")
else:
    st.warning("데이터베이스에 연결할 수 없습니다.")
