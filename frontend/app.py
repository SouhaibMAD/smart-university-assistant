"""Page d'accueil / connexion. Périmètre : Hafsa (feature/streamlit-ui)."""
import streamlit as st

import api_client

st.set_page_config(page_title="Smart University Assistant", page_icon="🎓", layout="wide")

st.title("🎓 Smart University Assistant")

if api_client.health():
    st.success("Backend joignable.")
else:
    st.error("Backend injoignable.")

st.info("Connexion / inscription : à implémenter.")
