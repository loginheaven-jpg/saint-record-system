
import streamlit as st
import datetime
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import time
from utils.sheets_api import SheetsAPI
from utils.ui import (
    load_custom_css, render_stat_card, render_dept_item,
    render_alert_item, render_chart_legend,
    render_dept_chart_legend, render_dept_card, render_group_grid,
    render_attendance_table, get_attendance_table_css
)


def get_nearest_sunday(d: date) -> date:
    """주어진 날짜의 해당 주 일요일 반환 (일요일이면 그대로)"""
    days_since_sunday = (d.weekday() + 1) % 7
    return d - timedelta(days=days_since_sunday)

# ============================================================
# 1. 페이지 설정 (반드시 첫 번째로 실행)
# ============================================================
st.set_page_config(
    page_title="성도기록부",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. CSS 및 UI 초기화
# ============================================================
load_custom_css()

# ============================================================
# 3. 데이터 로드 및 처리
# ============================================================
if 'api' not in st.session_state:
    try:
        st.session_state.api = SheetsAPI()
        st.session_state.db_connected = True
    except Exception as e:
        st.session_state.db_connected = False
        # 에러 메시지를 사용자에게 표시하지 않음 (콘솔에만 로깅)
        print(f"DB Connection Error: {str(e)}")

@st.cache_data(ttl=86400, show_spinner=False)  # 24시간 캐시
def fetch_dashboard_data_from_api(base_date: str):
    """
    API에서 대시보드 데이터 조회 (캐시됨)

    Args:
        base_date: 기준 날짜 (YYYY-MM-DD, 일요일)
    """
    data = {
        "total_members": 0,
        "current_attend": 0,
        "last_week_attend": 0,
        "new_members": {'count': 0, 'last_month_count': 0},
        "chart_dates": [],
        "chart_attend": [],
        "chart_total": [],
        "dept_attendance": [],
        "mokjang_attendance": [],
        "absent_3weeks": [],
        "birthdays": [],
        "last_sunday": base_date,
        # 새로 추가 (dashboard_v3 용)
        "stacked_chart_data": [],  # 8주 부서별 출석
        "dept_stats": [],          # 부서별 통계 (카드용)
        "dept_trends": {}          # 부서별 8주 트렌드 (팝오버용)
    }

    try:
        api = SheetsAPI()

        # 기준 날짜 파싱
        last_sunday = pd.Timestamp(base_date)
        last_sunday_str = base_date

        # 1. 전체 성도 (status='출석')
        df_members = api.get_members({'status': '출석'})
        data['total_members'] = len(df_members)

        # 2. 이번달 신규 등록
        data['new_members'] = api.get_new_members_this_month()

        # 3. 금주 출석 (선택된 날짜 기준)
        df_this = api.get_attendance(last_sunday.year, date=last_sunday_str)
        if not df_this.empty:
            data['current_attend'] = len(df_this[df_this['attend_type'].astype(str).isin(['1', '2'])])

        # 전주 출석
        prev_sunday = last_sunday - pd.Timedelta(days=7)
        df_prev = api.get_attendance(prev_sunday.year, date=str(prev_sunday.date()))
        if not df_prev.empty:
            data['last_week_attend'] = len(df_prev[df_prev['attend_type'].astype(str).isin(['1', '2'])])

        # 차트 데이터 (4주)
        dates = []
        attends = []
        totals = []
        for i in range(3, -1, -1):
            d = last_sunday - pd.Timedelta(days=7*i)
            d_str = d.strftime('%Y-%m-%d')
            df_d = api.get_attendance(d.year, date=d_str)
            cnt = 0
            if not df_d.empty:
                cnt = len(df_d[df_d['attend_type'].astype(str).isin(['1', '2'])])
            dates.append(d.strftime('%m/%d'))
            attends.append(cnt)
            totals.append(data['total_members'])
        data['chart_dates'] = dates
        data['chart_attend'] = attends
        data['chart_total'] = totals

        # 4. 부서별 출석
        data['dept_attendance'] = api.get_department_attendance(last_sunday_str)

        # 5. 목장별 출석
        data['mokjang_attendance'] = api.get_mokjang_attendance(last_sunday_str)

        # 6. 3주 연속 결석자
        try:
            data['absent_3weeks'] = api.get_3week_absent_members()
        except:
            data['absent_3weeks'] = []

        # 7. 이번 주 생일자
        try:
            data['birthdays'] = api.get_birthdays_this_week()
        except:
            data['birthdays'] = []

        # ===== dashboard_v3 용 데이터 =====

        # 8. 8주 부서별 출석 (스택 바 차트용)
        try:
            data['stacked_chart_data'] = api.get_8week_dept_attendance()
            print(f"[DEBUG] stacked_chart_data loaded: {len(data['stacked_chart_data'])} weeks")
        except Exception as e:
            print(f"[ERROR] get_8week_dept_attendance failed: {e}")
            data['stacked_chart_data'] = []

        # 9. 부서별 통계 (부서 카드용)
        try:
            data['dept_stats'] = api.get_dept_stats()
            print(f"[DEBUG] dept_stats loaded: {len(data['dept_stats'])} departments")
        except Exception as e:
            print(f"[ERROR] get_dept_stats failed: {e}")
            data['dept_stats'] = []

        # 10. 부서별 8주 트렌드 (팝오버 미니차트용)
        try:
            dept_trends = {}
            for dept in data['dept_stats']:
                dept_id = dept.get('dept_id', '')
                if dept_id:
                    dept_trends[dept_id] = api.get_dept_attendance_trend(dept_id)
            data['dept_trends'] = dept_trends
            print(f"[DEBUG] dept_trends loaded: {len(dept_trends)} departments")
        except Exception as e:
            print(f"[ERROR] get_dept_attendance_trend failed: {e}")
            data['dept_trends'] = {}

    except Exception as e:
        print(f"Data Load Error: {e}")

    return data

def get_dashboard_data(base_date: str, force_refresh=False):
    """대시보드 데이터 조회 (24시간 캐싱)"""
    if force_refresh:
        # 캐시 강제 삭제
        fetch_dashboard_data_from_api.clear()
        st.session_state['dashboard_cache_time'] = time.time()

    # 캐시 시간이 없으면 초기화
    if 'dashboard_cache_time' not in st.session_state:
        st.session_state['dashboard_cache_time'] = time.time()

    return fetch_dashboard_data_from_api(base_date)

# 앱 버전 체크 - 새 버전 배포 시 캐시 자동 클리어
APP_VERSION = "v3.1"  # 버전 변경 시 캐시 자동 클리어
if st.session_state.get('app_version') != APP_VERSION:
    st.session_state['app_version'] = APP_VERSION
    st.session_state['dashboard_data_loaded'] = False
    fetch_dashboard_data_from_api.clear()
    print(f"[INFO] App version updated to {APP_VERSION}, cache cleared.")

# ============================================================
# 기준 날짜 설정 (일요일만 선택 가능)
# ============================================================
# 기본값: 오늘 기준 가장 최근 일요일
today = date.today()
default_sunday = get_nearest_sunday(today)

# 세션에 선택된 날짜 저장
if 'selected_sunday' not in st.session_state:
    st.session_state.selected_sunday = default_sunday

# 선택된 날짜 문자열
selected_sunday_str = st.session_state.selected_sunday.strftime('%Y-%m-%d')

# 강제 새로고침 처리
force_refresh = st.session_state.get('force_refresh', False)
if force_refresh:
    st.session_state['force_refresh'] = False

# 로딩 표시 (데이터 로드 중)
if 'dashboard_data_loaded' not in st.session_state:
    with st.spinner("📊 데이터를 불러오는 중..."):
        dashboard_data = get_dashboard_data(selected_sunday_str, force_refresh=True)
        st.session_state['dashboard_data_loaded'] = True
else:
    dashboard_data = get_dashboard_data(selected_sunday_str, force_refresh=force_refresh)

# ============================================================
# 4. 사이드바 렌더링 (Streamlit 네이티브 네비게이션 사용)
# ============================================================
def render_sidebar():
    with st.sidebar:
        # 로고 섹션
        st.markdown('<div style="padding:1.5rem 0.75rem;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:1.5rem;"><div style="width:48px;height:48px;background:linear-gradient(135deg,#C9A962 0%,#D4B87A 100%);border-radius:14px;display:flex;align-items:center;justify-content:center;margin-bottom:16px;box-shadow:0 4px 16px rgba(201,169,98,0.3);font-size:24px;">⛪</div><div style="font-family:Playfair Display,serif;font-size:22px;font-weight:600;color:white;">성도기록부</div><div style="font-size:11px;color:rgba(255,255,255,0.5);margin-top:4px;letter-spacing:1px;">SAINT RECORD SYSTEM</div></div>', unsafe_allow_html=True)

        # 메인 섹션 라벨
        st.markdown('<div style="padding:0 0.5rem;"><div style="font-size:11px;font-weight:600;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;">메인</div></div>', unsafe_allow_html=True)

        # 대시보드 (활성) - 현재 페이지이므로 스타일링만
        st.markdown('<div style="display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:12px;background:rgba(201,169,98,0.15);color:white;margin:0 0.5rem 4px;position:relative;"><div style="position:absolute;left:0;top:0;bottom:0;width:3px;background:#C9A962;border-radius:0 2px 2px 0;"></div><span style="font-size:18px;">🏠</span><span style="font-size:14px;font-weight:500;">대시보드</span></div>', unsafe_allow_html=True)

        # 출석 입력 - 실제 네비게이션 링크
        st.page_link("pages/1_📋_출석입력.py", label="📋 출석 입력")

        # 관리 섹션 라벨
        st.markdown('<div style="padding:0 0.5rem;margin-top:20px;"><div style="font-size:11px;font-weight:600;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;">관리</div></div>', unsafe_allow_html=True)

        # 성도 관리 - 실제 네비게이션 링크
        st.page_link("pages/2_👤_성도관리.py", label="👤 성도 관리")

        # 서브메뉴 (가정관리)
        st.markdown('<div class="nav-sub-container">', unsafe_allow_html=True)
        st.page_link("pages/3_👨‍👩‍👧_가정관리.py", label="🏠 가정")
        st.markdown('</div>', unsafe_allow_html=True)

        # 조회 섹션 라벨
        st.markdown('<div style="padding:0 0.5rem;margin-top:20px;"><div style="font-size:11px;font-weight:600;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;">조회</div></div>', unsafe_allow_html=True)

        # 검색 페이지
        st.page_link("pages/4_🔍_검색.py", label="🔍 검색")

        # 분석 섹션 라벨
        st.markdown('<div style="padding:0 0.5rem;margin-top:20px;"><div style="font-size:11px;font-weight:600;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;">분석</div></div>', unsafe_allow_html=True)

        # 통계 페이지
        st.page_link("pages/5_📊_통계.py", label="📊 통계 / 보고서")

        # 설정 페이지
        st.page_link("pages/6_⚙️_설정.py", label="⚙️ 설정")

        # 푸터
        st.markdown('<div style="margin-top:auto;padding:1.5rem 1rem;border-top:1px solid rgba(255,255,255,0.1);"><div style="display:flex;align-items:center;gap:12px;"><div style="width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,#8B7355 0%,#C9A962 100%);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;color:white;">교</div><div><div style="font-size:14px;font-weight:500;color:white;">교적담당자</div><div style="font-size:12px;color:rgba(255,255,255,0.5);">관리자</div></div></div></div>', unsafe_allow_html=True)

render_sidebar()

# ============================================================
# 5. 메인 컨텐츠 렌더링
# ============================================================

# 출석 테이블 CSS 로드
st.markdown(get_attendance_table_css(), unsafe_allow_html=True)

# 헤더
col_title, col_date, col_refresh = st.columns([2, 1.5, 0.5])

with col_title:
    st.markdown('<h1 style="font-family:Playfair Display,serif;font-size:32px;font-weight:600;color:#2C3E50;margin:0 0 8px 0;">대시보드</h1><p style="font-size:14px;color:#6B7B8C;margin:0;">예봄교회 성도 현황을 한눈에 확인하세요</p>', unsafe_allow_html=True)

with col_date:
    # 날짜 선택 UI (일요일만 선택 가능)
    st.markdown('<p style="font-size:11px;color:#6B7B8C;margin:0 0 4px 0;">기준 날짜 (일요일)</p>', unsafe_allow_html=True)
    selected_date = st.date_input(
        "기준 날짜",
        value=st.session_state.selected_sunday,
        label_visibility="collapsed",
        key="date_selector"
    )
    # 일요일이 아닌 날짜 선택 시 가장 가까운 일요일로 조정
    if selected_date.weekday() != 6:  # 일요일이 아니면
        adjusted_sunday = get_nearest_sunday(selected_date)
        if adjusted_sunday != st.session_state.selected_sunday:
            st.session_state.selected_sunday = adjusted_sunday
            st.session_state['dashboard_data_loaded'] = False
            st.rerun()
    elif selected_date != st.session_state.selected_sunday:
        st.session_state.selected_sunday = selected_date
        st.session_state['dashboard_data_loaded'] = False
        st.rerun()

with col_refresh:
    # 캐시 시간 표시
    cache_time = st.session_state.get('dashboard_cache_time', 0)
    if cache_time > 0:
        cache_age_min = int((time.time() - cache_time) / 60)
        if cache_age_min < 60:
            cache_info = f"{cache_age_min}분 전"
        else:
            cache_info = f"{cache_age_min // 60}시간 전"
    else:
        cache_info = "새 데이터"
    st.markdown(f'<p style="font-size:10px;color:#6B7B8C;text-align:center;margin:8px 0 4px 0;">{cache_info}</p>', unsafe_allow_html=True)
    if st.button("🔄", key="refresh_btn", help="데이터 새로고침"):
        st.session_state['force_refresh'] = True
        st.session_state['dashboard_data_loaded'] = False
        st.rerun()

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# 통계 데이터 계산
val_total = 0
val_attend = 0
attend_rate = 0.0
last_attend_rate = 0.0
diff = 0

if dashboard_data['total_members'] > 0:
    val_total = dashboard_data['total_members']
    val_attend = dashboard_data['current_attend']
    attend_rate = (val_attend / val_total) * 100
    diff = val_attend - dashboard_data['last_week_attend']

    # 지난주 출석률 (트렌드 계산용)
    if dashboard_data['last_week_attend'] > 0:
        last_attend_rate = (dashboard_data['last_week_attend'] / val_total) * 100

# 트렌드 값 포맷팅
trend_dir = "up" if diff >= 0 else "down"
trend_sign = "+" if diff >= 0 else ""
trend_str = f"{trend_sign}{diff}"

# 출석률 트렌드
rate_diff = attend_rate - last_attend_rate
rate_trend_dir = "up" if rate_diff >= 0 else "down"
rate_trend_str = f"{'+' if rate_diff >= 0 else ''}{rate_diff:.1f}%"

# 신규 등록 데이터
new_members_data = dashboard_data['new_members']
new_count = new_members_data['count']
new_last_count = new_members_data['last_month_count']
new_diff = new_count - new_last_count
new_trend_dir = "up" if new_diff >= 0 else "down"
new_trend_str = f"{'+' if new_diff >= 0 else ''}{new_diff}"

# 통계 카드 그리드
stat_cols = st.columns(4)

with stat_cols[0]:
    html_0 = render_stat_card("users", "blue", str(val_total), "전체 성도", trend_str, trend_dir, False)
    st.markdown(html_0, unsafe_allow_html=True)

with stat_cols[1]:
    html_1 = render_stat_card("check", "white", str(val_attend), "금주 출석", trend_str, trend_dir, True)
    st.markdown(html_1, unsafe_allow_html=True)

with stat_cols[2]:
    html_2 = render_stat_card("chart", "green", f"{attend_rate:.1f}%", "출석률", rate_trend_str, rate_trend_dir, False)
    st.markdown(html_2, unsafe_allow_html=True)

with stat_cols[3]:
    html_3 = render_stat_card("user-plus", "gold", str(new_count), "신규 등록", new_trend_str, new_trend_dir, False)
    st.markdown(html_3, unsafe_allow_html=True)

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# ============================================================
# 섹션 1: 8주 출석 현황 (스택 바 차트)
# ============================================================
bar_chart_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:22px;height:22px;color:#C9A962;"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>'
st.markdown(f'''<div class="stacked-chart-section">
    <div class="section-title">{bar_chart_svg}최근 8주 출석 현황</div>
''', unsafe_allow_html=True)

# 스택 바 차트 데이터
stacked_data = dashboard_data.get('stacked_chart_data', [])

if stacked_data:
    # Plotly 스택 바 차트
    weeks = [d['week'] for d in stacked_data]
    adults_data = [d['adults'] for d in stacked_data]
    youth_data = [d['youth'] for d in stacked_data]
    teens_data = [d['teens'] for d in stacked_data]
    children_data = [d['children'] for d in stacked_data]

    fig = go.Figure()

    # 어린이부 (맨 아래)
    fig.add_trace(go.Bar(
        x=weeks, y=children_data, name='어린이부',
        marker_color='#D2691E', marker_line_width=0
    ))
    # 청소년부
    fig.add_trace(go.Bar(
        x=weeks, y=teens_data, name='청소년부',
        marker_color='#6B8E23', marker_line_width=0
    ))
    # 청년부
    fig.add_trace(go.Bar(
        x=weeks, y=youth_data, name='청년부',
        marker_color='#556B82', marker_line_width=0
    ))
    # 장년부 (맨 위)
    fig.add_trace(go.Bar(
        x=weeks, y=adults_data, name='장년부',
        marker_color='#6B5B47', marker_line_width=0
    ))

    fig.update_layout(
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=40),
        height=280,
        showlegend=False,
        barcornerradius=4,
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            tickfont=dict(size=12, color='#6B7B8C', family='Noto Sans KR')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#F0F0F0',
            showline=False,
            showticklabels=False,
            zeroline=False
        )
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.markdown('<p style="color:#6B7B8C;font-size:14px;text-align:center;padding:40px;">출석 데이터가 없습니다</p>', unsafe_allow_html=True)

