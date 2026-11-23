import streamlit as st

st.set_page_config(
    page_title="Solo Tracker",
    page_icon="🎲",
    layout="wide"
)

# Games is the default page so ?record_play=<id> links keep working
pages = [
    st.Page("games_page.py", title="Games", icon="🎲", default=True),
    st.Page("dashboard_page.py", title="Dashboard", icon="📊", url_path="dashboard"),
]

st.navigation(pages).run()
