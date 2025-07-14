import streamlit as st

st.set_page_config(page_title="Binji", page_icon=":material/recycling:")

page_home = st.Page("./pages/page_home.py", title="Home", icon=":material/recycling:")

pg = st.navigation([page_home])

pg.run()
