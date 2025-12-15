import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.sheets_api import SheetsAPI
from utils.ui import load_custom_css

st.set_page_config(page_title="통계", page_icon="📊", layout="wide")
load_custom_css()

# 부서 색상 매핑 (대시보드와 동일)
DEPT_COLORS = {
    '장년부': '#6B5B47',
    '청년부': '#556B82',
    '청소년부': '#6B8E23',
    '어린이부': '#D2691E',
}

DEPT_ORDER = ['장년부', '청년부', '청소년부', '어린이부']

# API 초기화
if 'api' not in st.session_state:
    try:
        st.session_state.api = SheetsAPI()
    except Exception as e:
        st.error(f"API 연결 오류: {e}")
        st.stop()

api = st.session_state.api


@st.cache_data(ttl=3600, show_spinner=False)
def get_yearly_statistics():
    """연간 주간 출석 데이터 (부서별)"""
    members = api.get_members({'status': '출석'})
    departments = api.get_departments()
    groups = api.get_groups()

    if members.empty or departments.empty:
        return {'weekly_data': [], 'members': members, 'departments': departments, 'groups': groups}

    # 올해 1월 첫 일요일부터 현재까지
    today = datetime.today()
    current_year = today.year

    # 올해 1월 1일의 첫 일요일 찾기
    jan_first = datetime(current_year, 1, 1)
    days_until_sunday = (6 - jan_first.weekday()) % 7
    first_sunday = jan_first + timedelta(days=days_until_sunday)
    if first_sunday.year < current_year:
        first_sunday += timedelta(days=7)

    # 현재 주의 일요일
    days_since_sunday = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(days=days_since_sunday)

    # 부서별 성도 수
    dept_member_counts = {}
    for dept_name in DEPT_ORDER:
        dept_row = departments[departments['dept_name'] == dept_name]
        if not dept_row.empty:
            dept_id = str(dept_row.iloc[0]['dept_id'])
            dept_members = members[members['dept_id'].astype(str) == dept_id]
            dept_member_counts[dept_name] = len(dept_members)
        else:
            dept_member_counts[dept_name] = 0

    total_members = sum(dept_member_counts.values())

    # 주간 데이터 수집
    weekly_data = []
    current_sunday = first_sunday

    while current_sunday <= last_sunday:
        sunday_str = current_sunday.strftime('%Y-%m-%d')
        year = current_sunday.year
        attendance = api.get_attendance(year, date=sunday_str)

        week_data = {
            'date': sunday_str,
            'display_date': current_sunday.strftime('%m/%d'),
            'week_no': current_sunday.isocalendar()[1],
        }

        # 부서별 출석 집계
        total_present = 0
        for dept_name in DEPT_ORDER:
            dept_row = departments[departments['dept_name'] == dept_name]
            if not dept_row.empty:
                dept_id = str(dept_row.iloc[0]['dept_id'])
                dept_members = members[members['dept_id'].astype(str) == dept_id]
                member_ids = dept_members['member_id'].tolist()

                if not attendance.empty and member_ids:
                    dept_attendance = attendance[attendance['member_id'].isin(member_ids)]
                    present = len(dept_attendance[dept_attendance['attend_type'].astype(str).isin(['1', '2'])])
                else:
                    present = 0
            else:
                present = 0

            week_data[dept_name] = present
            total_present += present

        week_data['합계'] = total_present
        week_data['출석률'] = round((total_present / total_members) * 100, 1) if total_members > 0 else 0

        weekly_data.append(week_data)
        current_sunday += timedelta(days=7)

    return {
        'weekly_data': weekly_data,
        'members': members,
        'departments': departments,
        'groups': groups,
        'dept_member_counts': dept_member_counts,
        'total_members': total_members
    }


# ============================================================
# 헤더 + 대시보드 복귀 버튼
# ============================================================
col_back, col_title = st.columns([1, 11])
with col_back:
    if st.button("← 대시보드", key="back_to_dashboard", use_container_width=True):
        st.switch_page("app.py")

