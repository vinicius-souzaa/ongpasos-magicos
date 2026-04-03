import streamlit as st

def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1rem 0 0.5rem;">
            <div style="font-size:1.1rem;font-weight:700;color:#6EE7B7;letter-spacing:-0.01em;">
                ✨ Passos Mágicos
            </div>
            <div style="font-size:0.7rem;color:#475569;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px;">
                Data Analytics · PEDE 2020–2022
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        st.caption("Vinicius A. E. Souza")
