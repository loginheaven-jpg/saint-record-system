# 성도기록부 시스템 - UI 구현 명세서
> **Version**: 1.0  
> **Purpose**: Streamlit 앱에서 HTML 디자인을 정확히 재현하기 위한 상세 명세  
> **Reference**: dashboard_ui_v2.html

---

## 1. 디자인 시스템

### 1.1 색상 팔레트 (정확한 HEX 코드)

```python
# utils/theme.py

COLORS = {
    # 배경
    "bg": "#F8F6F3",              # 메인 배경 (아이보리)
    "surface": "#FFFFFF",          # 카드 배경 (흰색)
    
    # 주요 색상
    "primary": "#2C3E50",          # 네이비 (텍스트, 사이드바)
    "secondary": "#8B7355",        # 브라운 (보조)
    "accent": "#C9A962",           # 골드 (강조)
    "accent_light": "#F5EFE0",     # 연한 골드 (호버 배경)
    
    # 텍스트
    "text": "#2C3E50",             # 기본 텍스트
    "text_light": "#6B7B8C",       # 보조 텍스트
    
    # 상태 색상
    "success": "#4A9B7F",          # 녹색 (상승, 높음)
    "warning": "#E8985E",          # 주황 (경고, 하락)
    
    # 테두리
    "border": "#E8E4DF",           # 테두리, 구분선
    
    # 사이드바 그라데이션
    "sidebar_top": "#2C3E50",      # 사이드바 상단
    "sidebar_bottom": "#1a2a3a",   # 사이드바 하단
}

# 통계 카드 아이콘 배경색
STAT_ICON_COLORS = {
    "blue": {"bg": "#E8F4FD", "icon": "#3498db"},
    "green": {"bg": "#E8F5F0", "icon": "#4A9B7F"},
    "gold": {"bg": "#FDF8E8", "icon": "#C9A962"},
    "purple": {"bg": "#F3E8FD", "icon": "#9b59b6"},
}

# 부서 아이콘 그라데이션
DEPT_GRADIENTS = {
    "adults": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "youth": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    "teens": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
    "children": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
}

# 목장 아이콘 색상
MOKJANG_COLORS = {
    "nepal": "#E8685C",
    "russia": "#5B8DEE",
    "philippines": "#FFD93D",
    "thailand": "#9B59B6",
    "benin": "#2ECC71",
    "congo": "#3498DB",
    "chile": "#E74C3C",
    "cheorwon": "#1ABC9C",
}
```

### 1.2 타이포그래피

```python
# 폰트 설정
FONTS = {
    "primary": "'Noto Sans KR', sans-serif",      # 본문
    "display": "'Playfair Display', serif",        # 제목, 숫자
}

# 폰트 크기 (px)
FONT_SIZES = {
    "xs": "11px",      # 라벨, 캡션
    "sm": "12px",      # 보조 텍스트
    "base": "14px",    # 기본 텍스트
    "md": "15px",      # 카드 제목 (작은)
    "lg": "18px",      # 카드 제목
    "xl": "22px",      # 로고 텍스트
    "2xl": "32px",     # 페이지 제목
    "3xl": "42px",     # 통계 숫자
}

# 폰트 두께
FONT_WEIGHTS = {
    "light": 300,
    "normal": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700,
}
```

### 1.3 간격 및 크기

```python
# 간격 (px)
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "12px",
    "lg": "16px",
    "xl": "20px",
    "2xl": "24px",
    "3xl": "28px",
    "4xl": "32px",
    "5xl": "36px",
    "6xl": "40px",
}

# 모서리 둥글기
RADIUS = {
    "sm": "12px",      # 버튼, 입력, 작은 카드
    "md": "16px",      # 통계 카드
    "lg": "24px",      # 메인 카드
}

# 그림자
SHADOWS = {
    "soft": "0 2px 20px rgba(44, 62, 80, 0.06)",
    "medium": "0 8px 32px rgba(44, 62, 80, 0.08)",
    "glow": "0 0 40px rgba(201, 169, 98, 0.15)",
}

# 고정 크기
SIZES = {
    "sidebar_width": "280px",
    "stat_icon": "52px",
    "dept_icon": "42px",
    "avatar": "40px",
    "logo_icon": "48px",
    "notification_btn": "48px",
    "progress_bar_height": "6px",
}
```

