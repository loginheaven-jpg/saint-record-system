
import streamlit as st
import datetime
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import time
from utils.sheets_api import SheetsAPI, clear_sheets_cache
from utils.ui import (
    load_custom_css, render_stat_card, render_dept_item,
    render_alert_item, render_chart_legend,
    render_dept_chart_legend, render_dept_card,
    get_attendance_table_css
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

        # 1. 전체 재적 성도 (status='재적' - 출석률 모수)
        df_members = api.get_members({'status': '재적'})
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

        # 9. 부서별 통계 (부서 카드용) - 선택된 날짜 기준
        try:
            data['dept_stats'] = api.get_dept_stats(base_date)
            print(f"[DEBUG] dept_stats loaded: {len(data['dept_stats'])} departments (base_date={base_date})")
        except Exception as e:
            print(f"[ERROR] get_dept_stats failed: {e}")
            data['dept_stats'] = []

        # 10. 부서별 8주 트렌드 (팝오버 미니차트용) - 선택된 날짜 기준
        try:
            dept_trends = {}
            for dept in data['dept_stats']:
                dept_id = dept.get('dept_id', '')
                if dept_id:
                    dept_trends[dept_id] = api.get_dept_attendance_trend(dept_id, base_date)
            data['dept_trends'] = dept_trends
            print(f"[DEBUG] dept_trends loaded: {len(dept_trends)} departments (base_date={base_date})")
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
APP_VERSION = "v3.14"  # 기본 메뉴 비활성화 + 버전 표시 추가
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

        # 버전 표시 (사이드바 하단)
        st.markdown(f'<div style="text-align:center;padding:8px;font-size:11px;color:rgba(255,255,255,0.4);">{APP_VERSION}</div>', unsafe_allow_html=True)

render_sidebar()

# ============================================================
# 5. 메인 컨텐츠 렌더링
# ============================================================

# 출석 테이블 CSS 로드
st.markdown(get_attendance_table_css(), unsafe_allow_html=True)

# 헤더 (제목 + 날짜 + 알림 + 새로고침)
col_title, col_date, col_alerts, col_refresh = st.columns([1.8, 1, 1.8, 0.4])

with col_title:
    st.markdown('<h1 style="font-family:Playfair Display,serif;font-size:32px;font-weight:600;color:#2C3E50;margin:0 0 4px 0;">대시보드</h1><p style="font-size:13px;color:#6B7B8C;margin:0;">예봄교회 성도 현황</p>', unsafe_allow_html=True)

with col_date:
    # 날짜 선택 UI
    st.markdown('<p style="font-size:10px;color:#6B7B8C;margin:0 0 2px 0;">기준 날짜</p>', unsafe_allow_html=True)
    selected_date = st.date_input(
        "기준 날짜",
        value=st.session_state.selected_sunday,
        label_visibility="collapsed",
        key="date_selector"
    )
    new_sunday = selected_date if selected_date.weekday() == 6 else get_nearest_sunday(selected_date)

    if new_sunday != st.session_state.selected_sunday:
        st.session_state.selected_sunday = new_sunday
        st.rerun()

    if selected_date.weekday() != 6:
        st.caption(f"⚠️ {new_sunday.strftime('%m/%d')}(일)로 조정됨")

with col_alerts:
    # 알림 배지 (결석자, 생일자) - 커스텀 HTML 배지
    absent_list = dashboard_data.get('absent_3weeks', [])
    birthdays = dashboard_data.get('birthdays', [])
    absent_count = len(absent_list)
    bday_count = len(birthdays)

    # 결석자 상세 목록 생성
    absent_detail = ""
    if absent_count > 0:
        dept_absent = {}
        for m in absent_list:
            dept = m.get('dept_name', '기타')
            if dept not in dept_absent:
                dept_absent[dept] = []
            dept_absent[dept].append(m['name'])
        for dept, names in dept_absent.items():
            absent_detail += f"<div style='margin-bottom:4px;'><strong>{dept}</strong> ({len(names)}명): {', '.join(names)}</div>"

    # 생일자 상세 목록 생성
    bday_detail = ""
    if bday_count > 0:
        dept_bday = {}
        for b in birthdays:
            dept = b.get('dept_name', '기타')
            if dept not in dept_bday:
                dept_bday[dept] = []
            dept_bday[dept].append(f"{b['name']} ({b['birth_date']})")
        for dept, names in dept_bday.items():
            bday_detail += f"<div style='margin-bottom:4px;'><strong>{dept}</strong> ({len(names)}명): {', '.join(names)}</div>"

    # 알림 배지 HTML (클릭 가능한 토글 스타일)
    alert_html = f'''
    <style>
    .alert-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 8px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
        margin-right: 8px;
    }}
    .alert-badge.warning {{
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        color: #E65100;
        border: 1px solid #FFB74D;
    }}
    .alert-badge.info {{
        background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
        color: #F57F17;
        border: 1px solid #FFD54F;
    }}
    .alert-badge.success {{
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        color: #2E7D32;
        border: 1px solid #81C784;
    }}
    .alert-badge:hover {{
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .alert-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
    }}
    </style>
    <div class="alert-container">
        <div class="alert-badge {'warning' if absent_count > 0 else 'success'}">
            {'⚠️' if absent_count > 0 else '✓'} 3주 연속 결석 {absent_count}명
        </div>
        <div class="alert-badge {'info' if bday_count > 0 else 'success'}">
            {'🎂' if bday_count > 0 else '✓'} 금주 생일 {bday_count}명
        </div>
    </div>
    '''
    st.markdown(alert_html, unsafe_allow_html=True)

    # 상세 내용 토글 (버튼으로 제어)
    if absent_count > 0 or bday_count > 0:
        if st.button("📋 상세 보기", key="alert_detail_btn", type="secondary"):
            st.session_state['show_alert_detail'] = not st.session_state.get('show_alert_detail', False)

        if st.session_state.get('show_alert_detail', False):
            detail_cols = st.columns(2)
            with detail_cols[0]:
                if absent_count > 0:
                    st.markdown(f'''
                    <div style="background:#FFF8E1;border-radius:12px;padding:14px;border-left:4px solid #E65100;">
                        <div style="font-weight:700;color:#E65100;margin-bottom:8px;font-size:14px;">⚠️ 3주 연속 결석 ({absent_count}명)</div>
                        <div style="font-size:12px;color:#5D4037;line-height:1.6;">{absent_detail}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            with detail_cols[1]:
                if bday_count > 0:
                    st.markdown(f'''
                    <div style="background:#FFFDE7;border-radius:12px;padding:14px;border-left:4px solid #F57F17;">
                        <div style="font-weight:700;color:#F57F17;margin-bottom:8px;font-size:14px;">🎂 금주 생일 ({bday_count}명)</div>
                        <div style="font-size:12px;color:#5D4037;line-height:1.6;">{bday_detail}</div>
                    </div>
                    ''', unsafe_allow_html=True)

with col_refresh:
    cache_time = st.session_state.get('dashboard_cache_time', 0)
    if cache_time > 0:
        cache_age_min = int((time.time() - cache_time) / 60)
        cache_info = f"{cache_age_min}분" if cache_age_min < 60 else f"{cache_age_min // 60}h"
    else:
        cache_info = "new"
    st.markdown(f'<p style="font-size:9px;color:#6B7B8C;text-align:center;margin:4px 0 2px 0;">{cache_info}</p>', unsafe_allow_html=True)
    if st.button("🔄", key="refresh_btn", help="데이터 새로고침"):
        fetch_dashboard_data_from_api.clear()
        clear_sheets_cache()
        st.session_state['force_refresh'] = True
        st.session_state['dashboard_data_loaded'] = False
        st.session_state['dashboard_cache_time'] = 0
        st.rerun()

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

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

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# ============================================================
# 섹션 1: 8주 출석 현황 (스택 바 차트)
# ============================================================
bar_chart_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;color:#C9A962;"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>'
st.markdown(f'''<div class="stacked-chart-section" style="padding:12px 20px;">
    <div class="section-title" style="font-size:15px;margin-bottom:8px;">{bar_chart_svg}최근 8주 출석 현황</div>
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

    # 합계 계산 (바 위에 표시용)
    totals = [a + y + t + c for a, y, t, c in zip(adults_data, youth_data, teens_data, children_data)]

    fig = go.Figure()

    # 어린이부 (맨 아래) - 숫자 내부 표시, textangle=0으로 회전 방지
    fig.add_trace(go.Bar(
        x=weeks, y=children_data, name='어린이부',
        marker_color='#D2691E', marker_line_width=0,
        text=children_data, textposition='inside',
        textfont=dict(color='white', size=12),
        insidetextanchor='middle', textangle=0
    ))
    # 청소년부 - 숫자 내부 표시, textangle=0으로 회전 방지
    fig.add_trace(go.Bar(
        x=weeks, y=teens_data, name='청소년부',
        marker_color='#6B8E23', marker_line_width=0,
        text=teens_data, textposition='inside',
        textfont=dict(color='white', size=12),
        insidetextanchor='middle', textangle=0
    ))
    # 청년부 - 숫자 내부 표시, textangle=0으로 회전 방지
    fig.add_trace(go.Bar(
        x=weeks, y=youth_data, name='청년부',
        marker_color='#556B82', marker_line_width=0,
        text=youth_data, textposition='inside',
        textfont=dict(color='white', size=12),
        insidetextanchor='middle', textangle=0
    ))
    # 장년부 (맨 위) - 숫자 내부 표시, textangle=0으로 회전 방지
    fig.add_trace(go.Bar(
        x=weeks, y=adults_data, name='장년부',
        marker_color='#6B5B47', marker_line_width=0,
        text=adults_data, textposition='inside',
        textfont=dict(color='white', size=12),
        insidetextanchor='middle', textangle=0
    ))

    # 합계를 바 위에 표시 (scatter로 추가)
    fig.add_trace(go.Scatter(
        x=weeks, y=totals, mode='text',
        text=[str(t) for t in totals],
        textposition='top center',
        textfont=dict(color='#2C3E50', size=13, weight='bold'),
        showlegend=False
    ))

    fig.update_layout(
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=40),
        height=380,
        showlegend=False,
        barcornerradius=4,
        dragmode=False,
        uniformtext=dict(minsize=8, mode='show'),  # 작은 바에도 텍스트 강제 표시
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

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})
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

