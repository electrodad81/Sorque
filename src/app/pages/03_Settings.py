
import streamlit as st

st.set_page_config(page_title="Settings — Sorque", page_icon="⚙️", layout="centered")
st.title("Settings")
typewriter = st.toggle("Typewriter effect (placeholder)", value=False)
content_filter = st.toggle("PG-13 content filter (always on in MVP)", value=True, disabled=True)
st.caption("More settings coming soon.")
