
import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go
from utils.sheets_api import SheetsAPI
import textwrap
from utils.ui import load_custom_css, render_stat_card, render_bar_chart, render_list_item

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
        st.error(f"DB Error: {str(e)}")

def get_dashboard_data():
    data = {
        "total_members": 0,
        "current_attend": 0,
        "last_week_attend": 0,
        "new_members": 0,
        "chart_dates": [],
        "chart_attend": [],
        "chart_total": []
    }
    
    if st.session_state.get('db_connected'):
        api = st.session_state.api
        try:
            # 1. 전체 성도
            df_members = api.get_members({'status': '재적'})
            data['total_members'] = len(df_members)
            
            # 2. 이번달 신규
            # (간단하게 구현: 가입일자 필터링은 스킵하거나 추후 구현)
            
            # 3. 출석 데이터 (최근 4주)
            today = pd.Timestamp.today()
            last_sunday = today - datetime.timedelta(days=today.weekday() + 1)
            
            # 금주(지난주 주일) 출석
            df_this = api.get_attendance(last_sunday.year, date=str(last_sunday.date()))
            if not df_this.empty:
                # attend_type 1=주일, 2=온라인 (enum 참조)
                data['current_attend'] = len(df_this[df_this['attend_type'].astype(str).isin(['1', '2'])])
            
            # 전주 출석 (트렌드 계산용)
            prev_sunday = last_sunday - datetime.timedelta(days=7)
            df_prev = api.get_attendance(prev_sunday.year, date=str(prev_sunday.date()))
            if not df_prev.empty:
                try:
                    data['last_week_attend'] = len(df_prev[df_prev['attend_type'].astype(str).isin(['1', '2'])])
                except KeyError:
                    pass

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
                    try:
                        cnt = len(df_d[df_d['attend_type'].astype(str).isin(['1', '2'])])
                    except KeyError:
                        pass
                
                dates.append(d.strftime('%m/%d'))
                attends.append(cnt)
                totals.append(data['total_members']) # 전체 인원은 현재 기준 근사치
            
            data['chart_dates'] = dates
            data['chart_attend'] = attends
            data['chart_total'] = totals
            
        except Exception as e:
            st.error(f"Data Load Error: {e}")
            
    return data

dashboard_data = get_dashboard_data()

