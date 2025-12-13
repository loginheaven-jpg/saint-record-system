
import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go
import time
from utils.sheets_api import SheetsAPI
from utils.ui import (
    load_custom_css, render_stat_card, render_dept_item,
    render_alert_item, render_chart_legend
)

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
def fetch_dashboard_data_from_api():
    """API에서 대시보드 데이터 조회 (캐시됨)"""
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
        "last_sunday": ""
    }

    try:
        api = SheetsAPI()

        # 1. 전체 성도
        df_members = api.get_members({'status': '재적'})
        data['total_members'] = len(df_members)

        # 2. 이번달 신규 등록
        data['new_members'] = api.get_new_members_this_month()

        # 3. 출석 데이터 (최근 4주)
        today = pd.Timestamp.today()
        last_sunday = today - datetime.timedelta(days=today.weekday() + 1)
        last_sunday_str = str(last_sunday.date())
        data['last_sunday'] = last_sunday_str

        # 금주 출석
        df_this = api.get_attendance(last_sunday.year, date=last_sunday_str)
        if not df_this.empty:
            data['current_attend'] = len(df_this[df_this['attend_type'].astype(str).isin(['1', '2'])])

        # 전주 출석
        prev_sunday = last_sunday - datetime.timedelta(days=7)
        df_prev = api.get_attendance(prev_sunday.year, date=str(prev_sunday.date()))
        if not df_prev.empty:
            data['last_week_attend'] = len(df_prev[df_prev['attend_type'].astype(str).isin(['1', '2'])])

        # 차트 데이터 (4주)
        dates = []
        attends = []
        totals = []
        for i in range(3, -1, -1):
            d = last_sunday - datetime.timedelta(days=7*i)
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

    except Exception as e:
        print(f"Data Load Error: {e}")

    return data

def get_dashboard_data(force_refresh=False):
    """대시보드 데이터 조회 (24시간 캐싱)"""
    if force_refresh:
        # 캐시 강제 삭제
        fetch_dashboard_data_from_api.clear()
        st.session_state['dashboard_cache_time'] = time.time()

    # 캐시 시간이 없으면 초기화
    if 'dashboard_cache_time' not in st.session_state:
        st.session_state['dashboard_cache_time'] = time.time()

    return fetch_dashboard_data_from_api()

# 강제 새로고침 처리
force_refresh = st.session_state.get('force_refresh', False)
if force_refresh:
    st.session_state['force_refresh'] = False

dashboard_data = get_dashboard_data(force_refresh=force_refresh)

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

        # 분석 섹션 라벨
        st.markdown('<div style="padding:0 0.5rem;margin-top:20px;"><div style="font-size:11px;font-weight:600;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;">분석</div></div>', unsafe_allow_html=True)

        # 통계 페이지
        st.page_link("pages/5_📊_통계.py", label="📊 출석 통계")

        # 푸터
        st.markdown('<div style="margin-top:auto;padding:1.5rem 1rem;border-top:1px solid rgba(255,255,255,0.1);"><div style="display:flex;align-items:center;gap:12px;"><div style="width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,#8B7355 0%,#C9A962 100%);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;color:white;">교</div><div><div style="font-size:14px;font-weight:500;color:white;">교적담당자</div><div style="font-size:12px;color:rgba(255,255,255,0.5);">관리자</div></div></div></div>', unsafe_allow_html=True)

render_sidebar()

# ============================================================
# 5. 메인 컨텐츠 렌더링
# ============================================================

# 헤더
col_title, col_date, col_refresh = st.columns([2.5, 1, 0.5])

with col_title:
    st.markdown('<h1 style="font-family:Playfair Display,serif;font-size:32px;font-weight:600;color:#2C3E50;margin:0 0 8px 0;">대시보드</h1><p style="font-size:14px;color:#6B7B8C;margin:0;">예봄교회 성도 현황을 한눈에 확인하세요</p>', unsafe_allow_html=True)

with col_date:
    today_formatted = datetime.date.today().strftime("%Y년 %m월 %d일")
    calendar_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;color:#C9A962;"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/></svg>'
    bell_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;color:#6B7B8C;"><path d="M18 8A6 6 0 106 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>'
    st.markdown(f'<div style="display:flex;justify-content:flex-end;gap:12px;padding-top:8px;"><div style="background:#FFFFFF;padding:12px 20px;border-radius:12px;box-shadow:0 2px 20px rgba(44,62,80,0.06);display:flex;align-items:center;gap:10px;">{calendar_svg}<span style="font-size:14px;font-weight:500;color:#2C3E50;">{today_formatted}</span></div><div style="width:48px;height:48px;background:#FFFFFF;border-radius:12px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 20px rgba(44,62,80,0.06);position:relative;cursor:pointer;">{bell_svg}<div style="position:absolute;top:10px;right:10px;width:10px;height:10px;background:#E8985E;border-radius:50%;border:2px solid #FFFFFF;"></div></div></div>', unsafe_allow_html=True)

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

# 메인 컨텐츠 그리드
left_col, right_col = st.columns([1.5, 1])

