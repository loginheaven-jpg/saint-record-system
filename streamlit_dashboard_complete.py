# 성도기록부 대시보드 - 완전한 Streamlit 구현 코드
# 파일명: app.py
# 이 파일을 그대로 복사하여 사용하세요.

import streamlit as st

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
# 2. CSS 스타일 정의
# ============================================================
def load_css():
    st.markdown("""
    <style>
    /* ========== Google Fonts ========== */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
    
    /* ========== CSS 변수 ========== */
    :root {
        --color-bg: #F8F6F3;
        --color-surface: #FFFFFF;
        --color-primary: #2C3E50;
        --color-secondary: #8B7355;
        --color-accent: #C9A962;
        --color-accent-light: #F5EFE0;
        --color-text: #2C3E50;
        --color-text-light: #6B7B8C;
        --color-success: #4A9B7F;
        --color-warning: #E8985E;
        --color-border: #E8E4DF;
    }
    
    /* ========== 전역 스타일 ========== */
    .stApp {
        background-color: #F8F6F3 !important;
    }
    
    /* Streamlit 기본 요소 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 메인 컨테이너 패딩 */
    .main .block-container {
        padding-top: 2rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }
    
    /* ========== 사이드바 스타일 ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2C3E50 0%, #1a2a3a 100%) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        padding-top: 0 !important;
    }
    
    /* 사이드바 내부 요소 */
    [data-testid="stSidebar"] .stMarkdown {
        color: rgba(255, 255, 255, 0.65);
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.1);
        margin: 1rem 0;
    }
    
    /* ========== 버튼 스타일 오버라이드 ========== */
    .stButton > button {
        background-color: #F8F6F3 !important;
        color: #6B7B8C !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #F5EFE0 !important;
        color: #2C3E50 !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #FFFFFF !important;
        color: #2C3E50 !important;
        box-shadow: 0 2px 8px rgba(44, 62, 80, 0.08) !important;
    }
    
    /* ========== 탭 버튼 컨테이너 ========== */
    .tab-container {
        display: flex;
        background: #F8F6F3;
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        margin-bottom: 16px;
    }
    
    .tab-button {
        flex: 1;
        padding: 10px 16px;
        font-size: 13px;
        font-weight: 500;
        color: #6B7B8C;
        background: transparent;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    
    .tab-button:hover {
        color: #2C3E50;
        background: rgba(255, 255, 255, 0.5);
    }
    
    .tab-button.active {
        background: #FFFFFF;
        color: #2C3E50;
        box-shadow: 0 2px 8px rgba(44, 62, 80, 0.08);
    }
    
    /* ========== 스크롤바 스타일 ========== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #E8E4DF;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #8B7355;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ============================================================
# 3. 사이드바 렌더링
# ============================================================
def render_sidebar():
    with st.sidebar:
        # 로고 섹션
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
        # 메인 네비게이션
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
        # 대시보드 (활성)
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
        # 출석 입력
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
        # 관리 섹션
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
        # 성도 관리
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
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
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
        # 분석 섹션
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
        # 푸터
        st.markdown("""
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
        """, unsafe_allow_html=True)

render_sidebar()

# ============================================================
# 4. 통계 카드 컴포넌트
# ============================================================
def stat_card(icon, value, label, trend=None, trend_direction="up", icon_color="blue", highlight=False):
    """통계 카드 렌더링"""
    
    # 색상 설정
    icon_colors = {
        "blue": {"bg": "#E8F4FD", "text": "#3498db"},
        "green": {"bg": "#E8F5F0", "text": "#4A9B7F"},
        "gold": {"bg": "#FDF8E8", "text": "#C9A962"},
        "purple": {"bg": "#F3E8FD", "text": "#9b59b6"},
    }
    
    if highlight:
        card_style = """
            background: linear-gradient(135deg, #2C3E50 0%, #3d5a73 100%);
            color: white;
        """
        value_color = "white"
        label_color = "rgba(255, 255, 255, 0.7)"
        icon_bg = "rgba(255, 255, 255, 0.2)"
        trend_bg = "rgba(255, 255, 255, 0.2)"
        trend_color = "white"
        bar_opacity = "1"
    else:
        card_style = "background: #FFFFFF;"
        value_color = "#2C3E50"
        label_color = "#6B7B8C"
        icon_bg = icon_colors.get(icon_color, icon_colors["blue"])["bg"]
        trend_bg = "rgba(74, 155, 127, 0.12)" if trend_direction == "up" else "rgba(232, 152, 94, 0.12)"
        trend_color = "#4A9B7F" if trend_direction == "up" else "#E8985E"
        bar_opacity = "0"
    
    # 트렌드 HTML
    trend_html = ""
    if trend:
        arrow = "▲" if trend_direction == "up" else "▼"
        trend_html = f'''
        <div style="
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 20px;
            background: {trend_bg};
            color: {trend_color};
        ">
            <span>{arrow}</span>
            <span>{trend}</span>
        </div>
        '''
    
    st.markdown(f'''
    <div style="
        {card_style}
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
        position: relative;
        overflow: hidden;
        height: 100%;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #C9A962, #8B7355);
            opacity: {bar_opacity};
        "></div>
        
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
            <div style="
                width: 52px;
                height: 52px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: {icon_bg};
                font-size: 24px;
            ">{icon}</div>
            {trend_html}
        </div>
        
        <div style="
            font-family: 'Playfair Display', serif;
            font-size: 42px;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 8px;
            color: {value_color};
        ">{value}</div>
        
        <div style="
            font-size: 14px;
            font-weight: 500;
            color: {label_color};
        ">{label}</div>
    </div>
    ''', unsafe_allow_html=True)

# ============================================================
# 5. 출석 현황 리스트 아이템
# ============================================================
def list_item(icon, name, count, percent, icon_bg):
    """부서/목장 리스트 아이템 렌더링"""
    
    # 프로그레스 바 색상
    if percent >= 75:
        progress_gradient = "linear-gradient(90deg, #4A9B7F, #6BC9A8)"
    elif percent >= 65:
        progress_gradient = "linear-gradient(90deg, #C9A962, #D4B87A)"
    else:
        progress_gradient = "linear-gradient(90deg, #E8985E, #F2B07E)"
    
    st.markdown(f'''
    <div style="
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px;
        background: #F8F6F3;
        border-radius: 12px;
        margin-bottom: 12px;
    ">
        <div style="
            width: 42px;
            height: 42px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            background: {icon_bg};
        ">{icon}</div>
        
        <div style="flex: 1;">
            <div style="font-size: 14px; font-weight: 600; color: #2C3E50; margin-bottom: 3px;">{name}</div>
            <div style="font-size: 12px; color: #6B7B8C;">{count}</div>
        </div>
        
        <div style="width: 90px; text-align: right;">
            <div style="
                height: 6px;
                background: #E8E4DF;
                border-radius: 3px;
                overflow: hidden;
                margin-bottom: 6px;
            ">
                <div style="
                    width: {percent}%;
                    height: 100%;
                    background: {progress_gradient};
                    border-radius: 3px;
                "></div>
            </div>
            <div style="font-size: 13px; font-weight: 600; color: #2C3E50;">{percent}%</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# ============================================================
# 6. 메인 컨텐츠 렌더링
# ============================================================

# 헤더
col_title, col_date = st.columns([3, 1])

with col_title:
    st.markdown('''
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
    ''', unsafe_allow_html=True)

with col_date:
    st.markdown('''
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
            <span style="font-size: 14px; font-weight: 500; color: #2C3E50;">2025년 1월 5일 (일)</span>
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
    ''', unsafe_allow_html=True)

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# 통계 카드 그리드
stat_cols = st.columns(4)

with stat_cols[0]:
    stat_card("👥", "199", "전체 성도", trend="+2", trend_direction="up", icon_color="blue")

with stat_cols[1]:
    stat_card("✓", "148", "금주 출석", trend="+5", trend_direction="up", icon_color="green", highlight=True)

with stat_cols[2]:
    stat_card("📈", "74.4%", "출석률", trend="+2.3%", trend_direction="up", icon_color="green")

with stat_cols[3]:
    stat_card("➕", "3", "신규 등록", trend="-1", trend_direction="down", icon_color="gold")

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# 메인 컨텐츠 그리드
left_col, right_col = st.columns([1.5, 1])

# 왼쪽: 차트 카드
with left_col:
    st.markdown('''
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
    ''', unsafe_allow_html=True)
    
    # 차트 (실제 구현 시 plotly 사용)
    import plotly.graph_objects as go
    
    weeks = ['12/15', '12/22', '12/29', '1/5']
    attendance = [140, 155, 120, 165]
    total = [180, 180, 180, 180]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='출석 인원',
        x=weeks,
        y=attendance,
        marker_color='#C9A962',
        width=0.35
    ))
    
    fig.add_trace(go.Bar(
        name='전체 인원',
        x=weeks,
        y=total,
        marker_color='#E8E4DF',
        width=0.35
    ))
    
    fig.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=40),
        height=260,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(family="Noto Sans KR", size=12, color="#6B7B8C")
        ),
        xaxis=dict(
            tickfont=dict(family="Noto Sans KR", size=12, color="#6B7B8C"),
            showgrid=False
        ),
        yaxis=dict(
            tickfont=dict(family="Noto Sans KR", size=12, color="#6B7B8C"),
            showgrid=True,
            gridcolor='#E8E4DF'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)

# 오른쪽: 출석 현황 카드
with right_col:
    st.markdown('''
    <div style="
        background: #FFFFFF;
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2 style="
                font-size: 18px;
                font-weight: 600;
                color: #2C3E50;
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 0;
            ">
                <span style="color: #C9A962;">📋</span>
                출석 현황
            </h2>
        </div>
    ''', unsafe_allow_html=True)
    
    # 탭 상태 관리
    if 'attendance_tab' not in st.session_state:
        st.session_state.attendance_tab = 'dept'
    
    # 탭 버튼
    tab_col1, tab_col2 = st.columns(2)
    
    with tab_col1:
        if st.button("📊 부서별", key="btn_dept", use_container_width=True, 
                     type="primary" if st.session_state.attendance_tab == 'dept' else "secondary"):
            st.session_state.attendance_tab = 'dept'
            st.rerun()
    
    with tab_col2:
        if st.button("👥 목장별", key="btn_mokjang", use_container_width=True,
                     type="primary" if st.session_state.attendance_tab == 'mokjang' else "secondary"):
            st.session_state.attendance_tab = 'mokjang'
            st.rerun()
    
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # 탭 컨텐츠
    if st.session_state.attendance_tab == 'dept':
        # 부서별
        list_item("👨‍👩‍👧", "장년부", "85 / 108명", 79, "linear-gradient(135deg, #667eea 0%, #764ba2 100%)")
        list_item("🎓", "청년부", "27 / 36명", 75, "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)")
        list_item("🎒", "청소년부", "14 / 23명", 61, "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)")
        list_item("🧒", "어린이부", "22 / 32명", 69, "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)")
    else:
        # 목장별
        st.markdown('<div style="max-height: 280px; overflow-y: auto; padding-right: 8px;">', unsafe_allow_html=True)
        list_item("🇳🇵", "네팔 목장", "11 / 12명", 92, "#E8685C")
        list_item("🇷🇺", "러시아 목장", "9 / 11명", 82, "#5B8DEE")
        list_item("🇵🇭", "필리핀 목장", "10 / 13명", 77, "#FFD93D")
        list_item("🇹🇭", "태국 목장", "8 / 10명", 80, "#9B59B6")
        list_item("🇧🇯", "베냉 목장", "7 / 11명", 64, "#2ECC71")
        list_item("🇨🇩", "콩고 목장", "10 / 12명", 83, "#3498DB")
        list_item("🇨🇱", "칠레 목장", "8 / 10명", 80, "#E74C3C")
        list_item("🏔️", "철원 목장", "6 / 9명", 67, "#1ABC9C")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 알림 섹션
    st.markdown('''
    <div style="margin-top: 24px; padding-top: 20px; border-top: 1px solid #E8E4DF;">
        <h3 style="
            font-size: 15px;
            font-weight: 600;
            color: #2C3E50;
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0 0 14px 0;
        ">
            <span style="color: #C9A962;">🔔</span>
            알림
        </h3>
        
        <div style="
            display: flex;
            align-items: flex-start;
            gap: 14px;
            padding: 14px;
            background: linear-gradient(90deg, rgba(232, 152, 94, 0.08) 0%, transparent 100%);
            border-radius: 12px;
            border-left: 4px solid #E8985E;
            margin-bottom: 12px;
        ">
            <div style="
                width: 34px;
                height: 34px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(232, 152, 94, 0.15);
                font-size: 16px;
            ">⚠️</div>
            <div>
                <div style="font-size: 13px; font-weight: 600; color: #2C3E50; margin-bottom: 3px;">3주 연속 결석</div>
                <div style="font-size: 12px; color: #6B7B8C;">김OO, 박OO 외 3명</div>
            </div>
        </div>
        
        <div style="
            display: flex;
            align-items: flex-start;
            gap: 14px;
            padding: 14px;
            background: linear-gradient(90deg, rgba(201, 169, 98, 0.08) 0%, transparent 100%);
            border-radius: 12px;
            border-left: 4px solid #C9A962;
        ">
            <div style="
                width: 34px;
                height: 34px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(201, 169, 98, 0.15);
                font-size: 16px;
            ">🎂</div>
            <div>
                <div style="font-size: 13px; font-weight: 600; color: #2C3E50; margin-bottom: 3px;">이번 주 생일</div>
                <div style="font-size: 12px; color: #6B7B8C;">이OO (1/7), 최OO (1/9)</div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # 빠른 실행 버튼
    st.markdown('''
    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #E8E4DF;">
        <div style="
            font-size: 12px;
            font-weight: 600;
            color: #6B7B8C;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 14px;
        ">빠른 실행</div>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
                padding: 16px 12px;
                background: #F8F6F3;
                border-radius: 12px;
                cursor: pointer;
                border: 2px solid transparent;
                transition: all 0.3s ease;
            ">
                <span style="font-size: 22px;">📋</span>
                <span style="font-size: 12px; font-weight: 500; color: #2C3E50;">출석 입력</span>
            </div>
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
                padding: 16px 12px;
                background: #F8F6F3;
                border-radius: 12px;
                cursor: pointer;
            ">
                <span style="font-size: 22px;">➕</span>
                <span style="font-size: 12px; font-weight: 500; color: #2C3E50;">성도 등록</span>
            </div>
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
                padding: 16px 12px;
                background: #F8F6F3;
                border-radius: 12px;
                cursor: pointer;
            ">
                <span style="font-size: 22px;">🔍</span>
                <span style="font-size: 12px; font-weight: 500; color: #2C3E50;">성도 검색</span>
            </div>
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
                padding: 16px 12px;
                background: #F8F6F3;
                border-radius: 12px;
                cursor: pointer;
            ">
                <span style="font-size: 22px;">📄</span>
                <span style="font-size: 12px; font-weight: 500; color: #2C3E50;">보고서</span>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