# ============================================================
# 4. 사이드바 렌더링
# ============================================================
def render_sidebar():
    with st.sidebar:
        # 로고 섹션
        st.markdown(textwrap.dedent("""
        <div style="padding: 1.5rem 0.75rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 1.5rem;">
            <div style="
                width: 48px; 
                height: 48px; 
                background: linear-gradient(135deg, #C9A962 0%, #D4B87A 100%);
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 16px;
                box-shadow: 0 4px 16px rgba(201, 169, 98, 0.3);
                font-size: 24px;
            ">⛪</div>
            <div style="
                font-family: 'Playfair Display', serif;
                font-size: 22px;
                font-weight: 600;
                color: white;
            ">성도기록부</div>
            <div style="
                font-size: 11px;
                color: rgba(255, 255, 255, 0.5);
                margin-top: 4px;
                letter-spacing: 1px;
            ">SAINT RECORD SYSTEM</div>
        </div>
        """), unsafe_allow_html=True)
        
        # 메인 네비게이션
        st.markdown(textwrap.dedent("""
        <div style="padding: 0 0.5rem;">
            <div style="
                font-size: 11px;
                font-weight: 600;
                color: rgba(255, 255, 255, 0.35);
                text-transform: uppercase;
                letter-spacing: 1.5px;
                margin-bottom: 12px;
            ">메인</div>
        </div>
        """), unsafe_allow_html=True)
        
        # 대시보드 (활성)
        st.markdown(textwrap.dedent("""
        <div style="
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            border-radius: 12px;
            background: rgba(201, 169, 98, 0.15);
            color: white;
            margin: 0 0.5rem 4px;
            position: relative;
        ">
            <div style="
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 3px;
                background: #C9A962;
                border-radius: 0 2px 2px 0;
            "></div>
            <span style="font-size: 18px;">🏠</span>
            <span style="font-size: 14px; font-weight: 500;">대시보드</span>
        </div>
        """), unsafe_allow_html=True)
        
        # 출석 입력
        st.markdown(textwrap.dedent("""
        <div style="
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            border-radius: 12px;
            color: rgba(255, 255, 255, 0.65);
            margin: 0 0.5rem 4px;
            cursor: pointer;
        ">
            <span style="font-size: 18px;">📋</span>
            <span style="font-size: 14px; font-weight: 500;">출석 입력</span>
        </div>
        """), unsafe_allow_html=True)
        
        # 관리 섹션
        st.markdown(textwrap.dedent("""
        <div style="padding: 0 0.5rem; margin-top: 20px;">
            <div style="
                font-size: 11px;
                font-weight: 600;
                color: rgba(255, 255, 255, 0.35);
                text-transform: uppercase;
                letter-spacing: 1.5px;
                margin-bottom: 12px;
            ">관리</div>
        </div>
        """), unsafe_allow_html=True)
        
        # 성도 관리
        st.markdown(textwrap.dedent("""
        <div style="
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            border-radius: 12px;
            color: rgba(255, 255, 255, 0.65);
            margin: 0 0.5rem 4px;
        ">
            <span style="font-size: 18px;">👤</span>
            <span style="font-size: 14px; font-weight: 500;">성도 관리</span>
        </div>
        """), unsafe_allow_html=True)
        
        # 서브 메뉴
        sub_menus = [("👤", "성도"), ("🏠", "가정"), ("👥", "목장"), ("📊", "부서")]
        
        sub_menu_html = '<div style="margin-left: 20px; padding-left: 16px; border-left: 1px solid rgba(255, 255, 255, 0.1); margin: 0 0.5rem 8px 1.75rem;">'
        for icon, label in sub_menus:
            sub_menu_html += f'''
            <div style="
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 10px 14px;
                border-radius: 12px;
                color: rgba(255, 255, 255, 0.65);
                margin-bottom: 4px;
                font-size: 13px;
            ">
                <span style="font-size: 14px;">{icon}</span>
                <span style="font-weight: 500;">{label}</span>
            </div>
            '''
        sub_menu_html += '</div>'
        st.markdown(sub_menu_html, unsafe_allow_html=True)
        
        # 조회 섹션
        st.markdown(textwrap.dedent("""
        <div style="padding: 0 0.5rem; margin-top: 20px;">
            <div style="
                font-size: 11px;
                font-weight: 600;
                color: rgba(255, 255, 255, 0.35);
                text-transform: uppercase;
                letter-spacing: 1.5px;
                margin-bottom: 12px;
            ">조회</div>
        </div>
        """), unsafe_allow_html=True)
        
        st.markdown(textwrap.dedent("""
        <div style="
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            border-radius: 12px;
            color: rgba(255, 255, 255, 0.65);
            margin: 0 0.5rem 4px;
        ">
            <span style="font-size: 18px;">🔍</span>
            <span style="font-size: 14px; font-weight: 500;">검색</span>
        </div>
        """), unsafe_allow_html=True)
        
        # 분석 섹션
        st.markdown(textwrap.dedent("""
        <div style="padding: 0 0.5rem; margin-top: 20px;">
            <div style="
                font-size: 11px;
                font-weight: 600;
                color: rgba(255, 255, 255, 0.35);
                text-transform: uppercase;
                letter-spacing: 1.5px;
                margin-bottom: 12px;
            ">분석</div>
        </div>
        """), unsafe_allow_html=True)
        
        st.markdown(textwrap.dedent("""
        <div style="
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            border-radius: 12px;
            color: rgba(255, 255, 255, 0.65);
            margin: 0 0.5rem 4px;
        ">
            <span style="font-size: 18px;">📈</span>
            <span style="font-size: 14px; font-weight: 500;">통계 / 보고서</span>
        </div>
        """), unsafe_allow_html=True)
        
        st.markdown(textwrap.dedent("""
        <div style="
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            border-radius: 12px;
            color: rgba(255, 255, 255, 0.65);
            margin: 0 0.5rem 4px;
        ">
            <span style="font-size: 18px;">⚙️</span>
            <span style="font-size: 14px; font-weight: 500;">설정</span>
        </div>
        """), unsafe_allow_html=True)
        
        # 푸터
        st.markdown(textwrap.dedent("""
        <div style="
            margin-top: auto;
            padding: 1.5rem 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="
                    width: 40px;
                    height: 40px;
                    border-radius: 12px;
                    background: linear-gradient(135deg, #8B7355 0%, #C9A962 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 14px;
                    font-weight: 600;
                    color: white;
                ">교</div>
                <div>
                    <div style="font-size: 14px; font-weight: 500; color: white;">교적담당자</div>
                    <div style="font-size: 12px; color: rgba(255, 255, 255, 0.5);">관리자</div>
                </div>
            </div>
        </div>
        """), unsafe_allow_html=True)

