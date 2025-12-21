import streamlit as st
import pandas as pd
from utils.ui import load_custom_css
from utils.sheets_api import SheetsAPI
from utils.enums import Relationship, MemberStatus

st.set_page_config(page_title="가정 관리", page_icon="👨‍👩‍👧", layout="wide")
load_custom_css()

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

# 헤더 (대시보드 돌아가기 버튼 포함)
col_back, col_title = st.columns([1, 11])
with col_back:
    if st.button("← 대시보드", key="back_to_dashboard", use_container_width=True):
        st.switch_page("app.py")
with col_title:
    st.markdown("""
    <div class="page-header">
        <div>
            <h1>👨‍👩‍👧 가정 관리</h1>
            <p>가정별 구성원을 조회하고 관리합니다</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if db_connected:
    with st.spinner("📊 데이터를 불러오는 중..."):
        members = load_members()
        groups = load_groups()

    if not members.empty:
        # 가정 그룹핑 (family_id 기준)
        # family_id가 없는 경우 가장의 member_id를 family_id로 사용
        families = {}

        for _, member in members.iterrows():
            family_id = member.get('family_id', '')
            if not family_id or pd.isna(family_id):
                # family_id가 없으면 가장인 경우 자신의 ID 사용
                if member.get('relationship') == '가장':
                    family_id = member.get('member_id')
                else:
                    continue  # 가장이 아니고 family_id도 없으면 스킵

            if family_id not in families:
                families[family_id] = []
            families[family_id].append(member.to_dict())

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
                head = family_members[0]  # 가장이 없으면 첫 번째 멤버를 대표로

            head_name = head.get('name', '알 수 없음') if head else '알 수 없음'

            # 검색 필터
            if search_term and search_term.lower() not in head_name.lower():
                continue

            displayed_count += 1

            # 가족 구성원 정렬 (가장 → 아내 → 자녀 → 부모 → 기타)
            relation_order = {'가장': 0, '아내': 1, '아들': 2, '딸': 3, '손자': 4, '손녀': 5, '부친': 6, '모친': 7}
            sorted_members = sorted(family_members, key=lambda x: relation_order.get(x.get('relationship', '기타'), 99))

            # 카드 HTML 생성
            members_html = ""
            for m in sorted_members:
                name = m.get('name', '?')
                rel = m.get('relationship', '기타')
                tag_class = get_member_tag_class(rel)
                members_html += f'<span class="member-tag {tag_class}">{rel}: {name}</span>'

            st.markdown(f"""
            <div class="family-card">
                <div class="family-head">
                    🏠 {head_name} 가정 <span style="font-size:13px;color:#6B7B8C;font-weight:400;">({len(sorted_members)}명)</span>
                </div>
                <div class="family-members">
                    {members_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        if displayed_count == 0:
            st.info("검색 결과가 없습니다.")
    else:
        st.info("등록된 성도가 없습니다.")
else:
    st.warning("데이터베이스에 연결할 수 없습니다.")
