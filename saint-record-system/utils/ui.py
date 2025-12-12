
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
            --radius-sm: 12px;
            --radius-md: 16px;
            --radius-lg: 24px;
        }

        /* Base Settings */
        .stApp {
            background-color: var(--color-bg);
            /* Background pattern simplified for performance/compatibility */
            background-image: radial-gradient(circle at 20% 20%, rgba(201, 169, 98, 0.08) 0%, transparent 50%);
            font-family: 'Noto Sans KR', sans-serif;
            color: var(--color-text);
        }

        /* Hide Default Header/Footer */
        header[data-testid="stHeader"], footer { display: none !important; }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--color-primary) 0%, #1a2a3a 100%);
            width: 280px !important;
        }
        
        section[data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.1);
        }
        
        /* Navigation Links Styling */
        .stPageLink a {
            background: transparent;
            color: rgba(255, 255, 255, 0.65) !important;
            border-radius: 12px;
            margin-bottom: 4px;
            border: none;
            transition: all 0.3s;
        }
        .stPageLink a:hover {
            background: rgba(255, 255, 255, 0.08);
            color: white !important;
        }
        /* Active Link */
        .stPageLink a[data-active="true"] {
            background: rgba(201, 169, 98, 0.15);
            color: white !important;
            border-left: 3px solid var(--color-accent);
        }
        
        /* Utils */
        .playfair { font-family: 'Playfair Display', serif; }
        
        /* Stats Card CSS */
        .stat-card {
            background: var(--color-surface);
            border-radius: var(--radius-md);
            padding: 24px;
            box-shadow: var(--shadow-soft);
            height: 100%;
            position: relative;
            transition: transform 0.3s;
        }
        .stat-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-medium); }
        .stat-card.highlight {
            background: linear-gradient(135deg, var(--color-primary) 0%, #3d5a73 100%);
            color: white;
        }
        
        .stat-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
        .stat-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; }
        .stat-icon svg { width: 24px; height: 24px; }
        .stat-icon.blue { background: #E8F4FD; color: #3498db; }
        .stat-icon.white { background: rgba(255,255,255,0.2); color: white; }
        .stat-icon.green { background: #E8F5F0; color: #4A9B7F; }
        .stat-icon.gold { background: #FDF8E8; color: #C9A962; }
        
        .stat-trend { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 4px; }
        .stat-trend.up { background: rgba(74, 155, 127, 0.12); color: #4A9B7F; }
        .stat-trend.down { background: rgba(232, 152, 94, 0.12); color: #E8985E; }
        .stat-card.highlight .stat-trend { background: rgba(255,255,255,0.2); color: white; }
        
        .stat-value { font-size: 36px; font-weight: 700; margin-bottom: 4px; font-family: 'Playfair Display', serif; color: var(--color-primary); }
        .stat-card.highlight .stat-value { color: white; }
        .stat-label { font-size: 14px; color: var(--color-text-light); }
        .stat-card.highlight .stat-label { color: rgba(255,255,255,0.7); }
        
        /* Custom Charts */
        .custom-card {
            background: white; border-radius: 24px; padding: 28px; box-shadow: var(--shadow-soft); height: 100%;
        }
        .card-title { font-size: 18px; font-weight: 600; color: var(--color-primary); display: flex; align-items: center; gap: 10px; margin-bottom: 24px; }
        .chart-container { display: flex; align-items: flex-end; justify-content: space-between; height: 200px; padding: 0 20px; }
        .bar-group { display: flex; flex-direction: column; align-items: center; gap: 12px; width: 40px; }
        .bar-wrapper { display: flex; align-items: flex-end; gap: 4px; height: 100%; }
        .bar { width: 14px; border-radius: 4px 4px 0 0; transition: height 1s ease; }
        .bar.primary { background: linear-gradient(180deg, #C9A962 0%, #D4B87A 100%); }
        .bar.secondary { background: #E8E4DF; }
        .chart-label { font-size: 12px; color: #6B7B8C; margin-top: 12px; }
        
        /* Dept List */
        .dept-row { display: flex; align-items: center; gap: 14px; padding: 12px; border-radius: 12px; margin-bottom: 8px; transition: background 0.3s; }
        .dept-row:hover { background: #F5EFE0; }
        .dept-icon-box { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
        .dept-name { font-weight: 600; color: var(--color-primary); font-size: 14px; }
        .dept-sub { font-size: 12px; color: #6B7B8C; }
        .dept-progress-bg { width: 80px; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; }
        .dept-progress-fill { height: 100%; border-radius: 3px; }
        
        </style>
    """, unsafe_allow_html=True)

def get_icon_svg(name):
    icons = {
        "users": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',
        "calendar": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="M9 14l2 2 4-4"/></svg>',
        "chart": '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>',
        "trend_up": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 4l-8 8h5v8h6v-8h5z"/></svg>',
        "trend_down": '<svg viewBox="0 0 24 24" fill="currentColor" style="transform: rotate(180deg)"><path d="M12 4l-8 8h5v8h6v-8h5z"/></svg>',
        "logo": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7v10l10 5 10-5V7L12 2zm0 2.8L18.5 8 12 11.2 5.5 8 12 4.8zM4 9.54l7 3.5v6.42l-7-3.5V9.54zm9 9.92v-6.42l7-3.5v6.42l-7 3.5z"/></svg>'
    }
    return icons.get(name, name)

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

def render_stat_card(icon_name, icon_color, value, label, trend_val, trend_dir, is_highlight=False):
    highlight_cls = "highlight" if is_highlight else ""
    return f"""
    <div class="stat-card {highlight_cls}">
        <div class="stat-header">
            <div class="stat-icon {icon_color}">{get_icon_svg(icon_name)}</div>
            <div class="stat-trend {trend_dir}">
                {get_icon_svg('trend_' + trend_dir)} {trend_val}
            </div>
        </div>
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """

def render_bar_chart(data):
    # data = [{'label': '12/15', 'p': 140, 's': 180}, ...]
    # Normalize heights to max ~150px
    bars_html = ""
    for d in data:
        p_h = min(int(d['p'] * 0.8), 160) # scale factor
        s_h = 160 # fixed max height for bg bar
        
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

def render_dept_item(emoji, bg_color, name, current, total, color):
    percent = int(current / total * 100) if total > 0 else 0
    return f"""
    <div class="dept-row">
        <div class="dept-icon-box" style="background: {bg_color};">{emoji}</div>
        <div style="flex:1;">
            <div class="dept-name">{name}</div>
            <div class="dept-sub">{current} / {total}명</div>
        </div>
        <div style="text-align: right;">
            <div class="dept-progress-bg">
                <div class="dept-progress-fill" style="width: {percent}%; background: {color};"></div>
            </div>
            <div style="font-size: 12px; font-weight: 600; color: #2C3E50; margin-top: 2px;">{percent}%</div>
        </div>
    </div>
    """
