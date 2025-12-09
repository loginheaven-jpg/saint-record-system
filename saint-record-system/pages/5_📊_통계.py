import streamlit as st
from utils.ui import load_custom_css

st.set_page_config(page_title="통계", page_icon="📊", layout="wide")
load_custom_css()

st.title("📊 통계")
st.info("준비 중입니다.")