# 부서 카드 그리드 (클릭 가능한 통합 UI)
dept_stats = dashboard_data.get('dept_stats', [])
dept_trends = dashboard_data.get('dept_trends', {})

# 부서 버튼 색상 매핑 (차트 색상과 일치)
DEPT_COLORS = {
    'adults': '#6B5B47',    # 장년부
    'youth': '#556B82',     # 청년부
    'teens': '#6B8E23',     # 청소년부
    'children': '#D2691E',  # 어린이부
}

# 부서 버튼 커스텀 CSS (선택 시 부서 색상 적용)
# 부서 인덱스와 색상을 매핑하여 nth-child 선택자 사용
selected_dept = st.session_state.get('selected_dept', '')
selected_idx = None
selected_color = '#C9A962'

for i, dept in enumerate(dept_stats):
    if dept.get('dept_id', '') == selected_dept:
        selected_idx = i + 1  # CSS nth-child는 1부터 시작
        css_class = dept.get('css_class', 'adults')
        selected_color = DEPT_COLORS.get(css_class, '#C9A962')
        break

# CSS 선택자 방식 제거 - 버튼 아래에 직접 색상 바 추가로 변경

if dept_stats:
    # 부서 수에 따라 컬럼 생성 (기본 4개)
    dept_cols = st.columns(len(dept_stats))

    for i, dept in enumerate(dept_stats):
        dept_id = dept.get('dept_id', '')
        dept_name = dept.get('name', '')
        is_active = (dept_id == st.session_state.selected_dept)
        trend_data = dept_trends.get(dept_id, [])

        with dept_cols[i]:
            # 부서 고유 색상
            css_class = dept.get('css_class', 'adults')
            dept_color = DEPT_COLORS.get(css_class, '#C9A962')

            # 부서 선택 버튼 (클릭 가능)
            btn_type = "primary" if is_active else "secondary"
            if st.button(
                f"{dept.get('emoji', '👥')} {dept_name}",
                key=f"dept_card_{dept_id}",
                use_container_width=True,
                type=btn_type
            ):
                st.session_state.selected_dept = dept_id
                st.session_state.selected_group = None  # 부서 변경 시 목장 선택 초기화
                st.rerun()

            # 선택된 부서일 경우 부서 고유색 바 표시
            if is_active:
                st.markdown(f'<div style="height:4px;background:{dept_color};border-radius:2px;margin-top:-8px;margin-bottom:8px;"></div>', unsafe_allow_html=True)

            # 부서 통계 카드 (시각적 정보)
            groups_count = dept.get('groups_count', 0)
            members_count = dept.get('members_count', 0)
            attendance_rate = dept.get('attendance_rate', 0)
            attendance_count = int(members_count * attendance_rate / 100) if members_count > 0 else 0
            group_label = "반" if dept.get('css_class') == "children" else "목장"

            # 미니 트렌드 라인차트 생성 (꺾은선 + 점 아래 숫자)
            trend_chart = ""
            if trend_data and len(trend_data) > 0:
                max_val = max(trend_data) if max(trend_data) > 0 else 100
                min_val = min(trend_data) if min(trend_data) > 0 else 0
                range_val = max_val - min_val if max_val != min_val else 1

                # SVG 꺾은선 차트 생성
                chart_width = 120
                chart_height = 36
                points = []
                labels = []
                for idx, val in enumerate(trend_data):
                    x = int((idx / (len(trend_data) - 1)) * (chart_width - 10)) + 5 if len(trend_data) > 1 else chart_width // 2
                    y = int(chart_height - 8 - ((val - min_val) / range_val) * (chart_height - 16))
                    points.append(f"{x},{y}")
                    # 점 아래 숫자 (매 2번째만 표시하여 겹침 방지)
                    if idx % 2 == 1 or len(trend_data) <= 4:
                        labels += f'<circle cx="{x}" cy="{y}" r="3" fill="{dept_color}"/>'
                        labels += f'<text x="{x}" y="{y + 12}" text-anchor="middle" font-size="8" fill="#6B7B8C">{val}</text>'
                    else:
                        labels += f'<circle cx="{x}" cy="{y}" r="2" fill="{dept_color}"/>'

                polyline = f'<polyline points="{" ".join(points)}" fill="none" stroke="{dept_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
                trend_chart = f'<svg width="100%" height="50" viewBox="0 0 {chart_width} {chart_height + 10}" preserveAspectRatio="xMidYMid meet" style="overflow:visible;">{polyline}{"".join(labels)}</svg>'
            else:
                trend_chart = '<div style="color:#6B7B8C;font-size:10px;">8주 트렌드</div>'

            active_style = "border-color:#C9A962;background:linear-gradient(135deg,rgba(201,169,98,0.15) 0%,rgba(201,169,98,0.05) 100%);" if is_active else ""

            # 순서: 전체/출석/출석률/목장
            st.markdown(f'''
                <div style="background:#F8F6F3;border:2px solid #E8E4DF;border-radius:12px;padding:12px;margin-top:8px;{active_style}">
                    <div style="display:flex;justify-content:space-between;gap:4px;margin-bottom:8px;">
                        <div style="text-align:center;flex:1;">
                            <div style="font-size:9px;color:#6B7B8C;margin-bottom:1px;">전체</div>
                            <div style="font-size:16px;font-weight:700;color:#2C3E50;">{members_count}</div>
                        </div>
                        <div style="text-align:center;flex:1;">
                            <div style="font-size:9px;color:#6B7B8C;margin-bottom:1px;">출석</div>
                            <div style="font-size:16px;font-weight:700;color:#4A9B7F;">{attendance_count}</div>
                        </div>
                        <div style="text-align:center;flex:1;">
                            <div style="font-size:9px;color:#6B7B8C;margin-bottom:1px;">출석률</div>
                            <div style="font-size:16px;font-weight:700;color:#C9A962;">{attendance_rate}%</div>
                        </div>
                        <div style="text-align:center;flex:1;">
                            <div style="font-size:9px;color:#6B7B8C;margin-bottom:1px;">{group_label}</div>
                            <div style="font-size:16px;font-weight:700;color:#2C3E50;">{groups_count}</div>
                        </div>
                    </div>
                    <div style="display:flex;align-items:center;justify-content:center;padding-top:6px;border-top:1px solid #E8E4DF;">
                        {trend_chart}
                    </div>
                </div>
            ''', unsafe_allow_html=True)

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
                # 목장 섹션 헤더
                group_label = "반" if selected_dept_name == "어린이부" else "목장"
                total_members = sum(g.get('members_count', 0) for g in groups)
                st.markdown(f'''<div class="groups-section">
                    <div class="groups-title">선택된 부서의 {group_label} ({selected_dept_name})</div>
                </div>''', unsafe_allow_html=True)

                # 전체 + 목장 버튼 그리드 (4열)
                cols_per_row = 4
                all_items = [{'group_id': None, 'name': '전체', 'members_count': total_members}] + groups

                for row_start in range(0, len(all_items), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for col_idx, item in enumerate(all_items[row_start:row_start + cols_per_row]):
                        with cols[col_idx]:
                            group_id = item.get('group_id')
                            group_name = item.get('name', '')
                            members_count = item.get('members_count', 0)
                            is_selected = (st.session_state.selected_group == group_id)

                            # 선택된 목장 스타일
                            btn_type = "primary" if is_selected else "secondary"
                            btn_label = f"{group_name} ({members_count})"

                            if st.button(btn_label, key=f"group_btn_{group_id}", use_container_width=True, type=btn_type):
                                st.session_state.selected_group = group_id
                                st.rerun()

                # ============================================================
                # 출석 현황 테이블 (편집 가능)
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

                    weeks = attendance_table_data.get('weeks', [])
                    week_dates = attendance_table_data.get('week_dates', [])
                    members_data = attendance_table_data.get('members', [])

                    if members_data:
                        title = f"{selected_group_name} 출석 현황" if selected_group_name else f"{selected_dept_name} 출석 현황"

                        # 출석률 계산
                        total_checks = len(members_data) * len(weeks)
                        present_checks = sum(sum(m.get('attendance', [])) for m in members_data)
                        rate = round((present_checks / total_checks) * 100, 1) if total_checks > 0 else 0

                        st.markdown(f'''<div class="attendance-table-section">
                            <div class="attendance-table-header">
                                <span class="attendance-table-title">📋 {title} (최근 8주)</span>
                                <span class="attendance-table-stat">평균 출석률: <strong>{rate}%</strong> ({present_checks}/{total_checks}) | 셀을 클릭하여 출석 수정</span>
                            </div>
                        ''', unsafe_allow_html=True)

                        # DataFrame 구성 (편집용)
                        df_data = []
                        for m in members_data:
                            row = {
                                'member_id': m['member_id'],  # hidden, for API call
                                '이름': m['name'],
                                '목장': m['group_name'],
                            }
                            # 각 주차별 출석 상태 (체크박스 형태)
                            for i, week_label in enumerate(weeks):
                                row[week_label] = bool(m['attendance'][i])
                            df_data.append(row)

                        df = pd.DataFrame(df_data)

                        # "전체" 선택 시 목장(1st) + 이름(2nd)으로 정렬
                        if not st.session_state.selected_group:
                            df = df.sort_values(by=['목장', '이름'], ascending=[True, True]).reset_index(drop=True)

                        # 원본 데이터 저장 (변경 감지용)
                        original_key = f"original_attendance_{st.session_state.selected_dept}_{st.session_state.selected_group}"
                        if original_key not in st.session_state:
                            st.session_state[original_key] = df.copy()

                        # 편집 가능한 테이블
                        column_config = {
                            'member_id': None,  # 숨김
                            '이름': st.column_config.TextColumn('이름', disabled=True, width='medium'),
                            '목장': st.column_config.TextColumn('목장', disabled=True, width='small'),
                        }
                        # 주차 컬럼은 체크박스로
                        for week_label in weeks:
                            column_config[week_label] = st.column_config.CheckboxColumn(
                                week_label,
                                width='small',
                                help=f'{week_label} 출석 여부 (클릭하여 변경)'
                            )

                        edited_df = st.data_editor(
                            df,
                            column_config=column_config,
                            hide_index=True,
                            use_container_width=True,
                            key=f"attendance_editor_{st.session_state.selected_dept}_{st.session_state.selected_group}"
                        )

                        # 변경 사항 수집 (즉시 저장하지 않음)
                        original_df = st.session_state[original_key]
                        pending_changes = []

                        for idx, row in edited_df.iterrows():
                            member_id = row['member_id']
                            for i, week_label in enumerate(weeks):
                                original_val = original_df.loc[idx, week_label] if idx < len(original_df) else None
                                new_val = row[week_label]

                                if original_val is not None and original_val != new_val:
                                    pending_changes.append({
                                        'member_id': member_id,
                                        'date': week_dates[i],
                                        'new_val': new_val
                                    })

                        st.markdown('</div>', unsafe_allow_html=True)

                        # 변경 사항이 있으면 저장 버튼 표시
                        if pending_changes:
                            if st.button(f"💾 {len(pending_changes)}건 저장", key="save_attendance_btn", type="primary", use_container_width=True):
                                success_count = 0
                                for change in pending_changes:
                                    try:
                                        result = api.toggle_attendance(change['member_id'], change['date'])
                                        if result.get('success'):
                                            success_count += 1
                                    except Exception as toggle_err:
                                        st.error(f"출석 변경 실패: {toggle_err}")

                                if success_count > 0:
                                    st.session_state[original_key] = edited_df.copy()
                                    fetch_dashboard_data_from_api.clear()
                                    st.toast(f"✅ {success_count}건 저장 완료", icon="✅")
                                    st.rerun()
                    else:
                        st.markdown(f'''<div class="attendance-table-section">
                            <div class="attendance-table-header">
                                <span class="attendance-table-title">📋 {selected_dept_name} 출석 현황</span>
                            </div>
                            <p style="color:#6B7B8C;font-size:14px;text-align:center;padding:40px;">출석 데이터가 없습니다</p>
                        </div>''', unsafe_allow_html=True)

                except Exception as e:
                    st.markdown(f'<div class="attendance-table-section"><p style="color:#6B7B8C;font-size:14px;text-align:center;padding:40px;">출석 데이터를 불러올 수 없습니다: {e}</p></div>', unsafe_allow_html=True)

            else:
                st.markdown(f'<div class="groups-section"><div class="groups-title">선택된 부서의 목장 ({selected_dept_name})</div><p style="color:#6B7B8C;font-size:14px;text-align:center;padding:20px;">목장 데이터가 없습니다</p></div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="groups-section"><p style="color:#6B7B8C;font-size:14px;text-align:center;padding:20px;">목장 데이터를 불러올 수 없습니다</p></div>', unsafe_allow_html=True)
else:
    st.markdown('<p style="color:#6B7B8C;font-size:14px;text-align:center;padding:40px;">부서 데이터가 없습니다</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 알림은 헤더 우측 상단으로 이동됨

