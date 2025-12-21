"""
공유 사이드바 모듈
모든 페이지에서 일관된 네비게이션을 제공합니다.
"""
import streamlit as st

APP_VERSION = "v3.22"

def render_shared_sidebar(current_page: str = None):
    """
    모든 페이지에서 공유되는 사이드바를 렌더링합니다.

    Args:
        current_page: 현재 페이지 식별자 (예: "dashboard", "attendance", "members", etc.)
    """
    with st.sidebar:
        # 로고 섹션
        st.markdown('''
        <div style="padding:1.5rem 0.75rem;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:1.5rem;">
            <div style="width:48px;height:48px;background:linear-gradient(135deg,#C9A962 0%,#D4B87A 100%);border-radius:14px;display:flex;align-items:center;justify-content:center;margin-bottom:16px;box-shadow:0 4px 16px rgba(201,169,98,0.3);font-size:24px;">⛪</div>
            <div style="font-family:Playfair Display,serif;font-size:22px;font-weight:600;color:white;">성도기록부</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.5);margin-top:4px;letter-spacing:1px;">SAINT RECORD SYSTEM</div>
        </div>
        ''', unsafe_allow_html=True)

        # 메인 섹션 라벨
        st.markdown('<div style="padding:0 0.5rem;"><div style="font-size:11px;font-weight:600;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;">메인</div></div>', unsafe_allow_html=True)

        # 대시보드
        if current_page == "dashboard":
            st.markdown('<div style="display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:12px;background:rgba(201,169,98,0.15);color:white;margin:0 0.5rem 4px;position:relative;"><div style="position:absolute;left:0;top:0;bottom:0;width:3px;background:#C9A962;border-radius:0 2px 2px 0;"></div><span style="font-size:18px;">🏠</span><span style="font-size:14px;font-weight:500;">대시보드</span></div>', unsafe_allow_html=True)
        else:
            st.page_link("app.py", label="🏠 대시보드")

        # 출석 입력
        if current_page == "attendance":
            st.markdown('<div style="display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:12px;background:rgba(201,169,98,0.15);color:white;margin:0 0.5rem 4px;position:relative;"><div style="position:absolute;left:0;top:0;bottom:0;width:3px;background:#C9A962;border-radius:0 2px 2px 0;"></div><span style="font-size:18px;">📋</span><span style="font-size:14px;font-weight:500;">출석 입력</span></div>', unsafe_allow_html=True)
        else:
            st.page_link("pages/1_📋_출석입력.py", label="📋 출석 입력")

        # 관리 섹션 라벨
        st.markdown('<div style="padding:0 0.5rem;margin-top:20px;"><div style="font-size:11px;font-weight:600;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;">관리</div></div>', unsafe_allow_html=True)

        # 성도 관리
        if current_page == "members":
            st.markdown('<div style="display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:12px;background:rgba(201,169,98,0.15);color:white;margin:0 0.5rem 4px;position:relative;"><div style="position:absolute;left:0;top:0;bottom:0;width:3px;background:#C9A962;border-radius:0 2px 2px 0;"></div><span style="font-size:18px;">👤</span><span style="font-size:14px;font-weight:500;">성도 관리</span></div>', unsafe_allow_html=True)
        else:
            st.page_link("pages/2_👤_성도관리.py", label="👤 성도 관리")

        # 가정 관리 (서브메뉴)
        if current_page == "family":
            st.markdown('<div style="display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:12px;background:rgba(201,169,98,0.15);color:white;margin:0 0.5rem 4px;position:relative;margin-left:1rem;"><div style="position:absolute;left:0;top:0;bottom:0;width:3px;background:#C9A962;border-radius:0 2px 2px 0;"></div><span style="font-size:18px;">👨‍👩‍👧</span><span style="font-size:14px;font-weight:500;">가정 관리</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="nav-sub-container">', unsafe_allow_html=True)
            st.page_link("pages/3_👨‍👩‍👧_가정관리.py", label="👨‍👩‍👧 가정 관리")
            st.markdown('</div>', unsafe_allow_html=True)

        # 조회 섹션 라벨
        st.markdown('<div style="padding:0 0.5rem;margin-top:20px;"><div style="font-size:11px;font-weight:600;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;">조회</div></div>', unsafe_allow_html=True)

        # 검색
        if current_page == "search":
            st.markdown('<div style="display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:12px;background:rgba(201,169,98,0.15);color:white;margin:0 0.5rem 4px;position:relative;"><div style="position:absolute;left:0;top:0;bottom:0;width:3px;background:#C9A962;border-radius:0 2px 2px 0;"></div><span style="font-size:18px;">🔍</span><span style="font-size:14px;font-weight:500;">검색</span></div>', unsafe_allow_html=True)
        else:
            st.page_link("pages/4_🔍_검색.py", label="🔍 검색")

        # 분석 섹션 라벨
        st.markdown('<div style="padding:0 0.5rem;margin-top:20px;"><div style="font-size:11px;font-weight:600;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;">분석</div></div>', unsafe_allow_html=True)

        # 통계
        if current_page == "stats":
            st.markdown('<div style="display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:12px;background:rgba(201,169,98,0.15);color:white;margin:0 0.5rem 4px;position:relative;"><div style="position:absolute;left:0;top:0;bottom:0;width:3px;background:#C9A962;border-radius:0 2px 2px 0;"></div><span style="font-size:18px;">📊</span><span style="font-size:14px;font-weight:500;">통계 / 보고서</span></div>', unsafe_allow_html=True)
        else:
            st.page_link("pages/5_📊_통계.py", label="📊 통계 / 보고서")

        # 설정
        if current_page == "settings":
            st.markdown('<div style="display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:12px;background:rgba(201,169,98,0.15);color:white;margin:0 0.5rem 4px;position:relative;"><div style="position:absolute;left:0;top:0;bottom:0;width:3px;background:#C9A962;border-radius:0 2px 2px 0;"></div><span style="font-size:18px;">⚙️</span><span style="font-size:14px;font-weight:500;">설정</span></div>', unsafe_allow_html=True)
        else:
            st.page_link("pages/6_⚙️_설정.py", label="⚙️ 설정")

        # 푸터
        st.markdown('''
        <div style="margin-top:auto;padding:1.5rem 1rem;border-top:1px solid rgba(255,255,255,0.1);">
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,#8B7355 0%,#C9A962 100%);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;color:white;">교</div>
                <div>
                    <div style="font-size:14px;font-weight:500;color:white;">교적담당자</div>
                    <div style="font-size:12px;color:rgba(255,255,255,0.5);">관리자</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # 버전 표시
        st.markdown(f'<div style="text-align:center;padding:8px;font-size:11px;color:rgba(255,255,255,0.4);">{APP_VERSION}</div>', unsafe_allow_html=True)