render_sidebar()

# ============================================================
# 5. 메인 컨텐츠 렌더링
# ============================================================

# 헤더
col_title, col_date = st.columns([3, 1])

with col_title:
    st.markdown(textwrap.dedent('''
    <h1 style="
        font-family: 'Playfair Display', serif;
        font-size: 32px;
        font-weight: 600;
        color: #2C3E50;
        margin: 0 0 8px 0;
    ">대시보드</h1>
    <p style="
        font-size: 14px;
        color: #6B7B8C;
        margin: 0;
    ">예봄교회 성도 현황을 한눈에 확인하세요</p>
    '''), unsafe_allow_html=True)

with col_date:
    today_formatted = datetime.date.today().strftime("%Y년 %m월 %d일")
    st.markdown(textwrap.dedent(f'''
    <div style="display: flex; justify-content: flex-end; gap: 16px; padding-top: 8px;">
        <div style="
            background: #FFFFFF;
            padding: 12px 20px;
            border-radius: 12px;
            box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
            display: flex;
            align-items: center;
            gap: 10px;
        ">
            <span style="font-size: 16px; color: #C9A962;">📅</span>
            <span style="font-size: 14px; font-weight: 500; color: #2C3E50;">{today_formatted}</span>
        </div>
        <div style="
            width: 48px;
            height: 48px;
            background: #FFFFFF;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
            position: relative;
            cursor: pointer;
        ">
            <span style="font-size: 20px;">🔔</span>
            <div style="
                position: absolute;
                top: 10px;
                right: 10px;
                width: 10px;
                height: 10px;
                background: #E8985E;
                border-radius: 50%;
                border: 2px solid #FFFFFF;
            "></div>
        </div>
    </div>
    '''), unsafe_allow_html=True)

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# 통계 데이터 계산
val_total = 0
val_attend = 0
attend_rate = 0.0
diff = 0

if dashboard_data['total_members'] > 0:
    val_total = dashboard_data['total_members']
    val_attend = dashboard_data['current_attend']
    attend_rate = (val_attend / val_total) * 100
    diff = val_attend - dashboard_data['last_week_attend']

# 트렌드 값 포맷팅
trend_dir = "up" if diff >= 0 else "down"
trend_sign = "+" if diff >= 0 else ""
trend_str = f"{trend_sign}{diff}"

# 통계 카드 그리드
stat_cols = st.columns(4)

