import streamlit as st

def load_custom_css():
    """UI 커스터마이징을 위한 CSS 주입"""
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

        /* Global Font Settings */
        html, body, [class*="css"] {
            font-family: 'Noto Sans KR', sans-serif;
            color: var(--color-text);
        }

        /* Background Pattern */
        .stApp {
            background-color: var(--color-bg);
            background-image: 
                radial-gradient(circle at 20% 20%, rgba(201, 169, 98, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(139, 115, 85, 0.06) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.5) 0%, transparent 70%);
            background-attachment: fixed;
        }

        /* Headings */
        h1, h2, h3 {
            font-family: 'Playfair Display', serif !important;
            font-weight: 700 !important;
            color: var(--color-primary) !important;
        }

        /* Header Style Override */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--color-primary) 0%, #1a2a3a 100%);
            box-shadow: 4px 0 24px rgba(44, 62, 80, 0.15);
        }
        section[data-testid="stSidebar"] * {
            color: rgba(255, 255, 255, 0.9) !important;
        }
        
        /* Metric Cards */
        div[data-testid="stMetricValue"] {
            font-family: 'Playfair Display', serif;
            color: var(--color-primary);
        }

        /* Standard Streamlit Containers */
        .stButton button {
            background: linear-gradient(135deg, var(--color-accent) 0%, #D4B87A 100%);
            color: white !important;
            border: none;
            border-radius: var(--radius-sm);
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(201, 169, 98, 0.2);
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(201, 169, 98, 0.4);
        }

        /* Dataframes & Tables */
        div[data-testid="stDataFrame"] {
            border-radius: var(--radius-md);
            border: 1px solid var(--color-border);
            box-shadow: var(--shadow-soft);
            background: white;
            padding: 10px;
        }

        /* Custom Card Class (HTML injection) */
        .card {
            background: var(--color-surface);
            border-radius: var(--radius-md);
            padding: 24px;
            box-shadow: var(--shadow-soft);
            border: 1px solid var(--color-border);
            margin-bottom: 20px;
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-medium);
        }
        
        .card-header {
            font-family: 'Playfair Display', serif;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--color-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .stat-value {
            font-family: 'Playfair Display', serif;
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--color-primary);
            line-height: 1.2;
        }
        
        .stat-label {
            color: var(--color-text-light);
            font-size: 0.9rem;
            font-weight: 500;
            margin-top: 4px;
        }

        .highlight-card {
            background: linear-gradient(135deg, var(--color-primary) 0%, #3d5a73 100%);
            color: white;
            border: none;
        }
        .highlight-card .stat-value, 
        .highlight-card .stat-label,
        .highlight-card .card-header {
            color: white !important;
        }
        .highlight-card::before {
            content: '';
            display: block;
            height: 4px;
            width: 100%;
            background: linear-gradient(90deg, var(--color-accent), #E8D5A8);
            margin-bottom: 16px;
            border-radius: 2px;
        }
        
        /* Tags/Badges */
        .tag {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .tag-success { background: rgba(74, 155, 127, 0.1); color: var(--color-success); }
        .tag-warning { background: rgba(232, 152, 94, 0.1); color: var(--color-warning); }
        
        </style>
    """, unsafe_allow_html=True)

def card_metric(label, value, delta=None, color="white", icon=None):
    """
    Custom Metric Card
    color options: white, highlight
    """
    card_class = "card"
    if color == "highlight":
        card_class += " highlight-card"
        
    delta_html = ""
    if delta:
        delta_val = float(str(delta).replace('%','')) if '%' in str(delta) else float(delta)
        delta_color = "#4A9B7F" if delta_val > 0 else "#E8985E"
        if color == "highlight": delta_color = "#E8D5A8"
        
        arrow = "↑" if delta_val > 0 else "↓"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.9rem; font-weight: 600; margin-top: 4px; display: flex; align-items: center; gap: 4px; background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 12px; width: fit-content;">{arrow} {abs(delta_val)}% <span style="font-weight:400; font-size: 0.8rem; opacity: 0.8;">vs 지난주</span></div>'

    icon_html = f'<span style="font-size: 1.2rem;">{icon}</span>' if icon else ""

    html = f"""
    <div class="{card_class}">
        <div class="card-header">{icon_html} {label}</div>
        <div class="stat-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
