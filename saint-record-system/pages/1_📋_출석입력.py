import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from utils.ui import load_custom_css
from utils.sheets_api import SheetsAPI
from utils.enums import AttendType, MemberStatus
from utils.validators import AttendanceCreate

st.set_page_config(page_title="출석 입력", page_icon="📋", layout="wide")
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

/* 날짜 선택 카드 */
.date-card {
    background: linear-gradient(135deg, #2C3E50 0%, #3d5a73 100%);
    border-radius: 20px;
    padding: 24px 32px;
    color: white;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.date-card-left {
    display: flex;
    align-items: center;
    gap: 20px;
}
.date-icon {
    width: 60px;
    height: 60px;
    background: rgba(255,255,255,0.15);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
}
.date-info h2 {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 600;
    margin: 0 0 4px 0;
}
.date-info p {
    font-size: 14px;
    color: rgba(255,255,255,0.7);
    margin: 0;
}

/* 통계 바 */
.stats-bar {
    display: flex;
    gap: 24px;
    padding: 20px 24px;
    background: #F8F6F3;
    border-radius: 16px;
    margin-bottom: 24px;
}
.stat-item {
    display: flex;
    align-items: center;
    gap: 10px;
}
.stat-dot {
    width: 12px;
    height: 12px;
    border-radius: 4px;
}
.stat-dot.present { background: #4A9B7F; }
.stat-dot.online { background: #3498db; }
.stat-dot.absent { background: #E8985E; }
.stat-label {
    font-size: 13px;
    color: #6B7B8C;
}
.stat-value {
    font-size: 18px;
    font-weight: 700;
    color: #2C3E50;
    font-family: 'Playfair Display', serif;
}

/* 성도 행 */
.member-row {
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 2px 8px rgba(44, 62, 80, 0.04);
    transition: all 0.3s ease;
}
.member-row:hover {
    transform: translateX(4px);
    box-shadow: 0 4px 16px rgba(44, 62, 80, 0.08);
}
.member-avatar {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 600;
    color: white;
    flex-shrink: 0;
}
.member-avatar.male { background: linear-gradient(135deg, #3498db 0%, #5faee3 100%); }
.member-avatar.female { background: linear-gradient(135deg, #e91e63 0%, #f06292 100%); }

.member-info { flex: 1; }
.member-name { font-size: 15px; font-weight: 600; color: #2C3E50; }
.member-role { font-size: 12px; color: #6B7B8C; }
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

# 헬퍼 함수
def get_week_number(d: date) -> int:
    return d.isocalendar()[1]

def get_sunday_of_week(d: date) -> date:
    days_since_sunday = (d.weekday() + 1) % 7
    return d - timedelta(days=days_since_sunday)

# 데이터 로드
@st.cache_data(ttl=60)
def load_departments():
    if db_connected:
        return api.get_departments()
    return pd.DataFrame()

@st.cache_data(ttl=60)
def load_groups():
    if db_connected:
        return api.get_groups()
    return pd.DataFrame()

@st.cache_data(ttl=60)
def load_members_by_group(group_id: str = None):
    if db_connected:
        filters = {'status': MemberStatus.ACTIVE.value}
        if group_id:
            filters['group_id'] = group_id
        return api.get_members(filters)
    return pd.DataFrame()

def load_attendance(year: int, week_no: int):
    if db_connected:
        return api.get_attendance(year, week_no=week_no)
    return pd.DataFrame()

# 헤더
st.markdown("""
<div class="page-header">
    <div>
        <h1>출석 입력</h1>
        <p>주일 예배 출석을 기록합니다</p>
    </div>
</div>
""", unsafe_allow_html=True)

if db_connected:
    departments = load_departments()
    groups = load_groups()

    # 날짜 선택
    col1, col2 = st.columns([3, 1])
    with col1:
        today = date.today()
        default_sunday = get_sunday_of_week(today)
        selected_date = st.date_input("출석 날짜", value=default_sunday, label_visibility="collapsed")

    year = selected_date.year
    week_no = get_week_number(selected_date)

    weekday_names = ['월', '화', '수', '목', '금', '토', '일']
    weekday = weekday_names[selected_date.weekday()]

    st.markdown(f"""
    <div class="date-card">
        <div class="date-card-left">
            <div class="date-icon">📅</div>
            <div class="date-info">
                <h2>{selected_date.year}년 {selected_date.month}월 {selected_date.day}일 ({weekday})</h2>
                <p>{year}년 {week_no}주차 예배</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 목장 선택
    if not groups.empty:
        group_list = groups['group_name'].tolist()
        group_ids = groups['group_id'].tolist()

        if 'selected_group_idx' not in st.session_state:
            st.session_state.selected_group_idx = 0
        if 'attendance_data' not in st.session_state:
            st.session_state.attendance_data = {}

        selected_group_name = st.selectbox("목장 선택", group_list, index=st.session_state.selected_group_idx, key="group_select")
        selected_group_idx = group_list.index(selected_group_name)
        selected_group_id = group_ids[selected_group_idx]

        members = load_members_by_group(selected_group_id)
        existing_attendance = load_attendance(year, week_no)

        attendance_key = f"{selected_date}_{selected_group_id}"
        if attendance_key not in st.session_state.attendance_data:
            st.session_state.attendance_data[attendance_key] = {}
            if not members.empty:
                for _, member in members.iterrows():
                    member_id = member.get('member_id')
                    if not existing_attendance.empty:
                        member_attend = existing_attendance[existing_attendance['member_id'] == member_id]
                        if not member_attend.empty:
                            st.session_state.attendance_data[attendance_key][member_id] = str(member_attend.iloc[0]['attend_type'])
                        else:
                            st.session_state.attendance_data[attendance_key][member_id] = '0'
                    else:
                        st.session_state.attendance_data[attendance_key][member_id] = '0'

        # 일괄 버튼
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        with col1:
            if st.button("✅ 전체 출석", use_container_width=True):
                for member_id in st.session_state.attendance_data[attendance_key]:
                    st.session_state.attendance_data[attendance_key][member_id] = '1'
                st.rerun()
        with col2:
            if st.button("💻 전체 온라인", use_container_width=True):
                for member_id in st.session_state.attendance_data[attendance_key]:
                    st.session_state.attendance_data[attendance_key][member_id] = '2'
                st.rerun()
        with col3:
            if st.button("❌ 전체 결석", use_container_width=True):
                for member_id in st.session_state.attendance_data[attendance_key]:
                    st.session_state.attendance_data[attendance_key][member_id] = '0'
                st.rerun()

        # 통계
        attend_counts = {'1': 0, '2': 0, '0': 0}
        for member_id, status in st.session_state.attendance_data.get(attendance_key, {}).items():
            attend_counts[status] = attend_counts.get(status, 0) + 1
        total = sum(attend_counts.values())
        present_rate = int((attend_counts['1'] + attend_counts['2']) / total * 100) if total > 0 else 0

        st.markdown(f"""
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-dot present"></div>
                <span class="stat-label">출석</span>
                <span class="stat-value">{attend_counts['1']}</span>
            </div>
            <div class="stat-item">
                <div class="stat-dot online"></div>
                <span class="stat-label">온라인</span>
                <span class="stat-value">{attend_counts['2']}</span>
            </div>
            <div class="stat-item">
                <div class="stat-dot absent"></div>
                <span class="stat-label">결석</span>
                <span class="stat-value">{attend_counts['0']}</span>
            </div>
            <div class="stat-item" style="margin-left: auto;">
                <span class="stat-label">출석률</span>
                <span class="stat-value">{present_rate}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 성도 목록
        if not members.empty:
            for idx, member in members.iterrows():
                member_id = member.get('member_id')
                name = member.get('name', '?')
                gender = member.get('gender', '')
                church_role = member.get('church_role', '')
                group_role = member.get('group_role', '')

                current_status = st.session_state.attendance_data.get(attendance_key, {}).get(member_id, '0')
                avatar_class = 'male' if gender == '남' else 'female'
                initial = name[0] if name else '?'

                col1, col2, col3, col4 = st.columns([0.5, 2, 1.5, 2])

                with col1:
                    st.markdown(f'<div class="member-avatar {avatar_class}">{initial}</div>', unsafe_allow_html=True)

                with col2:
                    role_text = church_role
                    if group_role and group_role != '목원':
                        role_text = f"{group_role} · {church_role}"
                    st.markdown(f'''
                    <div class="member-info">
                        <div class="member-name">{name}</div>
                        <div class="member-role">{role_text}</div>
                    </div>
                    ''', unsafe_allow_html=True)

                with col3:
                    status_text = {'1': '✅ 출석', '2': '💻 온라인', '0': '❌ 결석'}
                    status_color = {'1': '#4A9B7F', '2': '#3498db', '0': '#E8985E'}
                    st.markdown(f'<div style="font-weight:600; color:{status_color.get(current_status)}">{status_text.get(current_status)}</div>', unsafe_allow_html=True)

                with col4:
                    btn_cols = st.columns(3)
                    with btn_cols[0]:
                        if st.button("출석", key=f"p_{member_id}", use_container_width=True):
                            st.session_state.attendance_data[attendance_key][member_id] = '1'
                            st.rerun()
                    with btn_cols[1]:
                        if st.button("온라인", key=f"o_{member_id}", use_container_width=True):
                            st.session_state.attendance_data[attendance_key][member_id] = '2'
                            st.rerun()
                    with btn_cols[2]:
                        if st.button("결석", key=f"a_{member_id}", use_container_width=True):
                            st.session_state.attendance_data[attendance_key][member_id] = '0'
                            st.rerun()

                st.markdown("<hr style='border:none;border-top:1px solid #E8E4DF;margin:8px 0;'>", unsafe_allow_html=True)
        else:
            st.info("해당 목장에 등록된 성도가 없습니다.")

        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

        if st.button("💾 출석 저장", use_container_width=True, type="primary"):
            if not members.empty:
                records = []
                for member_id, attend_type in st.session_state.attendance_data.get(attendance_key, {}).items():
                    records.append(AttendanceCreate(
                        member_id=member_id,
                        attend_date=selected_date,
                        attend_type=AttendType(attend_type),
                        year=year,
                        week_no=week_no
                    ))
                if records:
                    result = api.save_attendance(records)
                    if result.get('success'):
                        st.success(f"저장 완료! (저장: {result.get('inserted')}건)")
                        st.cache_data.clear()
                    else:
                        st.error(f"저장 실패: {result.get('error')}")
    else:
        st.warning("목장 데이터가 없습니다.")
else:
    st.warning("데이터베이스에 연결할 수 없습니다.")
