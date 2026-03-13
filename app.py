import streamlit as st
import streamlit_mermaid as st_mermaid

st.title("Knowledge Base Centrale Termica")
st.sidebar.header("Componenti Installati")

# Qui puoi aggiungere/togliere componenti in futuro
componenti = ["Herz Firestar 35", "Puffer 2000L", "Solare ESR 31", "Tado Zone"]
st.sidebar.write(componenti)

code = """
graph TD
    ... (Incolla qui il codice Mermaid che ti ho scritto sopra) ...
"""
st_mermaid.st_mermaid(code)
