import streamlit as st
import pandas as pd
from utils.ui import load_custom_css
from utils.sheets_api import SheetsAPI, clear_sheets_cache
from utils.sidebar import render_shared_sidebar

st.set_page_config(page_title="설정", page_icon="⚙️", layout="wide")
load_custom_css()
render_shared_sidebar("settings")

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

/* 설정 카드 */
.settings-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px rgba(44, 62, 80, 0.08);
}
.settings-card-title {
    font-size: 16px;
    font-weight: 600;
    color: #2C3E50;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.settings-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #E8E4DF;
}
.settings-item:last-child {
    border-bottom: none;
}
.settings-label {
    font-size: 14px;
    color: #6B7B8C;
}
.settings-value {
    font-size: 14px;
    font-weight: 600;
    color: #2C3E50;
}
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.status-badge.connected { background: #E8F5E9; color: #2E7D32; }
.status-badge.disconnected { background: #FFEBEE; color: #C62828; }

/* 통계 그리드 */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-top: 16px;
}
.stat-box {
    background: #F8F6F3;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.stat-box-value {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 700;
    color: #2C3E50;
}
.stat-box-label {
    font-size: 12px;
    color: #6B7B8C;
    margin-top: 4px;
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

# 데이터 로드 함수
@st.cache_data(ttl=300)
def load_data_stats():
    if db_connected:
        members = api.get_members()
        departments = api.get_departments()
        groups = api.get_groups()
        return {
            'members': len(members) if not members.empty else 0,
            'departments': len(departments) if not departments.empty else 0,
            'groups': len(groups) if not groups.empty else 0,
            'active': len(members[members['status'] == '재적']) if not members.empty and 'status' in members.columns else 0
        }
    return {'members': 0, 'departments': 0, 'groups': 0, 'active': 0}

# 페이지 헤더
st.markdown("""
<div class="page-header">
    <div>
        <h1>⚙️ 설정</h1>
        <p>시스템 설정 및 정보를 관리합니다</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 앱 버전 (app.py와 동일)
APP_VERSION = "v3.25"

# 시스템 정보 섹션
st.markdown("""
<div class="settings-card">
    <div class="settings-card-title">📱 시스템 정보</div>
    <div class="settings-item">
        <span class="settings-label">앱 버전</span>
        <span class="settings-value">{version}</span>
    </div>
    <div class="settings-item">
        <span class="settings-label">데이터베이스 연결</span>
        <span class="status-badge {status_class}">{status_text}</span>
    </div>
</div>
""".format(
    version=APP_VERSION,
    status_class="connected" if db_connected else "disconnected",
    status_text="연결됨" if db_connected else "연결 실패"
), unsafe_allow_html=True)

# 데이터 통계 섹션
if db_connected:
    with st.spinner("데이터를 불러오는 중..."):
        stats = load_data_stats()

    st.markdown(f"""
    <div class="settings-card">
        <div class="settings-card-title">📊 데이터 현황</div>
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-box-value">{stats['members']}</div>
                <div class="stat-box-label">전체 성도</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-value">{stats['active']}</div>
                <div class="stat-box-label">재적 성도</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-value">{stats['departments']}</div>
                <div class="stat-box-label">부서</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-value">{stats['groups']}</div>
                <div class="stat-box-label">목장</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 캐시 관리 섹션
st.markdown("""
<div class="settings-card">
    <div class="settings-card-title">🔄 캐시 관리</div>
    <p style="font-size:13px; color:#6B7B8C; margin-bottom:16px;">
        데이터가 최신 상태로 표시되지 않으면 캐시를 초기화하세요.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("🗑️ 캐시 초기화", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.cache_resource.clear()
        clear_sheets_cache()
        st.success("캐시가 초기화되었습니다.")
        st.rerun()

with col2:
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 도움말 섹션
st.markdown("""
<div class="settings-card">
    <div class="settings-card-title">❓ 도움말</div>
    <div class="settings-item">
        <span class="settings-label">문의</span>
        <span class="settings-value">교회 관리자에게 연락하세요</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 버전 히스토리
with st.expander("📋 버전 히스토리"):
    st.markdown("""
    **v3.25** - 날짜 박스 popover 방식
    - 날짜 박스 클릭 시 날짜 선택 팝오버 표시
    - 목업과 일치하는 날짜 박스 스타일

    **v3.24** - 헤더 레이아웃 간소화

    **v3.23** - 헤더 레이아웃 완전 수정
    - 제목 + 날짜박스 + 새로고침을 같은 행에 배치
    - 알림: 상단 우측에 floating 배치

    **v3.22** - 헤더 날짜 중복 제거
    - HTML 날짜 표시 제거 (Streamlit date_input만 사용)

    **v3.21** - 헤더 UI Option C 100% 일치
    - HTML 목업과 완전 동일한 스타일 적용
    - 알림: "3주 결석" + 컬러 숫자 (주황/노랑)
    - 날짜: 기준일 라벨 + 연.월.일 (요일) 형식
    - 새로고침: 아이콘만 표시 (40x40 골드 버튼)

    **v3.20** - 헤더 UI 개선 (Option C)
    - 2-tier 레이아웃: 알림 상단 우측, 제목/날짜 하단
    - 알림 표시: 점(dot) + 텍스트 (박스 제거)
    - 날짜 표시: 아이콘 + 라벨 + 값 통합 박스
    - 새로고침 버튼: 골드 그라데이션 스타일

    **v3.19** - 공유 사이드바 구현
    - 모든 페이지에서 네비게이션 유지
    - 페이지 이동 시 사이드바 깜빡임 제거
    - 빈 박스 문제 수정 (data-content 제거)

    **v3.18** - 헤더 정렬 개선
    - 상단 헤더 요소 세로 중앙 정렬 (flexbox)

    **v3.17** - 알림 배지 hover 툴팁 수정

    **v3.16** - 대시보드 UI 개선
    - 제목 스타일 통일 (font-size 16px)
    - 데이터 영역 좌측 강조 바 추가
    - 헤더 레이아웃 정렬 개선

    **v3.15** - UI 완성
    - 출석/결석 이원화 (온라인 개념 제거)
    - 성도관리 UI 개선
    - 가정관리/검색/설정 페이지 구현
    - 네비게이션 개선

    **v3.14** - 기본 메뉴 비활성화 + 버전 표시

    **v3.13** - 성도관리 테이블 스크롤 수정

    **v3.12** - 알림 배지 재구현

    **v3.11** - UI 개선 및 성도관리 기능 강화
    """)