---

## 2. 레이아웃 구조

### 2.1 전체 구조

```
┌──────────────────────────────────────────────────────────────────┐
│                          VIEWPORT                                │
├────────────┬─────────────────────────────────────────────────────┤
│            │                                                     │
│  SIDEBAR   │                  MAIN CONTENT                       │
│  280px     │                  flex: 1                            │
│  fixed     │                  margin-left: 280px                 │
│  height:   │                  padding: 32px 40px                 │
│  100vh     │                                                     │
│            │  ┌─────────────────────────────────────────────┐   │
│            │  │ HEADER                                      │   │
│            │  │ display: flex; justify-content: space-between│   │
│            │  └─────────────────────────────────────────────┘   │
│            │                                                     │
│            │  ┌─────────────────────────────────────────────┐   │
│            │  │ STATS GRID                                  │   │
│            │  │ grid-template-columns: repeat(4, 1fr)       │   │
│            │  │ gap: 24px                                   │   │
│            │  └─────────────────────────────────────────────┘   │
│            │                                                     │
│            │  ┌────────────────────────┬────────────────────┐   │
│            │  │ CHART CARD             │ RIGHT CARD         │   │
│            │  │ flex: 1                │ width: 400px       │   │
│            │  │                        │                    │   │
│            │  │                        │                    │   │
│            │  └────────────────────────┴────────────────────┘   │
│            │  gap: 28px                                         │
│            │                                                     │
└────────────┴─────────────────────────────────────────────────────┘
```

### 2.2 사이드바 구조

```
┌─────────────────────────────┐
│ LOGO SECTION                │
│ padding: 0 28px 32px        │
│ border-bottom: 1px solid    │
│   rgba(255,255,255,0.1)     │
│                             │
│ ┌─────┐                     │
│ │ICON │ 48x48, radius: 14px │
│ └─────┘ gold gradient       │
│ 성도기록부                   │ Playfair Display, 22px
│ SAINT RECORD SYSTEM         │ 12px, rgba(255,255,255,0.5)
├─────────────────────────────┤
│ NAV SECTION                 │
│ padding: 0 16px             │
│                             │
│ ┌─ LABEL ─────────────────┐ │ 11px, uppercase, letter-spacing: 1.5px
│ │ 메인                     │ │ rgba(255,255,255,0.35)
│ └─────────────────────────┘ │
│                             │
│ ┌─ NAV ITEM ──────────────┐ │
│ │▌ 🏠 대시보드              │ │ active: gold left border (3px)
│ └─────────────────────────┘ │ padding: 14px 16px
│                             │
│ ┌─ NAV ITEM ──────────────┐ │
│ │  📋 출석 입력            │ │ inactive: rgba(255,255,255,0.65)
│ └─────────────────────────┘ │
│                             │
│ ┌─ LABEL ─────────────────┐ │
│ │ 관리                     │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─ NAV ITEM ──────────────┐ │
│ │  👤 성도 관리            │ │ 상위 메뉴
│ └─────────────────────────┘ │
│   │                         │ SUB NAV: margin-left: 20px
│   ├─ 👤 성도                │ border-left: 1px solid
│   ├─ 🏠 가정                │   rgba(255,255,255,0.1)
│   ├─ 👥 목장                │ padding: 10px 14px
│   └─ 📊 부서                │ font-size: 13px
│                             │
├─────────────────────────────┤
│ FOOTER (margin-top: auto)   │
│ border-top: 1px solid       │
│                             │
│ ┌──────────────────────────┐│
│ │ [Avatar] 교적담당자       ││
│ │          관리자           ││
│ └──────────────────────────┘│
└─────────────────────────────┘
```

### 2.3 통계 카드 구조

