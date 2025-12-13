import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from utils.sheets_api import SheetsAPI
from utils.ui import load_custom_css

st.set_page_config(page_title="통계", page_icon="📊", layout="wide")
load_custom_css()

# API 초기화
if 'api' not in st.session_state:
    try:
        st.session_state.api = SheetsAPI()
    except Exception as e:
        st.error(f"API 연결 오류: {e}")
        st.stop()

api = st.session_state.api


@st.cache_data(ttl=3600, show_spinner=False)
def get_statistics_data():
    """통계 데이터 조회"""
    # 성도 데이터
    members = api.get_members({'status': '재적'})
    departments = api.get_departments()
    groups = api.get_groups()

    # 최근 12주 출석 데이터
    today = datetime.today()
    last_sunday = today - timedelta(days=(today.weekday() + 1) % 7)

    weekly_data = []
    for i in range(12):
        sunday = last_sunday - timedelta(weeks=i)
        sunday_str = sunday.strftime('%Y-%m-%d')
        attendance = api.get_attendance(sunday.year, date=sunday_str)

        total = len(members)
        present = 0
        if not attendance.empty:
            present = len(attendance[attendance['attend_type'].astype(str).isin(['1', '2'])])

        weekly_data.append({
            'date': sunday_str,
            'display_date': sunday.strftime('%m/%d'),
            'total': total,
            'present': present,
            'rate': round((present / total) * 100, 1) if total > 0 else 0
        })

    weekly_data.reverse()  # 시간순 정렬

    return {
        'members': members,
        'departments': departments,
        'groups': groups,
        'weekly_data': weekly_data,
        'last_sunday': last_sunday.strftime('%Y-%m-%d')
    }


# 헤더
st.markdown("""
<h1 style="font-family: 'Playfair Display', serif; font-size: 32px; font-weight: 600; color: #2C3E50; margin-bottom: 8px;">
    📊 출석 통계
</h1>
<p style="font-size: 14px; color: #6B7B8C; margin-bottom: 24px;">
    출석 현황을 다양한 관점에서 분석합니다
</p>
""", unsafe_allow_html=True)

# 데이터 로드
with st.spinner("데이터 로딩 중..."):
    data = get_statistics_data()

members = data['members']
departments = data['departments']
groups = data['groups']
weekly_data = data['weekly_data']

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📈 주간 추이", "🏢 부서별 통계", "🏠 목장별 통계"])

# === 탭 1: 주간 출석 추이 ===
with tab1:
    st.subheader("최근 12주 출석 추이")

    # 차트 데이터 준비
    dates = [w['display_date'] for w in weekly_data]
    presents = [w['present'] for w in weekly_data]
    rates = [w['rate'] for w in weekly_data]

    # 출석 인원 차트
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=dates,
        y=presents,
        name='출석 인원',
        marker_color='#C9A962',
        text=presents,
        textposition='outside',
        textfont=dict(size=10, color='#6B7B8C')
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=rates,
        name='출석률 (%)',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#4A90D9', width=2),
        marker=dict(size=6)
    ))

    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=30, b=30),
        height=400,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color='#6B7B8C')
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
            tickfont=dict(size=11, color='#6B7B8C')
        )
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 주간 데이터 테이블
    st.subheader("주간 출석 상세")
    weekly_df = pd.DataFrame(weekly_data)
    weekly_df = weekly_df[['date', 'present', 'total', 'rate']]
    weekly_df.columns = ['날짜', '출석', '전체', '출석률(%)']
    st.dataframe(weekly_df, use_container_width=True, hide_index=True)

    # CSV 다운로드
    csv = weekly_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv,
        file_name=f"출석통계_주간_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


