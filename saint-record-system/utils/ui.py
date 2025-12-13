
import streamlit as st

def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

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

        /* Navigation Links Styling */
        .stPageLink a {
            background: transparent;
            color: rgba(255, 255, 255, 0.65) !important;
            border-radius: 12px;
            margin-bottom: 4px;
            border: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .stPageLink a:hover {
            background: rgba(255, 255, 255, 0.08);
            color: white !important;
        }
        .stPageLink a[data-active="true"] {
            background: rgba(201, 169, 98, 0.15);
            color: white !important;
            border-left: 3px solid var(--color-accent);
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

    return f'''<div style="{card_bg}border-radius:20px;padding:28px;box-shadow:0 2px 20px rgba(44,62,80,0.06);position:relative;overflow:hidden;">{top_bar}<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:20px;"><div style="width:52px;height:52px;border-radius:14px;display:flex;align-items:center;justify-content:center;{icon_style}">{sized_icon_svg}</div><div style="padding:4px 10px;border-radius:20px;font-size:12px;font-weight:600;display:flex;align-items:center;gap:4px;{trend_style}">{sized_trend_svg} {trend_val}</div></div><div style="font-size:42px;font-weight:700;margin-bottom:8px;font-family:Playfair Display,serif;{value_color}line-height:1;">{value}</div><div style="font-size:14px;font-weight:500;{label_color}">{label}</div></div>'''

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
    # SVG 크기 제한 추가
    sized_svg = icon_svg.replace('<svg ', '<svg style="width:18px;height:18px;" ')

    if alert_type == "warning":
        bg_style = "background:linear-gradient(90deg,rgba(232,152,94,0.08) 0%,transparent 100%);border-left:4px solid #E8985E;"
        icon_bg = "background:rgba(232,152,94,0.15);color:#E8985E;"
    else:
        bg_style = "background:linear-gradient(90deg,rgba(201,169,98,0.08) 0%,transparent 100%);border-left:4px solid #C9A962;"
        icon_bg = "background:rgba(201,169,98,0.15);color:#C9A962;"

    return f'''<div style="display:flex;align-items:flex-start;gap:14px;padding:14px;border-radius:12px;{bg_style}margin-bottom:12px;"><div style="width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;{icon_bg}">{sized_svg}</div><div style="flex:1;"><div style="font-size:13px;font-weight:600;color:#2C3E50;margin-bottom:3px;">{title}</div><div style="font-size:12px;color:#6B7B8C;line-height:1.5;">{desc}</div></div></div>'''

def render_quick_action(icon_name, label, href="#"):
    icon_svg = get_icon_svg(icon_name)
    # SVG에 크기 제한 추가
    sized_svg = icon_svg.replace('<svg ', '<svg style="width:20px;height:20px;color:#6B7B8C;" ')
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