```
┌──────────────────────────────────────────────────┐
│ STAT CARD                                        │
│ padding: 28px                                    │
│ border-radius: 16px                              │
│ background: #FFFFFF (또는 highlight 시 gradient) │
│                                                  │
│ ::before (상단 바)                               │
│   height: 4px                                    │
│   background: gold → brown gradient              │
│   opacity: 0 (hover 시 1)                        │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ HEADER (display: flex, space-between)      │  │
│ │                                            │  │
│ │ ┌────────┐                    ┌─────────┐ │  │
│ │ │  ICON  │ 52x52             │ TREND   │ │  │
│ │ │        │ radius: 14px      │ +2 ▲    │ │  │
│ │ └────────┘                    └─────────┘ │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ VALUE                                      │  │
│ │ 199                                        │  │ Playfair Display, 42px, bold
│ └────────────────────────────────────────────┘  │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ LABEL                                      │  │
│ │ 전체 성도                                   │  │ 14px, #6B7B8C
│ └────────────────────────────────────────────┘  │
│                                                  │
└──────────────────────────────────────────────────┘
```

### 2.4 탭 컴포넌트 구조

```
┌──────────────────────────────────────────────────┐
│ TABS CONTAINER                                   │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ TABS (display: flex)                       │  │
│ │ background: #F8F6F3                        │  │
│ │ border-radius: 12px                        │  │
│ │ padding: 4px                               │  │
│ │ gap: 4px                                   │  │
│ │                                            │  │
│ │ ┌─────────────────┐ ┌─────────────────┐   │  │
│ │ │ TAB (active)    │ │ TAB (inactive)  │   │  │
│ │ │ 📊 부서별       │ │ 👥 목장별       │   │  │
│ │ │                 │ │                 │   │  │
│ │ │ bg: #FFFFFF     │ │ bg: transparent │   │  │
│ │ │ shadow          │ │ color: #6B7B8C  │   │  │
│ │ │ color: #2C3E50  │ │                 │   │  │
│ │ └─────────────────┘ └─────────────────┘   │  │
│ │ flex: 1 each                               │  │
│ │ padding: 10px 16px                         │  │
│ │ border-radius: 8px                         │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ TAB CONTENT                                │  │
│ │ (display: none / block based on active)    │  │
│ │                                            │  │
│ │ animation: fadeIn 0.3s ease                │  │
│ │   from { opacity: 0; translateY(8px); }    │  │
│ │   to { opacity: 1; translateY(0); }        │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
└──────────────────────────────────────────────────┘
```

### 2.5 부서/목장 리스트 아이템

```
┌──────────────────────────────────────────────────┐
│ DEPT ITEM                                        │
│ display: flex                                    │
│ align-items: center                              │
│ gap: 14px                                        │
│ padding: 14px                                    │
│ background: #F8F6F3                              │
│ border-radius: 12px                              │
│ transition: all 0.3s ease                        │
│                                                  │
│ hover:                                           │
│   background: #F5EFE0                            │
│   transform: translateX(4px)                     │
│                                                  │
│ ┌────────┐ ┌──────────────────┐ ┌────────────┐ │
│ │  ICON  │ │ INFO             │ │ PROGRESS   │ │
│ │ 42x42  │ │                  │ │            │ │
│ │        │ │ 장년부           │ │ ████░░ 79% │ │
│ │ 👨‍👩‍👧   │ │ 85 / 108명      │ │            │ │
│ │        │ │                  │ │ width:90px │ │
│ └────────┘ └──────────────────┘ └────────────┘ │
│            flex: 1              text-align:right │
│                                                  │
└──────────────────────────────────────────────────┘

PROGRESS BAR:
┌──────────────────────────────────────────────────┐
│ height: 6px                                      │
│ background: #E8E4DF                              │
│ border-radius: 3px                               │
│                                                  │
│ FILL:                                            │
│ high (>=75%): #4A9B7F → #6BC9A8 gradient        │
│ medium (65-74%): #C9A962 → #D4B87A gradient     │
│ low (<65%): #E8985E → #F2B07E gradient          │
└──────────────────────────────────────────────────┘
```

---

## 3. Streamlit 구현 가이드

### 3.1 기본 설정

