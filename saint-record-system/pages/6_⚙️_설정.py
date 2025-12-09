import streamlit as st
from utils.ui import load_custom_css

st.set_page_config(page_title="설정", page_icon="⚙️", layout="wide")
load_custom_css()

st.title("⚙️ 설정")
st.info("준비 중입니다.")