# 왼쪽: 차트 카드
with left_col:
    # HTML 참조: .card-title svg { width: 20px; height: 20px; color: var(--color-accent); }
    bar_chart_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;color:#C9A962;"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>'
    chevron_svg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>'
    st.markdown(f'<div style="background:#FFFFFF;border-radius:24px;padding:28px;box-shadow:0 2px 20px rgba(44,62,80,0.06);height:100%;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;"><h2 style="font-size:18px;font-weight:600;color:#2C3E50;display:flex;align-items:center;gap:10px;margin:0;">{bar_chart_svg}최근 4주 출석 현황</h2></div>', unsafe_allow_html=True)
    
    # 차트 (Plotly 사용)
    weeks = dashboard_data.get('chart_dates', ['12/15', '12/22', '12/29', '1/5'])
    attendance_data = dashboard_data.get('chart_attend', [0, 0, 0, 0])
    total_data = dashboard_data.get('chart_total', [0, 0, 0, 0])
    
    if not weeks: 
        weeks = ['-', '-', '-', '-']
        attendance_data = [0,0,0,0]
        total_data = [0,0,0,0]

    fig = go.Figure()

    # 출석 bar (왼쪽, 골드색)
    fig.add_trace(go.Bar(
        x=weeks,
        y=attendance_data,
        name='출석 인원',
        marker_color='#C9A962',
        marker_line_width=0,
        width=0.35,
        text=attendance_data,
        textposition='outside',
        textfont=dict(size=11, color='#6B7B8C')
    ))

    # 전체 인원 bar (오른쪽, 회색)
    fig.add_trace(go.Bar(
        x=weeks,
        y=total_data,
        name='전체 인원',
        marker_color='#E8E4DF',
        marker_line_width=0,
        width=0.35
    ))

    # HTML 참조처럼 나란히 배치
    fig.update_layout(
        barmode='group',
        bargap=0.3,
        bargroupgap=0.1,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=30),
        height=260,
        showlegend=False,
        barcornerradius=6,
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

    # 차트 레전드
    st.markdown(render_chart_legend(), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# 오른쪽: 출석 현황 (탭 + 알림 + 빠른 실행)
with right_col:
    # HTML 참조: .card-title svg { width: 20px; height: 20px; color: var(--color-accent); } where accent=#C9A962
    st.markdown('''<div style="background:#FFFFFF;border-radius:24px;padding:28px;box-shadow:0 2px 20px rgba(44,62,80,0.06);"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;"><h2 style="font-size:18px;font-weight:600;color:#2C3E50;display:flex;align-items:center;gap:10px;margin:0;"><svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;color:#C9A962;"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>출석 현황</h2></div>''', unsafe_allow_html=True)

    # 탭 (Streamlit 네이티브 탭 사용)
    tab_dept, tab_mokjang = st.tabs(["부서별", "목장별"])

    with tab_dept:
        # 부서별 출석 현황 (실제 DB 데이터)
        dept_data = dashboard_data.get('dept_attendance', [])
        if dept_data:
            for dept in dept_data:
                st.markdown(render_dept_item(
                    dept['emoji'],
                    dept['css_class'],
                    dept['name'],
                    dept['present'],
                    dept['total']
                ), unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#6B7B8C;font-size:14px;text-align:center;padding:20px;">데이터가 없습니다</p>', unsafe_allow_html=True)

    with tab_mokjang:
        # 목장별 출석 현황 (실제 DB 데이터)
        mokjang_data = dashboard_data.get('mokjang_attendance', [])
        if mokjang_data:
            for mokjang in mokjang_data:
                st.markdown(render_dept_item(
                    mokjang['emoji'],
                    mokjang['css_class'],
                    mokjang['name'],
                    mokjang['present'],
                    mokjang['total']
                ), unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#6B7B8C;font-size:14px;text-align:center;padding:20px;">데이터가 없습니다</p>', unsafe_allow_html=True)

    # 알림 섹션 - HTML 참조: .card-title { font-size: 18px; } 하지만 알림 제목은 style="font-size: 15px;"
    st.markdown('''<div style="margin-top:24px;padding-top:20px;border-top:1px solid #E8E4DF;"><div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;"><svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;color:#C9A962;"><path d="M18 8A6 6 0 106 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg><span style="font-size:15px;font-weight:600;color:#2C3E50;">알림</span></div></div>''', unsafe_allow_html=True)

    # 3주 연속 결석 알림 (실제 DB 데이터)
    absent_list = dashboard_data.get('absent_3weeks', [])
    if absent_list:
        names = ', '.join([m['name'] for m in absent_list[:3]])
        extra = f" 외 {len(absent_list)-3}명" if len(absent_list) > 3 else ""
        st.markdown(render_alert_item("warning", "warning", "3주 연속 결석", names + extra), unsafe_allow_html=True)
    else:
        st.markdown(render_alert_item("info", "check", "출석 양호", "3주 연속 결석자가 없습니다"), unsafe_allow_html=True)

    # 이번 주 생일 알림 (실제 DB 데이터)
    birthdays = dashboard_data.get('birthdays', [])
    if birthdays:
        bday_text = ', '.join([f"{b['name']} ({b['birth_date']})" for b in birthdays[:3]])
        extra = f" 외 {len(birthdays)-3}명" if len(birthdays) > 3 else ""
        st.markdown(render_alert_item("info", "gift", "🎂 이번 주 생일", bday_text + extra), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