with col_title:
    st.markdown("""
    <h1 style="font-family: 'Playfair Display', serif; font-size: 32px; font-weight: 600; color: #2C3E50; margin: 0;">
        📊 출석 통계
    </h1>
    <p style="font-size: 14px; color: #6B7B8C; margin: 4px 0 16px 0;">
        연간 출석 현황을 다양한 관점에서 분석합니다
    </p>
    """, unsafe_allow_html=True)

# 데이터 로드
with st.spinner("데이터 로딩 중..."):
    data = get_yearly_statistics()

weekly_data = data.get('weekly_data', [])
members = data.get('members', pd.DataFrame())
departments = data.get('departments', pd.DataFrame())
groups = data.get('groups', pd.DataFrame())
dept_member_counts = data.get('dept_member_counts', {})
total_members = data.get('total_members', 0)


# ============================================================
# 탭 구성 (주간 추이 | 부서/목장 통계)
# ============================================================
tab1, tab2 = st.tabs(["📈 주간 추이", "🏢 부서/목장 통계"])


# ============================================================
# 탭 1: 연간 주간 추이 (스택 바 차트)
# ============================================================
with tab1:
    if not weekly_data:
        st.warning("출석 데이터가 없습니다.")
    else:
        st.subheader(f"📅 {datetime.now().year}년 주간 출석 추이")

        # 스택 바 차트 (부서별 색상)
        fig = go.Figure()

        for dept_name in DEPT_ORDER:
            y_values = [w.get(dept_name, 0) for w in weekly_data]
            fig.add_trace(go.Bar(
                name=dept_name,
                x=[w['display_date'] for w in weekly_data],
                y=y_values,
                marker_color=DEPT_COLORS.get(dept_name, '#C9A962'),
                hovertemplate=f'{dept_name}: %{{y}}명<extra></extra>'
            ))

        # 출석률 라인 (보조 Y축)
        rates = [w.get('출석률', 0) for w in weekly_data]
        fig.add_trace(go.Scatter(
            name='출석률',
            x=[w['display_date'] for w in weekly_data],
            y=rates,
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#2C3E50', width=2, dash='dot'),
            marker=dict(size=4),
            hovertemplate='출석률: %{y}%<extra></extra>'
        ))

        fig.update_layout(
            barmode='stack',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=60, t=30, b=50),
            height=400,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            xaxis=dict(
                showgrid=False,
                tickfont=dict(size=10, color='#6B7B8C'),
                tickangle=-45 if len(weekly_data) > 20 else 0
            ),
            yaxis=dict(
                title='출석 인원',
                showgrid=True,
                gridcolor='#F0F0F0',
                tickfont=dict(size=11, color='#6B7B8C')
            ),
            yaxis2=dict(
                title='출석률 (%)',
                overlaying='y',
                side='right',
                range=[0, 100],
                tickfont=dict(size=11, color='#6B7B8C'),
                showgrid=False
            )
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 주간 출석 상세 테이블
        st.subheader("📋 주간 출석 상세")

        # 테이블 데이터 구성
        table_data = []
        for w in weekly_data:
            row = {
                '날짜': w['display_date'],
                '장년부': w.get('장년부', 0),
                '청년부': w.get('청년부', 0),
                '청소년부': w.get('청소년부', 0),
                '어린이부': w.get('어린이부', 0),
                '합계': w.get('합계', 0),
                '출석률': f"{w.get('출석률', 0)}%"
            }
            table_data.append(row)

        # 역순 정렬 (최신 먼저)
        table_data.reverse()

        weekly_df = pd.DataFrame(table_data)

        # 스타일링된 테이블 표시
        st.dataframe(
            weekly_df,
            use_container_width=True,
            hide_index=True,
            height=min(400, len(weekly_df) * 35 + 38)
        )

        # CSV 다운로드
        csv = weekly_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name=f"출석통계_주간_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


