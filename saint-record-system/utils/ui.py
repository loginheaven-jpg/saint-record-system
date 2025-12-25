
import streamlit as st

def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

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
            --shadow-soft: 0 2px 20px rgba(44, 62, 80, 0.06);
            --shadow-medium: 0 8px 32px rgba(44, 62, 80, 0.08);
            --shadow-glow: 0 0 40px rgba(201, 169, 98, 0.15);
            --radius-sm: 12px;
            --radius-md: 16px;
            --radius-lg: 24px;

            /* Department Colors - dashboard_v3.html 참조 */
            --dept-adults: #6B5B47;
            --dept-youth: #556B82;
            --dept-teens: #6B8E23;
            --dept-children: #D2691E;
        }

        /* Base Settings */
        .stApp {
            background-color: var(--color-bg);
            background-image:
                radial-gradient(circle at 20% 20%, rgba(201, 169, 98, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(139, 115, 85, 0.06) 0%, transparent 50%);
            font-family: 'Noto Sans KR', sans-serif;
            color: var(--color-text);
        }

        /* Hide Default Header/Footer */
        header[data-testid="stHeader"], footer { display: none !important; }
        #MainMenu { display: none; }

        /* Hide Streamlit default page navigation (small icons at top) */
        [data-testid="stSidebarNav"] { display: none !important; }
        section[data-testid="stSidebar"] > div:first-child > div:first-child { display: none !important; }

        /* Main content area */
        .main .block-container {
            padding: 32px 40px !important;
            max-width: 1400px;
        }

        /* Global Font Override - HTML 참조와 일치 */
        .main, .main *, .stMarkdown, .stMarkdown *, p, span, div, h1, h2, h3, h4, h5, h6 {
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* Playfair for headings and stat values */
        h1, .stat-value, [style*="Playfair"] {
            font-family: 'Playfair Display', serif !important;
        }

        /* HTML 참조 폰트 크기 강제 적용 */
        .stMarkdown h1 {
            font-size: 32px !important;
            font-weight: 600 !important;
            line-height: 1.2 !important;
        }

        .stMarkdown h2 {
            font-size: 18px !important;
            font-weight: 600 !important;
        }

        .stMarkdown p {
            font-size: 14px !important;
            line-height: 1.5 !important;
        }

        /* 탭 스타일 - HTML 참조 일치 */
        .stTabs [data-baseweb="tab-list"] {
            background: #F8F6F3 !important;
            border-radius: 12px !important;
            padding: 4px !important;
            gap: 4px !important;
        }

        .stTabs [data-baseweb="tab-list"] button {
            font-family: 'Noto Sans KR', sans-serif !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            padding: 10px 16px !important;
            border-radius: 8px !important;
            background: transparent !important;
            color: #6B7B8C !important;
        }

        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background: #FFFFFF !important;
            color: #2C3E50 !important;
            box-shadow: 0 2px 8px rgba(44,62,80,0.08) !important;
        }

        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 16px !important;
        }

        /* Streamlit 기본 요소 크기 조정 */
        .element-container {
            font-size: 14px !important;
        }

        /* Streamlit column gap fix */
        [data-testid="column"] {
            padding: 0 5px !important;
        }

        /* Quick action buttons spacing */
        [data-testid="column"] > div > div {
            margin-bottom: 10px;
        }

        /* 에러 메시지 스타일 */
        .stAlert {
            font-size: 13px !important;
            border-radius: 12px !important;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--color-primary) 0%, #1a2a3a 100%);
            width: 280px !important;
            box-shadow: 4px 0 24px rgba(44, 62, 80, 0.15);
        }

        section[data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.1);
        }

        section[data-testid="stSidebar"]::-webkit-scrollbar {
            width: 6px;
        }
        section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
        }

        /* Navigation Links Styling - 사이드바 메뉴 가시성 개선 */
        .stPageLink a {
            background: rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.9) !important;
            border-radius: 12px;
            margin: 0 0.5rem 4px;
            padding: 14px 16px !important;
            border: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            font-size: 14px !important;
            font-weight: 500 !important;
        }
        .stPageLink a:hover {
            background: rgba(255, 255, 255, 0.12);
            color: white !important;
        }
        .stPageLink a[data-active="true"] {
            background: rgba(201, 169, 98, 0.15);
            color: white !important;
            border-left: 3px solid var(--color-accent);
        }

        /* 사이드바 전체 텍스트 가시성 개선 */
        section[data-testid="stSidebar"] * {
            color: rgba(255, 255, 255, 0.9) !important;
        }
        section[data-testid="stSidebar"] .stPageLink span {
            color: rgba(255, 255, 255, 0.9) !important;
            font-weight: 500 !important;
        }

        /* 서브 내비게이션 - HTML 참조 .nav-sub 스타일 */
        .nav-sub-container {
            margin-left: 20px;
            padding-left: 16px;
            border-left: 1px solid rgba(255, 255, 255, 0.1);
            margin-top: 4px;
            margin-bottom: 8px;
        }
        .nav-sub-container .stPageLink a {
            padding: 10px 14px !important;
            font-size: 13px !important;
            margin: 0 0 2px !important;
        }

        /* Stats Card CSS */
        .stat-card {
            background: var(--color-surface);
            border-radius: var(--radius-md);
            padding: 28px;
            box-shadow: var(--shadow-soft);
            height: 100%;
            position: relative;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--color-accent), var(--color-secondary));
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-medium), var(--shadow-glow);
        }
        .stat-card:hover::before {
            opacity: 1;
        }
        .stat-card.highlight {
            background: linear-gradient(135deg, var(--color-primary) 0%, #3d5a73 100%);
            color: white;
        }
        .stat-card.highlight::before {
            background: linear-gradient(90deg, var(--color-accent), #E8D5A8);
            opacity: 1;
        }

        .stat-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
        .stat-icon {
            width: 52px;
            height: 52px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .stat-icon svg { width: 26px; height: 26px; }
        .stat-icon.blue { background: linear-gradient(135deg, #E8F4FD 0%, #D1E9FA 100%); color: #3498db; }
        .stat-icon.white { background: rgba(255,255,255,0.2); color: white; }
        .stat-icon.green { background: linear-gradient(135deg, #E8F5F0 0%, #D1EBE3 100%); color: #4A9B7F; }
        .stat-icon.gold { background: linear-gradient(135deg, #FDF8E8 0%, #F5EFD1 100%); color: #C9A962; }
        .stat-icon.purple { background: linear-gradient(135deg, #F3E8FD 0%, #E5D1FA 100%); color: #9b59b6; }

        .stat-trend {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .stat-trend.up { background: rgba(74, 155, 127, 0.12); color: #4A9B7F; }
        .stat-trend.down { background: rgba(232, 152, 94, 0.12); color: #E8985E; }
        .stat-card.highlight .stat-trend { background: rgba(255,255,255,0.2); color: white; }

        .stat-value {
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 8px;
            font-family: 'Playfair Display', serif;
            color: var(--color-primary);
            line-height: 1;
        }
        .stat-card.highlight .stat-value { color: white; }
        .stat-label { font-size: 14px; color: var(--color-text-light); font-weight: 500; }
        .stat-card.highlight .stat-label { color: rgba(255,255,255,0.7); }

        /* Card Base */
        .custom-card {
            background: var(--color-surface);
            border-radius: var(--radius-lg);
            padding: 28px;
            box-shadow: var(--shadow-soft);
            height: 100%;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }

        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--color-primary);
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 0;
        }
        .card-title svg {
            width: 20px;
            height: 20px;
            color: var(--color-accent);
        }

        .card-action {
            font-size: 13px;
            color: var(--color-secondary);
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: color 0.2s ease;
        }
        .card-action:hover {
            color: var(--color-accent);
        }

        /* Tabs */
        .tabs-container {
            margin-bottom: 20px;
        }
        .tabs {
            display: flex;
            background: var(--color-bg);
            border-radius: var(--radius-sm);
            padding: 4px;
            gap: 4px;
        }
        .tab-btn {
            flex: 1;
            padding: 10px 16px;
            font-size: 13px;
            font-weight: 500;
            color: var(--color-text-light);
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
        .tab-btn:hover {
            color: var(--color-primary);
            background: rgba(255, 255, 255, 0.5);
        }
        .tab-btn.active {
            background: var(--color-surface);
            color: var(--color-primary);
            box-shadow: 0 2px 8px rgba(44, 62, 80, 0.08);
        }

        /* Department/Mokjang List */
        .dept-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .dept-item {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px;
            background: var(--color-bg);
            border-radius: var(--radius-sm);
            transition: all 0.3s ease;
        }
        .dept-item:hover {
            background: var(--color-accent-light);
            transform: translateX(4px);
        }
        .dept-icon {
            width: 42px;
            height: 42px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: white;
        }
        .dept-icon.adults { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .dept-icon.youth { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .dept-icon.teens { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .dept-icon.children { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
        .dept-icon.nepal { background: linear-gradient(135deg, #E8685C 0%, #C75B50 100%); }
        .dept-icon.russia { background: linear-gradient(135deg, #5B8DEE 0%, #4A7BD9 100%); }
        .dept-icon.philippines { background: linear-gradient(135deg, #FFD93D 0%, #E5C235 100%); }
        .dept-icon.thailand { background: linear-gradient(135deg, #9B59B6 0%, #8E44AD 100%); }
        .dept-icon.benin { background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%); }
        .dept-icon.congo { background: linear-gradient(135deg, #3498DB 0%, #2980B9 100%); }
        .dept-icon.chile { background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%); }
        .dept-icon.cheorwon { background: linear-gradient(135deg, #1ABC9C 0%, #16A085 100%); }

        .dept-info { flex: 1; }
        .dept-name { font-size: 14px; font-weight: 600; color: var(--color-primary); margin-bottom: 3px; }
        .dept-count { font-size: 12px; color: var(--color-text-light); }
        .dept-progress { width: 90px; text-align: right; }
        .progress-bar {
            height: 6px;
            background: var(--color-border);
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 6px;
        }
        .progress-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 1s ease;
        }
        .progress-fill.high { background: linear-gradient(90deg, #4A9B7F, #6BC9A8); }
        .progress-fill.medium { background: linear-gradient(90deg, #C9A962, #D4B87A); }
        .progress-fill.low { background: linear-gradient(90deg, #E8985E, #F2B07E); }
        .progress-text { font-size: 13px; font-weight: 600; color: var(--color-primary); }

        /* Alerts */
        .alerts-section {
            margin-top: 24px;
            padding-top: 20px;
            border-top: 1px solid var(--color-border);
        }
        .alert-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .alert-item {
            display: flex;
            align-items: flex-start;
            gap: 14px;
            padding: 14px;
            border-radius: var(--radius-sm);
            border-left: 4px solid transparent;
            transition: all 0.3s ease;
        }
        .alert-item:hover {
            transform: translateX(4px);
        }
        .alert-item.warning {
            background: linear-gradient(90deg, rgba(232, 152, 94, 0.08) 0%, transparent 100%);
            border-left-color: var(--color-warning);
        }
        .alert-item.info {
            background: linear-gradient(90deg, rgba(201, 169, 98, 0.08) 0%, transparent 100%);
            border-left-color: var(--color-accent);
        }
        .alert-icon {
            width: 34px;
            height: 34px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .alert-icon.warning { background: rgba(232, 152, 94, 0.15); color: var(--color-warning); }
        .alert-icon.info { background: rgba(201, 169, 98, 0.15); color: var(--color-accent); }
        .alert-icon svg { width: 16px; height: 16px; }
        .alert-content { flex: 1; }
        .alert-title { font-size: 13px; font-weight: 600; color: var(--color-primary); margin-bottom: 3px; }
        .alert-desc { font-size: 12px; color: var(--color-text-light); line-height: 1.5; }

        /* Quick Actions */
        .quick-actions {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid var(--color-border);
        }
        .quick-actions-title {
            font-size: 12px;
            font-weight: 600;
            color: var(--color-text-light);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 14px;
        }
        .action-buttons {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        .action-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            padding: 16px 12px;
            background: var(--color-bg);
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
            text-decoration: none;
        }
        .action-btn:hover {
            background: var(--color-accent-light);
            border-color: var(--color-accent);
            transform: translateY(-2px);
        }
        .action-btn svg {
            width: 22px;
            height: 22px;
            color: var(--color-secondary);
        }
        .action-btn:hover svg {
            color: var(--color-accent);
        }
        .action-btn span {
            font-size: 12px;
            font-weight: 500;
            color: var(--color-text);
        }

        /* Chart Legend */
        .chart-legend {
            display: flex;
            justify-content: center;
            gap: 32px;
            margin-top: 20px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: var(--color-text-light);
        }
        .legend-dot {
            width: 12px;
            height: 12px;
            border-radius: 4px;
        }
        .legend-dot.primary { background: var(--color-accent); }
        .legend-dot.secondary { background: #E8E4DF; }

        /* Scrollable List */
        .scroll-list {
            max-height: 280px;
            overflow-y: auto;
            padding-right: 8px;
        }
        .scroll-list::-webkit-scrollbar {
            width: 6px;
        }
        .scroll-list::-webkit-scrollbar-track {
            background: transparent;
        }
        .scroll-list::-webkit-scrollbar-thumb {
            background: var(--color-border);
            border-radius: 3px;
        }
        .scroll-list::-webkit-scrollbar-thumb:hover {
            background: var(--color-secondary);
        }

        /* ========================================
           Stacked Bar Chart - dashboard_v3.html
           ======================================== */
        .stacked-chart-section {
            background: transparent;
            padding: 0;
            margin-bottom: 16px;
        }

        .chart-wrapper {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            height: 280px;
            gap: 16px;
            padding: 20px 0;
            border-bottom: 2px solid var(--color-border);
        }

        .bar-group {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
        }

        .stacked-bar {
            width: 100%;
            max-width: 60px;
            height: 240px;
            background: white;
            border-radius: 6px 6px 0 0;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .stacked-bar:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        }

        .bar-segment {
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 11px;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .bar-segment.adults { background: var(--dept-adults); }
        .bar-segment.youth { background: var(--dept-youth); }
        .bar-segment.teens { background: var(--dept-teens); }
        .bar-segment.children { background: var(--dept-children); }

        .bar-label {
            font-size: 13px;
            font-weight: 600;
            color: var(--color-primary);
            text-align: center;
        }

        /* Stacked Chart Legend */
        .stacked-chart-legend {
            display: flex;
            justify-content: center;
            gap: 32px;
            flex-wrap: wrap;
            padding-top: 20px;
            border-top: 1px solid var(--color-border);
            margin-top: 20px;
        }

        .legend-item-dept {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: var(--color-text);
        }

        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }

        .legend-color.adults { background: var(--dept-adults); }
        .legend-color.youth { background: var(--dept-youth); }
        .legend-color.teens { background: var(--dept-teens); }
        .legend-color.children { background: var(--dept-children); }

        /* ========================================
           Department Cards - dashboard_v3.html
           ======================================== */
        .hierarchy-section {
            background: transparent;
            padding: 0;
            margin-bottom: 16px;
        }

        .section-title {
            font-size: 20px;
            font-weight: 600;
            color: var(--color-primary);
            margin-bottom: 6px;
            padding: 0;
            display: flex;
            align-items: center;
            gap: 10px;
            line-height: 1.4;
        }

        .section-title svg {
            width: 22px;
            height: 22px;
            color: var(--color-accent);
            flex-shrink: 0;
        }

        /* 섹션 제목 + 인라인 범례 (같은 줄) */
        .section-title-row {
            font-size: 20px;
            font-weight: 600;
            color: var(--color-primary);
            margin-bottom: 6px;
            padding: 0;
            display: flex;
            align-items: center;
            gap: 10px;
            line-height: 1.4;
        }
        .section-title-row svg {
            width: 22px;
            height: 22px;
            color: var(--color-accent);
            flex-shrink: 0;
        }
        .inline-legend {
            margin-left: auto;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
            font-weight: 400;
            color: #6B7B8C;
        }
        .legend-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 2px;
            margin-right: 4px;
        }

        /* 데이터 영역 좌측 강조 바 */
        .data-content {
            border-left: 4px solid var(--color-accent);
            padding-left: 16px;
            margin-left: 8px;
            background: rgba(201, 169, 98, 0.05);
            border-radius: 0 8px 8px 0;
            padding-top: 12px;
            padding-bottom: 12px;
        }

        .dept-container {
            display: grid;
            grid-template-columns: repeat(4, 1fr);  /* 기본: 4x1 */
            gap: 16px;
            margin-bottom: 20px;
        }

        .dept-card {
            background: linear-gradient(135deg, var(--color-accent-light) 0%, rgba(201, 169, 98, 0.05) 100%);
            border: 2px solid var(--color-border);
            border-radius: var(--radius-md);
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: visible;
        }

        .dept-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            border-radius: 16px 16px 0 0;
            transition: all 0.3s ease;
        }

        .dept-card.adults::before { background: var(--dept-adults); }
        .dept-card.youth::before { background: var(--dept-youth); }
        .dept-card.teens::before { background: var(--dept-teens); }
        .dept-card.children::before { background: var(--dept-children); }

        .dept-card:hover {
            border-color: var(--color-accent);
            background: linear-gradient(135deg, var(--color-accent-light) 0%, rgba(201, 169, 98, 0.15) 100%);
            box-shadow: 0 4px 16px rgba(201, 169, 98, 0.2);
            transform: translateY(-2px);
        }

        .dept-card.active {
            border-color: var(--color-accent);
            background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-secondary) 100%);
            color: white;
        }

        .dept-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }

        .dept-card-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            background: rgba(255, 255, 255, 0.3);
        }

        .dept-card.active .dept-card-icon {
            background: rgba(255, 255, 255, 0.2);
        }

        .dept-card-name {
            font-size: 16px;
            font-weight: 600;
            color: var(--color-primary);
        }

        .dept-card.active .dept-card-name {
            color: white;
        }

        .dept-card-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--color-border);
        }

        .dept-card.active .dept-card-stats {
            border-top-color: rgba(255, 255, 255, 0.2);
        }

        .stat-box {
            text-align: center;
        }

        .stat-box-label {
            font-size: 13px;
            color: var(--color-text-light);
            margin-bottom: 4px;
            font-weight: 500;
        }

        .dept-card.active .stat-box-label {
            color: rgba(255, 255, 255, 0.7);
        }

        .stat-box-value {
            font-size: 18px;
            font-weight: 700;
            color: var(--color-primary);
        }

        .dept-card.active .stat-box-value {
            color: white;
        }

        /* ========================================
           Department Popover - dashboard_v3.html
           ======================================== */
        .dept-popover {
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%) translateY(-12px);
            background: white;
            border-radius: 12px;
            padding: 14px 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            pointer-events: auto;
            min-width: 280px;
        }

        .dept-card:hover .dept-popover {
            opacity: 1;
            visibility: visible;
            transform: translateX(-50%) translateY(-16px);
        }

        .dept-popover::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid white;
        }

        .popover-title {
            font-size: 12px;
            font-weight: 600;
            color: #6B7B8C;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .popover-chart {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            height: 52px;
            gap: 4px;
        }

        .popover-bar {
            flex: 1;
            border-radius: 2px;
            transition: all 0.2s ease;
            min-height: 4px;
            background: #D0D0D0;
        }

        .dept-card.adults:hover .popover-bar { background: var(--dept-adults); }
        .dept-card.youth:hover .popover-bar { background: var(--dept-youth); }
        .dept-card.teens:hover .popover-bar { background: var(--dept-teens); }
        .dept-card.children:hover .popover-bar { background: var(--dept-children); }

        /* ========================================
           Group Grid - dashboard_v3.html
           ======================================== */
        .groups-section {
            margin-top: 28px;
            padding-top: 28px;
            border-top: 2px solid var(--color-border);
        }

        .groups-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--color-text-light);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
            padding: 8px 0;
            line-height: 1.4;
        }

        .group-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
        }

        .group-card {
            background: var(--color-bg);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            padding: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .group-card:hover {
            background: var(--color-accent-light);
            border-color: var(--color-accent);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(201, 169, 98, 0.15);
        }

        .group-card-name {
            font-size: 13px;
            font-weight: 600;
            color: var(--color-primary);
            margin-bottom: 8px;
        }

        .group-card-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: var(--color-text-light);
        }

        .group-card-count {
            background: var(--color-accent-light);
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 600;
            color: var(--color-accent);
        }

        .group-card:hover .group-card-count {
            background: var(--color-accent);
            color: white;
        }

        /* ========================================
           Attendance Modal - dashboard_v3.html
           ======================================== */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        }

        .attendance-modal {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 1000px;
            width: 90%;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
        }

        .modal-header {
            padding: 24px;
            border-bottom: 2px solid #E8E4DF;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-title {
            font-family: 'Playfair Display', serif;
            font-size: 24px;
            font-weight: 600;
            color: #2C3E50;
        }

        .modal-body {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
        }

        .attendance-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        .attendance-table thead {
            position: sticky;
            top: 0;
            background: #F8F6F3;
            z-index: 10;
        }

        .attendance-table th {
            padding: 12px 8px;
            text-align: center;
            font-weight: 600;
            color: #2C3E50;
            border-bottom: 2px solid #E8E4DF;
            white-space: nowrap;
            font-size: 12px;
        }

        .attendance-table th:first-child {
            text-align: left;
            min-width: 120px;
        }

        .attendance-table td {
            padding: 12px 8px;
            text-align: center;
            border-bottom: 1px solid #E8E4DF;
            color: #6B7B8C;
        }

        .attendance-table td:first-child {
            text-align: left;
            font-weight: 500;
            color: #2C3E50;
        }

        .attendance-table tbody tr:hover {
            background: #F8F6F3;
        }

        .modal-footer {
            padding: 16px 24px;
            border-top: 2px solid #E8E4DF;
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }

        /* Responsive */
        @media (max-width: 1200px) {
            .dept-container {
                grid-template-columns: repeat(2, 1fr);  /* 태블릿: 2x2 */
            }
        }

        @media (max-width: 1024px) {
            .chart-wrapper {
                height: 220px;
            }

            .stacked-bar {
                height: 180px;
            }
        }

        @media (max-width: 768px) {
            .dept-container {
                grid-template-columns: 1fr;  /* 모바일: 1x4 */
            }

            .group-grid {
                grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            }

            .chart-wrapper {
                height: 180px;
                gap: 8px;
            }

            .stacked-bar {
                height: 140px;
                max-width: 50px;
            }

            .bar-label {
                font-size: 11px;
            }
        }

        /* Animation */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .stat-card { animation: fadeInUp 0.6s ease forwards; }

        /* Playfair utility */
        .playfair { font-family: 'Playfair Display', serif; }

        /* Streamlit specific overrides */
        .stSelectbox > div > div {
            background: white;
            border-radius: 12px;
        }
        .stButton > button {
            border-radius: 12px;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-medium);
        }

        </style>
    """, unsafe_allow_html=True)

# SVG Icons
ICONS = {
    "users": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',
    "check": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>',
    "chart": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    "user-plus": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>',
    "clipboard": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="M9 14l2 2 4-4"/></svg>',
    "search": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>',
    "file": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>',
    "warning": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "gift": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>',
    "bar-chart": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>',
    "grid": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>',
    "trend_up": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 4l-8 8h5v8h6v-8h5z"/></svg>',
    "trend_down": '<svg viewBox="0 0 24 24" fill="currentColor" style="transform: rotate(180deg)"><path d="M12 4l-8 8h5v8h6v-8h5z"/></svg>',
}

def get_icon_svg(name):
    return ICONS.get(name, name)

def render_stat_card(icon_name, icon_color, value, label, trend_val, trend_dir, is_highlight=False):
    icon_svg = get_icon_svg(icon_name)
    trend_svg = get_icon_svg('trend_' + trend_dir)

    # Icon color backgrounds
    icon_colors = {
        'blue': 'background:linear-gradient(135deg,#E8F4FD 0%,#D1E9FA 100%);color:#3498db;',
        'white': 'background:rgba(255,255,255,0.2);color:white;',
        'green': 'background:linear-gradient(135deg,#E8F5F0 0%,#D1EBE3 100%);color:#4A9B7F;',
        'gold': 'background:linear-gradient(135deg,#FDF8E8 0%,#F5EFD1 100%);color:#C9A962;',
        'purple': 'background:linear-gradient(135deg,#F3E8FD 0%,#E5D1FA 100%);color:#9b59b6;',
    }
    icon_style = icon_colors.get(icon_color, icon_colors['blue'])

    # Trend colors
    if is_highlight:
        trend_style = 'background:rgba(255,255,255,0.2);color:white;'
    elif trend_dir == 'up':
        trend_style = 'background:rgba(74,155,127,0.12);color:#4A9B7F;'
    else:
        trend_style = 'background:rgba(232,152,94,0.12);color:#E8985E;'

    # Card styles
    if is_highlight:
        card_bg = 'background:linear-gradient(135deg,#2C3E50 0%,#3d5a73 100%);'
        value_color = 'color:white;'
        label_color = 'color:rgba(255,255,255,0.7);'
        top_bar = '<div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#C9A962,#E8D5A8);"></div>'
    else:
        card_bg = 'background:#FFFFFF;'
        value_color = 'color:#2C3E50;'
        label_color = 'color:#6B7B8C;'
        top_bar = ''

    # SVG 크기 조정
    sized_icon_svg = icon_svg.replace('<svg ', '<svg style="width:26px;height:26px;" ')
    sized_trend_svg = trend_svg.replace('<svg ', '<svg style="width:12px;height:12px;" ')

    # HTML 참조: border-radius: var(--radius-md) = 16px
    # 수정: 패딩 축소, 아이콘+숫자 가로 배치
    return f'''<div style="{card_bg}border-radius:16px;padding:16px 20px;box-shadow:0 2px 20px rgba(44,62,80,0.06);position:relative;overflow:hidden;">{top_bar}<div style="display:flex;justify-content:space-between;align-items:center;"><div style="display:flex;align-items:center;gap:14px;"><div style="width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;flex-shrink:0;{icon_style}">{sized_icon_svg}</div><div><div style="font-size:32px;font-weight:700;font-family:Playfair Display,serif;{value_color}line-height:1;">{value}</div><div style="font-size:12px;font-weight:500;margin-top:2px;{label_color}">{label}</div></div></div><div style="padding:4px 10px;border-radius:20px;font-size:11px;font-weight:600;display:flex;align-items:center;gap:4px;{trend_style}">{sized_trend_svg} {trend_val}</div></div></div>'''

def render_dept_item(emoji, css_class, name, current, total):
    percent = int(current / total * 100) if total > 0 else 0

    # Progress bar gradient based on percentage
    if percent >= 75:
        progress_bg = "linear-gradient(90deg, #4A9B7F, #6BC9A8)"
    elif percent >= 65:
        progress_bg = "linear-gradient(90deg, #C9A962, #D4B87A)"
    else:
        progress_bg = "linear-gradient(90deg, #E8985E, #F2B07E)"

    # Icon gradient based on css_class
    icon_gradients = {
        "adults": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "youth": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "teens": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "children": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "nepal": "linear-gradient(135deg, #E8685C 0%, #C75B50 100%)",
        "russia": "linear-gradient(135deg, #5B8DEE 0%, #4A7BD9 100%)",
        "philippines": "linear-gradient(135deg, #FFD93D 0%, #E5C235 100%)",
        "thailand": "linear-gradient(135deg, #9B59B6 0%, #8E44AD 100%)",
        "benin": "linear-gradient(135deg, #2ECC71 0%, #27AE60 100%)",
        "congo": "linear-gradient(135deg, #3498DB 0%, #2980B9 100%)",
        "chile": "linear-gradient(135deg, #E74C3C 0%, #C0392B 100%)",
        "cheorwon": "linear-gradient(135deg, #1ABC9C 0%, #16A085 100%)",
    }
    icon_bg = icon_gradients.get(css_class, "linear-gradient(135deg, #667eea 0%, #764ba2 100%)")

    return f'''<div style="display:flex;align-items:center;gap:14px;padding:14px;background:#F8F6F3;border-radius:12px;margin-bottom:12px;"><div style="width:42px;height:42px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;background:{icon_bg};">{emoji}</div><div style="flex:1;"><div style="font-size:14px;font-weight:600;color:#2C3E50;margin-bottom:3px;">{name}</div><div style="font-size:12px;color:#6B7B8C;">{current} / {total}명</div></div><div style="width:90px;text-align:right;"><div style="height:6px;background:#E8E4DF;border-radius:3px;overflow:hidden;margin-bottom:6px;"><div style="width:{percent}%;height:100%;background:{progress_bg};border-radius:3px;"></div></div><div style="font-size:13px;font-weight:600;color:#2C3E50;">{percent}%</div></div></div>'''

def render_alert_item(alert_type, icon_name, title, desc):
    icon_svg = get_icon_svg(icon_name)
    # SVG 크기: HTML 참조 .alert-icon svg { width: 16px; height: 16px; }
    sized_svg = icon_svg.replace('<svg ', '<svg style="width:16px;height:16px;" ')

    if alert_type == "warning":
        bg_style = "background:linear-gradient(90deg,rgba(232,152,94,0.08) 0%,transparent 100%);border-left:4px solid #E8985E;"
        icon_bg = "background:rgba(232,152,94,0.15);color:#E8985E;"
    else:
        bg_style = "background:linear-gradient(90deg,rgba(201,169,98,0.08) 0%,transparent 100%);border-left:4px solid #C9A962;"
        icon_bg = "background:rgba(201,169,98,0.15);color:#C9A962;"

    return f'''<div style="display:flex;align-items:flex-start;gap:14px;padding:14px;border-radius:12px;{bg_style}margin-bottom:12px;"><div style="width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;{icon_bg}">{sized_svg}</div><div style="flex:1;"><div style="font-size:13px;font-weight:600;color:#2C3E50;margin-bottom:3px;">{title}</div><div style="font-size:12px;color:#6B7B8C;line-height:1.5;">{desc}</div></div></div>'''

def render_quick_action(icon_name, label, href="#"):
    icon_svg = get_icon_svg(icon_name)
    # SVG 크기: HTML 참조 .action-btn svg { width: 22px; height: 22px; }
    sized_svg = icon_svg.replace('<svg ', '<svg style="width:22px;height:22px;color:#8B7355;" ')
    return f'''<a href="{href}" style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 12px;background:#F8F6F3;border-radius:12px;text-decoration:none;border:2px solid transparent;">{sized_svg}<span style="font-size:12px;font-weight:500;color:#2C3E50;">{label}</span></a>'''

def render_chart_legend():
    return '''<div style="display:flex;justify-content:center;gap:32px;margin-top:20px;"><div style="display:flex;align-items:center;gap:8px;font-size:13px;color:#6B7B8C;"><div style="width:12px;height:12px;border-radius:4px;background:#C9A962;"></div><span>출석 인원</span></div><div style="display:flex;align-items:center;gap:8px;font-size:13px;color:#6B7B8C;"><div style="width:12px;height:12px;border-radius:4px;background:#E8E4DF;"></div><span>전체 인원</span></div></div>'''

def render_list_item(icon, name, count, percent, icon_bg):
    if percent >= 75:
        progress_gradient = "linear-gradient(90deg, #4A9B7F, #6BC9A8)"
    elif percent >= 65:
        progress_gradient = "linear-gradient(90deg, #C9A962, #D4B87A)"
    else:
        progress_gradient = "linear-gradient(90deg, #E8985E, #F2B07E)"

    return f'''
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
    '''

def render_bar_chart(data):
    bars_html = ""
    for d in data:
        p_h = min(int(d['p'] * 0.8), 160)
        s_h = 160

        bars_html += f"""
        <div class="bar-group">
            <div class="bar-wrapper">
                <div class="bar primary" style="height: {p_h}px;"></div>
                <div class="bar secondary" style="height: {s_h}px;"></div>
            </div>
            <div class="chart-label">{d['label']}</div>
        </div>
        """
    return f"""
    <div class="chart-container">
        {bars_html}
    </div>
    """


# ============================================================
# 새 컴포넌트 함수 (dashboard_v3.html 기반)
# ============================================================

def render_dept_chart_legend():
    """부서별 4색 레전드 (장년/청년/청소년/어린이)"""
    return '''<div class="stacked-chart-legend">
        <div class="legend-item-dept"><div class="legend-color adults"></div><span>장년부</span></div>
        <div class="legend-item-dept"><div class="legend-color youth"></div><span>청년부</span></div>
        <div class="legend-item-dept"><div class="legend-color teens"></div><span>청소년부</span></div>
        <div class="legend-item-dept"><div class="legend-color children"></div><span>어린이부</span></div>
    </div>'''


def render_dept_card(dept_id: str, name: str, emoji: str,
                     groups_count: int, members_count: int,
                     attendance_rate: int, trend_data: list, is_active: bool = False) -> str:
    """
    호버 시 팝오버 차트 표시되는 부서 카드

    Args:
        dept_id: 부서 ID (adults, youth, teens, children)
        name: 부서명 (장년부, 청년부 등)
        emoji: 아이콘 이모지
        groups_count: 목장/반 수
        members_count: 성도 수
        attendance_rate: 출석률 (%)
        trend_data: 8주 출석률 리스트 [80, 82, 76, ...]
        is_active: 선택된 상태 여부
    """
    active_class = "active" if is_active else ""

    # 팝오버 미니 차트 바 생성
    popover_bars = ""
    if trend_data and len(trend_data) > 0:
        max_val = max(trend_data) if max(trend_data) > 0 else 100
        for val in trend_data:
            height_pct = int((val / max_val) * 100) if max_val > 0 else 0
            popover_bars += f'<div class="popover-bar" style="height:{height_pct}%;" title="{val}%"></div>'
    else:
        # 기본 8개 바
        for _ in range(8):
            popover_bars += '<div class="popover-bar" style="height:50%;"></div>'

    # 목장/반 라벨 (어린이부는 "반", 나머지는 "목장")
    group_label = "반" if dept_id == "children" else "목장"

    return f'''<div class="dept-card {dept_id} {active_class}" data-dept="{dept_id}">
        <div class="dept-popover">
            <div class="popover-title">{name} 8주 출석률 추이</div>
            <div class="popover-chart">{popover_bars}</div>
        </div>
        <div class="dept-header">
            <div class="dept-card-icon">{emoji}</div>
            <div class="dept-card-name">{name}</div>
        </div>
        <div class="dept-card-stats">
            <div class="stat-box">
                <div class="stat-box-label">{group_label}</div>
                <div class="stat-box-value">{groups_count}</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-label">성도</div>
                <div class="stat-box-value">{members_count}</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-label">출석률</div>
                <div class="stat-box-value">{attendance_rate}%</div>
            </div>
        </div>
    </div>'''


def render_group_card(name: str, members_count: int) -> str:
    """목장/반 카드"""
    return f'''<div class="group-card">
        <div class="group-card-name">{name}</div>
        <div class="group-card-info">
            <span>성도</span>
            <span class="group-card-count">{members_count}</span>
        </div>
    </div>'''


def render_group_grid(groups: list, dept_name: str = "장년부") -> str:
    """
    목장 그리드 렌더링

    Args:
        groups: [{"name": "네팔 목장", "members_count": 13}, ...]
        dept_name: 부서명 (타이틀에 표시)
    """
    cards_html = ""
    for g in groups:
        cards_html += render_group_card(g.get('name', ''), g.get('members_count', 0))

    return f'''<div class="groups-section">
        <div class="groups-title">선택된 부서의 목장 ({dept_name})</div>
        <div class="group-grid">{cards_html}</div>
    </div>'''


def render_section_title(icon_svg: str, title: str) -> str:
    """섹션 타이틀 (아이콘 + 제목)"""
    return f'''<div class="section-title">{icon_svg}{title}</div>'''


def render_attendance_table(data: dict, dept_name: str, group_name: str = None) -> str:
    """
    출석 현황 테이블 HTML 렌더링

    Args:
        data: {"weeks": ["12/7", "11/30", ...], "members": [{"name": ..., "group_name": ..., "attendance": [1,0,...]}, ...]}
        dept_name: 부서명
        group_name: 목장명 (선택, None이면 부서 전체)
    """
    weeks = data.get('weeks', [])
    members = data.get('members', [])

    if not members:
        return f'''<div class="attendance-table-section">
            <div class="attendance-table-header">
                <span class="attendance-table-title">📋 {dept_name} 출석 현황</span>
            </div>
            <p style="color:#6B7B8C;font-size:14px;text-align:center;padding:40px;">출석 데이터가 없습니다</p>
        </div>'''

    title = f"{group_name} 출석 현황" if group_name else f"{dept_name} 출석 현황"

    # 테이블 헤더
    header_cells = '<th>이름</th><th>목장</th>'
    for w in weeks:
        header_cells += f'<th>{w}</th>'

    # 테이블 바디
    body_rows = ''
    for member in members:
        name = member.get('name', '')
        group = member.get('group_name', '-')
        attendance = member.get('attendance', [])

        cells = f'<td class="name-cell">{name}</td><td class="group-cell">{group}</td>'
        for i, att in enumerate(attendance):
            if att == 1:
                cells += '<td class="att-cell att-present">✓</td>'
            else:
                cells += '<td class="att-cell att-absent">-</td>'

        body_rows += f'<tr>{cells}</tr>'

    # 출석 통계 (출석률)
    total_checks = len(members) * len(weeks)
    present_checks = sum(sum(m.get('attendance', [])) for m in members)
    rate = round((present_checks / total_checks) * 100, 1) if total_checks > 0 else 0

    return f'''<div class="attendance-table-section">
        <div class="attendance-table-header">
            <span class="attendance-table-title">📋 {title} (최근 8주)</span>
            <span class="attendance-table-stat">평균 출석률: <strong>{rate}%</strong> ({present_checks}/{total_checks})</span>
        </div>
        <div class="attendance-table-wrapper">
            <table class="attendance-table">
                <thead>
                    <tr>{header_cells}</tr>
                </thead>
                <tbody>
                    {body_rows}
                </tbody>
            </table>
        </div>
    </div>'''


def get_attendance_table_css() -> str:
    """출석 테이블 전용 CSS"""
    return '''
    <style>
    .attendance-table-section {
        background: transparent;
        padding: 0;
        margin-top: 24px;
    }

    .attendance-table-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        flex-wrap: wrap;
        gap: 12px;
    }

    .attendance-table-title {
        font-size: 20px;
        font-weight: 600;
        color: #2C3E50;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .attendance-table-stat {
        font-size: 14px;
        color: #6B7B8C;
    }

    .attendance-table-stat strong {
        color: #4A9B7F;
        font-weight: 700;
    }

    .attendance-table-wrapper {
        overflow-x: auto;
        max-height: 500px;
        overflow-y: auto;
    }

    .attendance-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        min-width: 600px;
    }

    .attendance-table thead {
        position: sticky;
        top: 0;
        background: #F8F6F3;
        z-index: 10;
    }

    .attendance-table th {
        padding: 12px 8px;
        text-align: center;
        font-weight: 600;
        color: #2C3E50;
        border-bottom: 2px solid #E8E4DF;
        white-space: nowrap;
        font-size: 12px;
    }

    .attendance-table th:first-child,
    .attendance-table th:nth-child(2) {
        text-align: left;
        min-width: 80px;
    }

    .attendance-table td {
        padding: 10px 8px;
        text-align: center;
        border-bottom: 1px solid #E8E4DF;
        color: #6B7B8C;
    }

    .attendance-table .name-cell {
        text-align: left;
        font-weight: 500;
        color: #2C3E50;
        white-space: nowrap;
    }

    .attendance-table .group-cell {
        text-align: left;
        font-size: 12px;
        color: #8B7355;
        white-space: nowrap;
    }

    .attendance-table .att-cell {
        width: 45px;
        font-weight: 600;
    }

    .attendance-table .att-present {
        color: #4A9B7F;
        background: rgba(74, 155, 127, 0.08);
    }

    .attendance-table .att-absent {
        color: #D0D0D0;
    }

    .attendance-table tbody tr:hover {
        background: #F8F6F3;
    }

    .attendance-table tbody tr:hover .att-present {
        background: rgba(74, 155, 127, 0.15);
    }

    @media (max-width: 768px) {
        .attendance-table-header {
            flex-direction: column;
            align-items: flex-start;
        }

        .attendance-table {
            font-size: 11px;
        }

        .attendance-table th,
        .attendance-table td {
            padding: 8px 4px;
        }
    }
    </style>
    '''
