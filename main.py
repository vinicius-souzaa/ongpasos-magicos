import streamlit as st

st.set_page_config(
    page_title="Passos Mágicos · Data Analytics",
    layout="wide",
    page_icon="✨",
    initial_sidebar_state="expanded"
)

pages = st.navigation([
    st.Page("pages/1_Analise_Exploratoria.py",  title="📊 Análise Exploratória"),
    st.Page("pages/2_Modelos_Preditivos.py",    title="🤖 Modelos Preditivos"),
    st.Page("pages/3_Conclusoes.py",            title="💡 Conclusões"),
    st.Page("pages/4_Simulador.py",             title="🎯 Simulador"),
], position="sidebar")
pages.run()