# ============================================================
# 탭 2: 부서/목장 계층형 통계
# ============================================================
with tab2:
    st.subheader("🏢 부서/목장별 출석 현황")

    if departments.empty:
        st.warning("부서 데이터가 없습니다.")
    else:
        # 최근 주 데이터
        last_week = weekly_data[-1] if weekly_data else None
        last_week_date = last_week['date'] if last_week else None

        # 부서별 통계 카드 + 목장 펼침
        for dept_name in DEPT_ORDER:
            dept_row = departments[departments['dept_name'] == dept_name]
            if dept_row.empty:
                continue

            dept_id = str(dept_row.iloc[0]['dept_id'])
            dept_members = members[members['dept_id'].astype(str) == dept_id]
            dept_total = len(dept_members)

            if dept_total == 0:
                continue

            # 부서 출석률 계산
            dept_present = last_week.get(dept_name, 0) if last_week else 0
            dept_rate = round((dept_present / dept_total) * 100, 1) if dept_total > 0 else 0

            # 부서 색상
            dept_color = DEPT_COLORS.get(dept_name, '#C9A962')

            # Expander로 부서 표시
            with st.expander(f"**{dept_name}** ({dept_total}명, 출석률 {dept_rate}%)", expanded=False):
                # 부서 요약 카드
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("등록 성도", f"{dept_total}명")
                with col2:
                    st.metric("금주 출석", f"{dept_present}명")
                with col3:
                    st.metric("출석률", f"{dept_rate}%")

                # 해당 부서의 목장 목록
                dept_groups = groups[groups['dept_id'].astype(str) == dept_id]

                if dept_groups.empty:
                    st.info("등록된 목장이 없습니다.")
                else:
                    st.markdown("##### 목장별 현황")

                    # 목장별 데이터 수집
                    group_stats = []
                    for _, group in dept_groups.iterrows():
                        group_id = str(group.get('group_id', ''))
                        group_name = group.get('group_name', '')

                        if not group_id:
                            continue

                        group_members = dept_members[dept_members['group_id'].astype(str) == group_id]
                        group_total = len(group_members)

                        if group_total == 0:
                            continue

                        # 금주 출석
                        group_present = 0
                        if last_week_date:
                            year = int(last_week_date[:4])
                            attendance = api.get_attendance(year, date=last_week_date)
                            if not attendance.empty:
                                member_ids = group_members['member_id'].tolist()
                                group_attendance = attendance[attendance['member_id'].isin(member_ids)]
                                group_present = len(group_attendance[
                                    group_attendance['attend_type'].astype(str).isin(['1', '2'])
                                ])

                        group_rate = round((group_present / group_total) * 100, 1) if group_total > 0 else 0

                        group_stats.append({
                            '목장': group_name,
                            '인원': group_total,
                            '출석': group_present,
                            '출석률': group_rate
                        })

                    if group_stats:
                        # 출석률 내림차순 정렬
                        group_stats.sort(key=lambda x: x['출석률'], reverse=True)

                        # 목장별 진행바 표시
                        for g in group_stats:
                            rate = g['출석률']
                            # 색상: 80% 이상 녹색, 60% 이상 노랑, 그 외 빨강
                            if rate >= 80:
                                bar_color = '#4CAF50'
                            elif rate >= 60:
                                bar_color = '#FFC107'
                            else:
                                bar_color = '#FF5722'

                            col_name, col_bar = st.columns([2, 5])
                            with col_name:
                                st.markdown(f"**{g['목장']}** ({g['인원']}명)")
                            with col_bar:
                                st.markdown(f"""
                                <div style="display:flex;align-items:center;gap:8px;">
                                    <div style="flex:1;background:#E8E4DF;border-radius:4px;height:20px;">
                                        <div style="width:{rate}%;background:{bar_color};height:100%;border-radius:4px;"></div>
                                    </div>
                                    <span style="font-size:14px;font-weight:600;color:#2C3E50;min-width:45px;">{rate}%</span>
                                </div>
                                """, unsafe_allow_html=True)

                        # 목장 테이블
                        st.markdown("---")
                        group_df = pd.DataFrame(group_stats)
                        group_df['출석률'] = group_df['출석률'].apply(lambda x: f"{x}%")
                        st.dataframe(group_df, use_container_width=True, hide_index=True)

                    else:
                        st.info("등록된 성도가 있는 목장이 없습니다.")


# ============================================================
# 새로고침 버튼
# ============================================================
st.markdown("---")
if st.button("🔄 데이터 새로고침", use_container_width=False):
    get_yearly_statistics.clear()
    st.rerun()
