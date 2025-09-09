import streamlit as st
from auth_module import auth_ui

auth_ui()

if st.session_state.get("logged_in", False):
    st.write("Welcome to the main app!")