```python
# app.py

import streamlit as st

# 페이지 설정 (가장 먼저 호출)
st.set_page_config(
    page_title="성도기록부",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 주입
def load_css():
    st.markdown("""
    <style>
    /* Google Fonts 로드 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
    
    /* 전역 스타일 리셋 */
    .stApp {
        background-color: #F8F6F3;
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    /* Streamlit 기본 요소 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 메인 컨텐츠 패딩 조정 */
    .main .block-container {
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 100%;
    }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2C3E50 0%, #1a2a3a 100%);
        padding-top: 0;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }
    
    /* 사이드바 텍스트 색상 */
    [data-testid="stSidebar"] .stMarkdown {
        color: rgba(255, 255, 255, 0.65);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()
```

### 3.2 사이드바 구현

```python
# components/sidebar.py

import streamlit as st

def render_sidebar():
    with st.sidebar:
        # 로고 섹션
        st.markdown("""
        <div style="padding: 0 12px 24px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 24px;">
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
            ">
                <span style="font-size: 24px;">⛪</span>
            </div>
            <div style="
                font-family: 'Playfair Display', serif;
                font-size: 22px;
                font-weight: 600;
                color: white;
            ">성도기록부</div>
            <div style="
                font-size: 12px;
                color: rgba(255, 255, 255, 0.5);
                margin-top: 4px;
                letter-spacing: 1px;
            ">SAINT RECORD SYSTEM</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 네비게이션 라벨
        st.markdown("""
        <div style="
            font-size: 11px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.35);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            padding: 0 12px;
            margin-bottom: 12px;
        ">메인</div>
        """, unsafe_allow_html=True)
        
        # 네비게이션 아이템 (활성)
        st.markdown("""
        <div style="
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            border-radius: 12px;
            background: rgba(201, 169, 98, 0.15);
            color: white;
            margin-bottom: 4px;
            position: relative;
            cursor: pointer;
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
        
        # 네비게이션 아이템 (비활성)
        st.markdown("""
        <div style="
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            border-radius: 12px;
            color: rgba(255, 255, 255, 0.65);
            margin-bottom: 4px;
            cursor: pointer;
        ">
            <span style="font-size: 18px;">📋</span>
            <span style="font-size: 14px; font-weight: 500;">출석 입력</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 관리 섹션 라벨
        st.markdown("""
        <div style="
            font-size: 11px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.35);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            padding: 0 12px;
            margin: 20px 0 12px;
        ">관리</div>
        """, unsafe_allow_html=True)
        
        # 성도 관리 (상위)
        st.markdown("""
        <div style="
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            border-radius: 12px;
            color: rgba(255, 255, 255, 0.65);
            margin-bottom: 4px;
            cursor: pointer;
        ">
            <span style="font-size: 18px;">👤</span>
            <span style="font-size: 14px; font-weight: 500;">성도 관리</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 서브 메뉴
        sub_menus = [
            ("👤", "성도"),
            ("🏠", "가정"),
            ("👥", "목장"),
            ("📊", "부서"),
        ]
        
        st.markdown("""
        <div style="
            margin-left: 20px;
            padding-left: 16px;
            border-left: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 8px;
        ">
        """, unsafe_allow_html=True)
        
        for icon, label in sub_menus:
            st.markdown(f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 10px 14px;
                border-radius: 12px;
                color: rgba(255, 255, 255, 0.65);
                margin-bottom: 4px;
                cursor: pointer;
                font-size: 13px;
            ">
                <span style="font-size: 14px;">{icon}</span>
                <span style="font-weight: 500;">{label}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
```

### 3.3 통계 카드 컴포넌트