# === 탭 2: 부서별 통계 ===
with tab2:
    st.subheader("부서별 출석 현황")

    if departments.empty:
        st.warning("부서 데이터가 없습니다.")
    else:
        # 부서별 데이터 집계
        dept_stats = []
        for _, dept in departments.iterrows():
            dept_id = str(dept.get('dept_id', ''))
            dept_name = dept.get('dept_name', '')

            if not dept_id:
                continue

            dept_members = members[members['dept_id'].astype(str) == dept_id]
            total = len(dept_members)

            if total == 0:
                continue

            # 최근 4주 평균 출석률
            recent_presents = []
            for w in weekly_data[-4:]:
                attendance = api.get_attendance(2025, date=w['date'])
                if not attendance.empty:
                    dept_attendance = attendance[
                        attendance['member_id'].isin(dept_members['member_id'].tolist())
                    ]
                    present = len(dept_attendance[
                        dept_attendance['attend_type'].astype(str).isin(['1', '2'])
                    ])
                else:
                    present = 0
                recent_presents.append(present)

            avg_present = sum(recent_presents) / len(recent_presents) if recent_presents else 0
            avg_rate = (avg_present / total) * 100 if total > 0 else 0

            dept_stats.append({
                '부서': dept_name,
                '등록인원': total,
                '평균출석': round(avg_present, 1),
                '출석률': round(avg_rate, 1)
            })

        if dept_stats:
            dept_df = pd.DataFrame(dept_stats)

            # 파이 차트
            fig_pie = px.pie(
                dept_df,
                values='등록인원',
                names='부서',
                title='부서별 인원 분포',
                color_discrete_sequence=['#C9A962', '#4A90D9', '#7CB342', '#FF7043']
            )
            fig_pie.update_layout(height=350)
            st.plotly_chart(fig_pie, use_container_width=True)

            # 바 차트
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=dept_df['부서'],
                y=dept_df['출석률'],
                marker_color=['#C9A962', '#4A90D9', '#7CB342', '#FF7043'][:len(dept_df)],
                text=[f"{r}%" for r in dept_df['출석률']],
                textposition='outside'
            ))
            fig_bar.update_layout(
                title='부서별 평균 출석률 (최근 4주)',
                yaxis_title='출석률 (%)',
                yaxis_range=[0, 100],
                height=350
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # 테이블
            st.dataframe(dept_df, use_container_width=True, hide_index=True)

            # CSV 다운로드
            csv = dept_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 부서별 통계 CSV",
                data=csv,
                file_name=f"출석통계_부서별_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )


# === 탭 3: 목장별 통계 ===
with tab3:
    st.subheader("목장별 출석 현황")

    # 부서 선택
    if not departments.empty:
        dept_options = ['전체'] + departments['dept_name'].tolist()
        selected_dept = st.selectbox("부서 선택", dept_options)
    else:
        selected_dept = '전체'

    if groups.empty:
        st.warning("목장 데이터가 없습니다.")
    else:
        # 부서 필터링
        if selected_dept != '전체' and not departments.empty:
            dept_row = departments[departments['dept_name'] == selected_dept]
            if not dept_row.empty:
                selected_dept_id = str(dept_row.iloc[0]['dept_id'])
                filtered_groups = groups[groups['dept_id'].astype(str) == selected_dept_id]
            else:
                filtered_groups = groups
        else:
            filtered_groups = groups

        # 목장별 데이터 집계
        group_stats = []
        for _, group in filtered_groups.iterrows():
            group_id = str(group.get('group_id', ''))
            group_name = group.get('group_name', '')

            if not group_id:
                continue

            group_members = members[members['group_id'].astype(str) == group_id]
            total = len(group_members)

            if total == 0:
                continue

            # 최근 주 출석
            last_week = weekly_data[-1] if weekly_data else None
            present = 0
            if last_week:
                attendance = api.get_attendance(2025, date=last_week['date'])
                if not attendance.empty:
                    group_attendance = attendance[
                        attendance['member_id'].isin(group_members['member_id'].tolist())
                    ]
                    present = len(group_attendance[
                        group_attendance['attend_type'].astype(str).isin(['1', '2'])
                    ])

            rate = (present / total) * 100 if total > 0 else 0

            group_stats.append({
                '목장': group_name,
                '등록인원': total,
                '금주출석': present,
                '출석률': round(rate, 1)
            })

        if group_stats:
            group_df = pd.DataFrame(group_stats)
            group_df = group_df.sort_values('출석률', ascending=False)

            # 바 차트
            fig_group = go.Figure()
            colors = ['#4CAF50' if r >= 80 else '#FFC107' if r >= 60 else '#FF5722'
                      for r in group_df['출석률']]

            fig_group.add_trace(go.Bar(
                y=group_df['목장'],
                x=group_df['출석률'],
                orientation='h',
                marker_color=colors,
                text=[f"{r}%" for r in group_df['출석률']],
                textposition='outside'
            ))
            fig_group.update_layout(
                title='목장별 출석률 (금주)',
                xaxis_title='출석률 (%)',
                xaxis_range=[0, 100],
                height=max(400, len(group_df) * 30),
                yaxis=dict(autorange='reversed')
            )
            st.plotly_chart(fig_group, use_container_width=True)

            # 테이블
            st.dataframe(group_df, use_container_width=True, hide_index=True)

            # CSV 다운로드
            csv = group_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 목장별 통계 CSV",
                data=csv,
                file_name=f"출석통계_목장별_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("해당 부서에 등록된 성도가 없습니다.")

# 새로고침 버튼
st.markdown("---")
if st.button("🔄 데이터 새로고침"):
    get_statistics_data.clear()
    st.rerun()
