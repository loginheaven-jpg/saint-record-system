import streamlit as st
import pandas as pd
import datetime
from utils.ui import load_custom_css, card_metric
from utils.sheets_api import SheetsAPI

st.set_page_config(
    page_title="성도기록부",
    page_icon="⛪",
    layout="wide"
)

# Load Custom Styles
load_custom_css()

# Initialize Session State
if 'api' not in st.session_state:
    # Initialize API cautiously
    try:
        st.session_state.api = SheetsAPI()
        st.session_state.db_connected = True
    except Exception as e:
        st.session_state.db_connected = False
        st.session_state.db_error = str(e)
        st.error(f"Debug Error: {str(e)}") # Directly show error for debugging

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style="padding: 1rem 0; text-align: center;">
            <div style="
                width: 60px; height: 60px; 
                background: linear-gradient(135deg, #C9A962 0%, #D4B87A 100%);
                border-radius: 14px; margin: 0 auto 16px;
                display: flex; align-items: center; justify-content: center;
                box-shadow: 0 4px 16px rgba(201, 169, 98, 0.3);
            ">
                <span style="font-size: 30px;">⛪</span>
            </div>
            <h2 style="color: white !important; font-size: 1.2rem; margin: 0;">예봄교회</h2>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">성도기록부 시스템 v1.0</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

st.title("대시보드")
st.markdown(f'<p style="color: #6B7B8C; margin-bottom: 2rem;">{datetime.date.today().strftime("%Y년 %m월 %d일")} 현황 보고</p>', unsafe_allow_html=True)

if not st.session_state.db_connected:
    st.error("데이터베이스에 연결할 수 없습니다.")
    st.warning("Google Cloud Service Account 설정이 필요합니다. `.streamlit/secrets.toml` 또는 `credentials/credentials.json`을 확인해주세요.")
    st.info("현재는 데모 모드로 UI만 표시됩니다.")
    
    # Mock Data for Demo
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        card_metric("전체 성도", "199", 2)
    with col2:
        card_metric("금주 출석", "148", -5, "highlight")
    with col3:
        card_metric("출석률", "74.4%")
    with col4:
        card_metric("신규 등록", "2")
        
    st.markdown("### 부서별 현황")
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
        <div class="card">
            <h4>장년부</h4>
            <div style="background: #eee; height: 8px; border-radius: 4px; overflow: hidden; margin-top: 8px;">
                <div style="width: 80%; height: 100%; background: linear-gradient(90deg, #4A9B7F, #6BC9A8);"></div>
            </div>
            <p style="text-align: right; font-size: 0.8rem; margin-top: 4px;">80%</p>
        </div>
        <div class="card">
            <h4>청년부</h4>
            <div style="background: #eee; height: 8px; border-radius: 4px; overflow: hidden; margin-top: 8px;">
                <div style="width: 70%; height: 100%; background: linear-gradient(90deg, #C9A962, #D4B87A);"></div>
            </div>
            <p style="text-align: right; font-size: 0.8rem; margin-top: 4px;">70%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Real Data
    api = st.session_state.api
    
    # 1. Stats
    try:
        members = api.get_members({'status': '재적'})
        total_members = len(members)
        
        # Calculate Attendance (Last Sunday)
        today = datetime.date.today()
        last_sunday = today - datetime.timedelta(days=today.weekday() + 1)
        attendance = api.get_attendance(last_sunday.year, date=str(last_sunday))
        
        present_count = 0
        if not attendance.empty:
            present_val = attendance['attend_type'].astype(str)
            present_count = len(attendance[present_val.isin(['1', 'O', '2'])])
        
        attend_rate = (present_count / total_members * 100) if total_members > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            card_metric("전체 성도", f"{total_members}명")
        with col2:
            card_metric("금주 출석", f"{present_count}명", color="highlight")
        with col3:
            card_metric("출석률", f"{attend_rate:.1f}%")
        with col4:
            # TODO: Get new members count
            card_metric("신규 등록", "-")
            
        # 2. Charts
        st.markdown("### 📈 주간 출석 추이")
        # Placeholder for chart
        st.info("데이터가 충분히 쌓이면 차트가 표시됩니다.")

    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