```python
# components/stat_card.py

import streamlit as st

def stat_card(
    icon: str,
    value: str,
    label: str,
    trend: str = None,
    trend_direction: str = "up",
    icon_color: str = "blue",
    highlight: bool = False
):
    """
    통계 카드 컴포넌트
    
    Args:
        icon: 이모지 또는 SVG 아이콘
        value: 표시할 값 (예: "199", "74.4%")
        label: 라벨 텍스트
        trend: 트렌드 텍스트 (예: "+2", "-1")
        trend_direction: "up" 또는 "down"
        icon_color: "blue", "green", "gold", "purple"
        highlight: True면 강조 카드 (네이비 배경)
    """
    
    # 색상 매핑
    icon_colors = {
        "blue": {"bg": "#E8F4FD", "icon": "#3498db"},
        "green": {"bg": "#E8F5F0", "icon": "#4A9B7F"},
        "gold": {"bg": "#FDF8E8", "icon": "#C9A962"},
        "purple": {"bg": "#F3E8FD", "icon": "#9b59b6"},
    }
    
    trend_colors = {
        "up": {"bg": "rgba(74, 155, 127, 0.12)", "text": "#4A9B7F"},
        "down": {"bg": "rgba(232, 152, 94, 0.12)", "text": "#E8985E"},
    }
    
    if highlight:
        card_bg = "linear-gradient(135deg, #2C3E50 0%, #3d5a73 100%)"
        text_color = "white"
        label_color = "rgba(255, 255, 255, 0.7)"
        icon_bg = "rgba(255, 255, 255, 0.2)"
        icon_text_color = "white"
        trend_bg = "rgba(255, 255, 255, 0.2)"
        trend_text_color = "white"
        bar_opacity = "1"
    else:
        card_bg = "#FFFFFF"
        text_color = "#2C3E50"
        label_color = "#6B7B8C"
        icon_bg = icon_colors.get(icon_color, icon_colors["blue"])["bg"]
        icon_text_color = icon_colors.get(icon_color, icon_colors["blue"])["icon"]
        trend_bg = trend_colors.get(trend_direction, trend_colors["up"])["bg"]
        trend_text_color = trend_colors.get(trend_direction, trend_colors["up"])["text"]
        bar_opacity = "0"
    
    trend_html = ""
    if trend:
        arrow = "▲" if trend_direction == "up" else "▼"
        trend_html = f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 20px;
            background: {trend_bg};
            color: {trend_text_color};
        ">
            <span>{arrow}</span>
            <span>{trend}</span>
        </div>
        """
    
    st.markdown(f"""
    <div style="
        background: {card_bg};
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
        position: relative;
        overflow: hidden;
        transition: all 0.4s ease;
    ">
        <!-- 상단 바 -->
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #C9A962, #8B7355);
            opacity: {bar_opacity};
        "></div>
        
        <!-- 헤더 -->
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
        ">
            <!-- 아이콘 -->
            <div style="
                width: 52px;
                height: 52px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: {icon_bg};
                font-size: 24px;
            ">
                <span style="color: {icon_text_color};">{icon}</span>
            </div>
            
            <!-- 트렌드 -->
            {trend_html}
        </div>
        
        <!-- 값 -->
        <div style="
            font-family: 'Playfair Display', serif;
            font-size: 42px;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 8px;
            color: {text_color};
        ">{value}</div>
        
        <!-- 라벨 -->
        <div style="
            font-size: 14px;
            font-weight: 500;
            color: {label_color};
        ">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_stats_grid(stats_data: list):
    """
    통계 카드 4열 그리드 렌더링
    
    Args:
        stats_data: [
            {"icon": "👥", "value": "199", "label": "전체 성도", "trend": "+2", ...},
            ...
        ]
    """
    cols = st.columns(4)
    
    for i, stat in enumerate(stats_data):
        with cols[i]:
            stat_card(**stat)
```

### 3.4 탭 컴포넌트 (부서별/목장별)