# 차트 레전드 (부서별 4색)
st.markdown(render_dept_chart_legend(), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# ============================================================
# 섹션 2: 부서별 현황 (2x2 카드 + 목장 그리드)
# ============================================================
hierarchy_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:22px;height:22px;color:#C9A962;"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>'
st.markdown(f'''<div class="hierarchy-section">
    <div class="section-title">{hierarchy_svg}부서별 현황</div>
''', unsafe_allow_html=True)

# 부서 선택 상태 초기화
if 'selected_dept' not in st.session_state:
    dept_stats = dashboard_data.get('dept_stats', [])
    if dept_stats:
        st.session_state.selected_dept = dept_stats[0].get('dept_id', '')
    else:
        st.session_state.selected_dept = ''

# 부서 카드 2x2 그리드
dept_stats = dashboard_data.get('dept_stats', [])
dept_trends = dashboard_data.get('dept_trends', {})

if dept_stats:
    st.markdown('<div class="dept-container">', unsafe_allow_html=True)
    for dept in dept_stats:
        dept_id = dept.get('dept_id', '')
        trend_data = dept_trends.get(dept_id, [])
        is_active = (dept_id == st.session_state.selected_dept)

        card_html = render_dept_card(
            dept_id=dept.get('css_class', 'adults'),
            name=dept.get('name', ''),
            emoji=dept.get('emoji', '👥'),
            groups_count=dept.get('groups_count', 0),
            members_count=dept.get('members_count', 0),
            attendance_rate=dept.get('attendance_rate', 0),
            trend_data=trend_data,
            is_active=is_active
        )
        st.markdown(card_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 부서 선택 버튼 (Streamlit 네이티브)
    st.markdown('<div style="margin-top:16px;">', unsafe_allow_html=True)
    dept_cols = st.columns(len(dept_stats))
    for i, dept in enumerate(dept_stats):
        with dept_cols[i]:
            if st.button(f"📍 {dept.get('name', '')}", key=f"dept_btn_{dept.get('dept_id', i)}", use_container_width=True):
                st.session_state.selected_dept = dept.get('dept_id', '')
                st.session_state.selected_group = None  # 부서 변경 시 목장 선택 초기화
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 목장 선택 상태 초기화
    if 'selected_group' not in st.session_state:
        st.session_state.selected_group = None  # None이면 부서 전체

    # 선택된 부서의 목장 그리드
    if st.session_state.selected_dept:
        try:
            api = st.session_state.api
            groups = api.get_groups_by_dept(st.session_state.selected_dept)

            # 선택된 부서명 찾기
            selected_dept_name = "장년부"
            for dept in dept_stats:
                if dept.get('dept_id') == st.session_state.selected_dept:
                    selected_dept_name = dept.get('name', '장년부')
                    break

            if groups:
                st.markdown(render_group_grid(groups, selected_dept_name), unsafe_allow_html=True)

                # 목장 선택 버튼 (전체 + 개별 목장)
                st.markdown('<div style="margin-top:16px;">', unsafe_allow_html=True)

                # 전체 보기 + 목장 버튼들
                num_cols = min(len(groups) + 1, 6)  # 최대 6개 컬럼
                group_cols = st.columns(num_cols)

                # 전체 보기 버튼
                with group_cols[0]:
                    btn_label = "📋 전체" if st.session_state.selected_group is None else "전체"
                    if st.button(btn_label, key="group_btn_all", use_container_width=True):
                        st.session_state.selected_group = None
                        st.rerun()

                # 개별 목장 버튼
                for i, group in enumerate(groups[:num_cols-1]):
                    with group_cols[i + 1]:
                        group_id = group.get('group_id', '')
                        group_name = group.get('name', '')
                        is_selected = (st.session_state.selected_group == group_id)
                        btn_label = f"📍 {group_name}" if is_selected else group_name
                        if st.button(btn_label, key=f"group_btn_{group_id}", use_container_width=True):
                            st.session_state.selected_group = group_id
                            st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

                # ============================================================
                # 출석 현황 테이블 (B: 별도 섹션)
                # ============================================================
                st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

                # 출석 테이블 데이터 조회
                try:
                    attendance_table_data = api.get_dept_attendance_table(
                        dept_id=st.session_state.selected_dept,
                        base_date=selected_sunday_str,
                        group_id=st.session_state.selected_group
                    )

                    # 선택된 목장명 찾기
                    selected_group_name = None
                    if st.session_state.selected_group:
                        for g in groups:
                            if g.get('group_id') == st.session_state.selected_group:
                                selected_group_name = g.get('name')
                                break

                    # 출석 테이블 렌더링
                    st.markdown(
                        render_attendance_table(attendance_table_data, selected_dept_name, selected_group_name),
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.markdown(f'<div class="attendance-table-section"><p style="color:#6B7B8C;font-size:14px;text-align:center;padding:40px;">출석 데이터를 불러올 수 없습니다: {e}</p></div>', unsafe_allow_html=True)

            else:
                st.markdown(f'<div class="groups-section"><div class="groups-title">선택된 부서의 목장 ({selected_dept_name})</div><p style="color:#6B7B8C;font-size:14px;text-align:center;padding:20px;">목장 데이터가 없습니다</p></div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="groups-section"><p style="color:#6B7B8C;font-size:14px;text-align:center;padding:20px;">목장 데이터를 불러올 수 없습니다</p></div>', unsafe_allow_html=True)
else:
    st.markdown('<p style="color:#6B7B8C;font-size:14px;text-align:center;padding:40px;">부서 데이터가 없습니다</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# ============================================================
# 섹션 3: 알림
# ============================================================
st.markdown('''<div style="background:#FFFFFF;border-radius:24px;padding:28px;box-shadow:0 2px 20px rgba(44,62,80,0.06);">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="width:22px;height:22px;color:#C9A962;">
            <path d="M18 8A6 6 0 106 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 01-3.46 0"/>
        </svg>
        <span style="font-size:18px;font-weight:600;color:#2C3E50;">알림</span>
    </div>
''', unsafe_allow_html=True)

# 3주 연속 결석 알림
absent_list = dashboard_data.get('absent_3weeks', [])
if absent_list:
    names = ', '.join([m['name'] for m in absent_list[:3]])
    extra = f" 외 {len(absent_list)-3}명" if len(absent_list) > 3 else ""
    st.markdown(render_alert_item("warning", "warning", "3주 연속 결석", names + extra), unsafe_allow_html=True)
else:
    st.markdown(render_alert_item("info", "check", "출석 양호", "3주 연속 결석자가 없습니다"), unsafe_allow_html=True)

# 이번 주 생일 알림
birthdays = dashboard_data.get('birthdays', [])
if birthdays:
    bday_text = ', '.join([f"{b['name']} ({b['birth_date']})" for b in birthdays[:3]])
    extra = f" 외 {len(birthdays)-3}명" if len(birthdays) > 3 else ""
    st.markdown(render_alert_item("info", "gift", "🎂 이번 주 생일", bday_text + extra), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