with stat_cols[0]:
    # stat_card(icon, value, label, trend, trend_direction, icon_color, highlight) -> local old
    # render_stat_card(icon_name, icon_color, value, label, trend_val, trend_dir, is_highlight) -> utils new
    html_0 = render_stat_card("👥", "blue", str(val_total), "전체 성도", "+2", "up", False)
    st.markdown(html_0, unsafe_allow_html=True)

with stat_cols[1]:
    html_1 = render_stat_card("✓", "green", str(val_attend), "금주 출석", trend_str, trend_dir, True)
    st.markdown(html_1, unsafe_allow_html=True)

with stat_cols[2]:
    html_2 = render_stat_card("📈", "green", f"{attend_rate:.1f}%", "출석률", "+2.3%", "up", False)
    st.markdown(html_2, unsafe_allow_html=True)

with stat_cols[3]:
    html_3 = render_stat_card("➕", "gold", "3", "신규 등록", "-1", "down", False)
    st.markdown(html_3, unsafe_allow_html=True)

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# 메인 컨텐츠 그리드
left_col, right_col = st.columns([1.5, 1])

# 왼쪽: 차트 카드
with left_col:
    st.markdown(textwrap.dedent('''
    <div style="
        background: #FFFFFF;
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
        height: 100%;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
            <h2 style="
                font-size: 18px;
                font-weight: 600;
                color: #2C3E50;
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 0;
            ">
                <span style="color: #C9A962;">📊</span>
                최근 4주 출석 현황
            </h2>
            <span style="font-size: 13px; color: #8B7355; font-weight: 500; cursor: pointer;">자세히 보기 ›</span>
        </div>
    '''), unsafe_allow_html=True)
    
    # 차트 (Plotly 사용)
    weeks = dashboard_data.get('chart_dates', ['12/15', '12/22', '12/29', '1/5'])
    attendance_data = dashboard_data.get('chart_attend', [0, 0, 0, 0])
    total_data = dashboard_data.get('chart_total', [0, 0, 0, 0])
    
    if not weeks: 
        weeks = ['-', '-', '-', '-']
        attendance_data = [0,0,0,0]
        total_data = [0,0,0,0]

    fig = go.Figure()
    
    # 배경 bar (전체 인원)
    fig.add_trace(go.Bar(
        x=weeks,
        y=total_data,
        name='전체',
        marker_color='#F5EFE0',
        marker_func=None,
        hoverinfo='none'
    ))
    
    # 출석 bar
    fig.add_trace(go.Bar(
        x=weeks,
        y=attendance_data,
        name='출석',
        marker_color='#C9A962',
        width=0.4
    ))

    fig.update_layout(
        barmode='overlay',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=220,
        showlegend=False,
        barcornerradius=4, # Plotly 5.23+
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            tickfont=dict(size=12, color='#6B7B8C')
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
    
    st.markdown("</div>", unsafe_allow_html=True)

# 오른쪽: 부서별 현황
with right_col:
    st.markdown(textwrap.dedent('''
    <div style="
        background: #FFFFFF;
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
        height: 100%;
        min-height: 380px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
            <h2 style="
                font-size: 18px;
                font-weight: 600;
                color: #2C3E50;
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 0;
            ">
                <span style="color: #4A9B7F;">👥</span>
                부서별 출석률
            </h2>
            <span style="font-size: 13px; color: #8B7355; font-weight: 500; cursor: pointer;">전체보기 ›</span>
        </div>
    '''), unsafe_allow_html=True)
    
    # 리스트 아이템
    # render_list_item(icon, name, count, percent, icon_bg)
    html_list = ""
    html_list += render_list_item("👨‍💼", "장년부", "85/92명", 92, "#E8F4FD")
    html_list += render_list_item("🧑‍🎓", "청년부", "42/55명", 76, "#E8F5F0")
    html_list += render_list_item("🧒", "주일학교", "28/35명", 80, "#FDF8E8")
    html_list += render_list_item("👶", "영유아부", "12/20명", 60, "#F3E8FD")
    
    st.markdown(html_list, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