```python
# components/tabs.py

import streamlit as st

def render_attendance_tabs():
    """출석 현황 탭 (부서별/목장별)"""
    
    # 탭 선택 상태
    if 'attendance_tab' not in st.session_state:
        st.session_state.attendance_tab = 'dept'
    
    # 탭 버튼 렌더링
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "📊 부서별", 
            key="tab_dept",
            use_container_width=True,
            type="primary" if st.session_state.attendance_tab == 'dept' else "secondary"
        ):
            st.session_state.attendance_tab = 'dept'
            st.rerun()
    
    with col2:
        if st.button(
            "👥 목장별", 
            key="tab_mokjang",
            use_container_width=True,
            type="primary" if st.session_state.attendance_tab == 'mokjang' else "secondary"
        ):
            st.session_state.attendance_tab = 'mokjang'
            st.rerun()
    
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # 탭 컨텐츠
    if st.session_state.attendance_tab == 'dept':
        render_dept_list()
    else:
        render_mokjang_list()


def render_dept_list():
    """부서별 출석 리스트"""
    dept_data = [
        {"icon": "👨‍👩‍👧", "name": "장년부", "count": "85 / 108명", "percent": 79, "color": "adults"},
        {"icon": "🎓", "name": "청년부", "count": "27 / 36명", "percent": 75, "color": "youth"},
        {"icon": "🎒", "name": "청소년부", "count": "14 / 23명", "percent": 61, "color": "teens"},
        {"icon": "🧒", "name": "어린이부", "count": "22 / 32명", "percent": 69, "color": "children"},
    ]
    
    for dept in dept_data:
        render_list_item(dept)


def render_mokjang_list():
    """목장별 출석 리스트"""
    mokjang_data = [
        {"icon": "🇳🇵", "name": "네팔 목장", "count": "11 / 12명", "percent": 92, "color": "nepal"},
        {"icon": "🇷🇺", "name": "러시아 목장", "count": "9 / 11명", "percent": 82, "color": "russia"},
        {"icon": "🇵🇭", "name": "필리핀 목장", "count": "10 / 13명", "percent": 77, "color": "philippines"},
        {"icon": "🇹🇭", "name": "태국 목장", "count": "8 / 10명", "percent": 80, "color": "thailand"},
        {"icon": "🇧🇯", "name": "베냉 목장", "count": "7 / 11명", "percent": 64, "color": "benin"},
        {"icon": "🇨🇩", "name": "콩고 목장", "count": "10 / 12명", "percent": 83, "color": "congo"},
        {"icon": "🇨🇱", "name": "칠레 목장", "count": "8 / 10명", "percent": 80, "color": "chile"},
        {"icon": "🏔️", "name": "철원 목장", "count": "6 / 9명", "percent": 67, "color": "cheorwon"},
    ]
    
    # 스크롤 컨테이너
    st.markdown("""
    <div style="max-height: 280px; overflow-y: auto; padding-right: 8px;">
    """, unsafe_allow_html=True)
    
    for mokjang in mokjang_data:
        render_list_item(mokjang)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_list_item(item: dict):
    """리스트 아이템 렌더링"""
    
    # 프로그레스 바 색상
    if item["percent"] >= 75:
        progress_color = "linear-gradient(90deg, #4A9B7F, #6BC9A8)"
    elif item["percent"] >= 65:
        progress_color = "linear-gradient(90deg, #C9A962, #D4B87A)"
    else:
        progress_color = "linear-gradient(90deg, #E8985E, #F2B07E)"
    
    # 아이콘 배경색
    icon_gradients = {
        "adults": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "youth": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "teens": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "children": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "nepal": "#E8685C",
        "russia": "#5B8DEE",
        "philippines": "#FFD93D",
        "thailand": "#9B59B6",
        "benin": "#2ECC71",
        "congo": "#3498DB",
        "chile": "#E74C3C",
        "cheorwon": "#1ABC9C",
    }
    
    icon_bg = icon_gradients.get(item["color"], "#667eea")
    if not icon_bg.startswith("linear"):
        icon_bg = f"background-color: {icon_bg}"
    else:
        icon_bg = f"background: {icon_bg}"
    
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px;
        background: #F8F6F3;
        border-radius: 12px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    ">
        <!-- 아이콘 -->
        <div style="
            width: 42px;
            height: 42px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            {icon_bg};
        ">{item["icon"]}</div>
        
        <!-- 정보 -->
        <div style="flex: 1;">
            <div style="
                font-size: 14px;
                font-weight: 600;
                color: #2C3E50;
                margin-bottom: 3px;
            ">{item["name"]}</div>
            <div style="
                font-size: 12px;
                color: #6B7B8C;
            ">{item["count"]}</div>
        </div>
        
        <!-- 프로그레스 -->
        <div style="width: 90px; text-align: right;">
            <div style="
                height: 6px;
                background: #E8E4DF;
                border-radius: 3px;
                overflow: hidden;
                margin-bottom: 6px;
            ">
                <div style="
                    width: {item["percent"]}%;
                    height: 100%;
                    {progress_color.replace('linear-gradient', 'background: linear-gradient')};
                    border-radius: 3px;
                "></div>
            </div>
            <div style="
                font-size: 13px;
                font-weight: 600;
                color: #2C3E50;
            ">{item["percent"]}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
```

### 3.5 메인 대시보드 조립

```python
# app.py (메인)

import streamlit as st
from components.sidebar import render_sidebar
from components.stat_card import stat_card, render_stats_grid
from components.tabs import render_attendance_tabs

# 페이지 설정
st.set_page_config(
    page_title="성도기록부",
    page_icon="⛪",
    layout="wide"
)

# CSS 로드
load_css()

# 사이드바
render_sidebar()

# 헤더
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <h1 style="
        font-family: 'Playfair Display', serif;
        font-size: 32px;
        font-weight: 600;
        color: #2C3E50;
        margin-bottom: 8px;
    ">대시보드</h1>
    <p style="
        font-size: 14px;
        color: #6B7B8C;
    ">예봄교회 성도 현황을 한눈에 확인하세요</p>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="display: flex; justify-content: flex-end; gap: 16px;">
        <div style="
            background: #FFFFFF;
            padding: 12px 20px;
            border-radius: 12px;
            box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
            display: flex;
            align-items: center;
            gap: 10px;
        ">
            <span style="font-size: 18px;">📅</span>
            <span style="font-size: 14px; font-weight: 500; color: #2C3E50;">
                2025년 1월 5일 (일)
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# 통계 카드 그리드
stats_data = [
    {
        "icon": "👥",
        "value": "199",
        "label": "전체 성도",
        "trend": "+2",
        "trend_direction": "up",
        "icon_color": "blue",
        "highlight": False
    },
    {
        "icon": "✓",
        "value": "148",
        "label": "금주 출석",
        "trend": "+5",
        "trend_direction": "up",
        "icon_color": "green",
        "highlight": True  # 강조 카드
    },
    {
        "icon": "📈",
        "value": "74.4%",
        "label": "출석률",
        "trend": "+2.3%",
        "trend_direction": "up",
        "icon_color": "green",
        "highlight": False
    },
    {
        "icon": "➕",
        "value": "3",
        "label": "신규 등록",
        "trend": "-1",
        "trend_direction": "down",
        "icon_color": "gold",
        "highlight": False
    },
]

cols = st.columns(4)
for i, stat in enumerate(stats_data):
    with cols[i]:
        stat_card(**stat)

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# 메인 컨텐츠 그리드
left_col, right_col = st.columns([1.5, 1])

with left_col:
    # 차트 카드
    st.markdown("""
    <div style="
        background: #FFFFFF;
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
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
            <span style="
                font-size: 13px;
                color: #8B7355;
                font-weight: 500;
                cursor: pointer;
            ">자세히 보기 ›</span>
        </div>
        
        <!-- 차트 영역 (실제로는 plotly 또는 altair 사용) -->
        <div style="height: 280px; display: flex; align-items: flex-end; justify-content: space-around; padding: 0 20px;">
            <!-- 여기에 실제 차트 구현 -->
        </div>
    </div>
    """, unsafe_allow_html=True)

with right_col:
    # 출석 현황 카드
    st.markdown("""
    <div style="
        background: #FFFFFF;
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 2px 20px rgba(44, 62, 80, 0.06);
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
                <span style="color: #C9A962;">📋</span>
                출석 현황
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # 탭 컴포넌트
    render_attendance_tabs()
    
    st.markdown("</div>", unsafe_allow_html=True)
```

---

## 4. 아이콘 참조

### 4.1 메뉴 아이콘 (이모지 또는 SVG)

| 메뉴 | 이모지 | 대체 텍스트 |
|------|--------|-------------|
| 대시보드 | 🏠 | 홈 |
| 출석 입력 | 📋 | 체크리스트 |
| 성도 관리 | 👤 | 사람 |
| 성도 | 👤 | 사람 |
| 가정 | 🏠 | 집 |
| 목장 | 👥 | 그룹 |
| 부서 | 📊 | 차트 |
| 검색 | 🔍 | 돋보기 |
| 통계 | 📈 | 그래프 |
| 설정 | ⚙️ | 톱니바퀴 |

### 4.2 부서 아이콘

| 부서 | 이모지 | 배경 그라데이션 |
|------|--------|-----------------|
| 장년부 | 👨‍👩‍👧 | #667eea → #764ba2 |
| 청년부 | 🎓 | #f093fb → #f5576c |
| 청소년부 | 🎒 | #4facfe → #00f2fe |
| 어린이부 | 🧒 | #43e97b → #38f9d7 |

### 4.3 목장 아이콘 (국기)

| 목장 | 이모지 | 배경색 |
|------|--------|--------|
| 네팔 | 🇳🇵 | #E8685C |
| 러시아 | 🇷🇺 | #5B8DEE |
| 필리핀 | 🇵🇭 | #FFD93D |
| 태국 | 🇹🇭 | #9B59B6 |
| 베냉 | 🇧🇯 | #2ECC71 |
| 콩고 | 🇨🇩 | #3498DB |
| 칠레 | 🇨🇱 | #E74C3C |
| 철원 | 🏔️ | #1ABC9C |

---

## 5. 체크리스트

### 5.1 구현 전 확인

- [ ] Google Fonts 로드 (Noto Sans KR, Playfair Display)
- [ ] 색상 변수 정의 (theme.py 또는 CSS variables)
- [ ] Streamlit 기본 스타일 오버라이드

### 5.2 컴포넌트별 체크

- [ ] 사이드바 구현
  - [ ] 로고 섹션 (아이콘 + 텍스트)
  - [ ] 네비게이션 라벨
  - [ ] 네비게이션 아이템 (활성/비활성)
  - [ ] 서브 메뉴 (들여쓰기 + 좌측선)
  - [ ] 푸터 (사용자 정보)

- [ ] 헤더 구현
  - [ ] 제목 + 부제목
  - [ ] 날짜 표시
  - [ ] 알림 버튼

- [ ] 통계 카드 구현
  - [ ] 4열 그리드
  - [ ] 아이콘 (색상별 배경)
  - [ ] 트렌드 배지 (상승/하락)
  - [ ] 강조 카드 (네이비 배경)

- [ ] 차트 카드 구현
  - [ ] 카드 헤더
  - [ ] 막대 차트 (plotly/altair)
  - [ ] 범례

- [ ] 출석 현황 카드 구현
  - [ ] 탭 버튼 (부서별/목장별)
  - [ ] 부서 리스트
  - [ ] 목장 리스트 (스크롤)
  - [ ] 프로그레스 바

- [ ] 알림 섹션
  - [ ] 경고 아이템 (주황)
  - [ ] 정보 아이템 (골드)

- [ ] 빠른 실행 버튼
  - [ ] 2x2 그리드
  - [ ] 호버 효과

### 5.3 스타일 체크

- [ ] 폰트 적용 확인
- [ ] 색상 일치 확인
- [ ] 간격 (padding, margin) 확인
- [ ] 모서리 둥글기 확인
- [ ] 그림자 효과 확인
- [ ] 호버 효과 확인
- [ ] 애니메이션 확인

---

## 6. 문제 해결 가이드

### 6.1 Streamlit에서 커스텀 CSS가 적용되지 않을 때

```python
# unsafe_allow_html=True 반드시 사용
st.markdown("""
<style>
    .custom-class { ... }
</style>
""", unsafe_allow_html=True)
```

### 6.2 사이드바 배경색이 적용되지 않을 때

```css
/* 정확한 선택자 사용 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2C3E50 0%, #1a2a3a 100%) !important;
}

[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
}
```

### 6.3 그리드 레이아웃이 깨질 때

```python
# Streamlit columns 사용
col1, col2, col3, col4 = st.columns(4)

# 또는 HTML 그리드
st.markdown("""
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px;">
    ...
</div>
""", unsafe_allow_html=True)
```

### 6.4 폰트가 적용되지 않을 때

```python
# @import 대신 link 태그 사용
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)
```

---

*Document Version: 1.0*  
*Last Updated: 2025-01-09*  
*Reference: dashboard_ui_v2.html*
