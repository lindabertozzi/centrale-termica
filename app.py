import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Digital Twin Centrale Termica", layout="wide")

# Funzione semplificata al massimo per evitare il TypeError
def render_mermaid(code):
    html_code = f"""
    <div class="mermaid">
        {code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
    </script>
    """
    return components.html(html_code, height=500)

st.title("🛡️ Sistema Ibrido Herz & Solare")

# Sidebar - Markdown semplice
st.sidebar.title("📖 Scheda Tecnica")
st.sidebar.markdown("""
**Generatore:** Herz Firestar 35kW  
**Accumulo:** 2000L (2x1000L)  
**Solare:** ESR 31 (TA)  
---
**Parametri Solare:** - Δ ON: 8.0 K  
- Δ OFF: 4.0 K  
""")

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔄 Schema Idraulico")
    
    # Stringa Mermaid pulita (senza doppie graffe per evitare conflitti Python)
    mermaid_graph = """
    graph TD
        subgraph Generazione
            Herz[Caldaia Herz 35kW]
            Solare[Pannelli Solari]
            Gas[Caldaia Gas Backup]
        end

        subgraph Accumulo
            P1[Puffer 1 - Master]
            P2[Puffer 2 - Slave]
            P1 --- P2
        end

        Solare --> ESR31[Centralina ESR 31]
        ESR31 -- "dT > 8K" --> P1

        P1 -- "ACS" --> Scambiatore[Scambiatore Gas]
        Gas --> Scambiatore
        Scambiatore --> Utenze[Sanitari]

        P1 -- "T > 50C" --> K1[Rele Master K1]
        K1 -- "Consenso" --> Herz533[Modulo Herz 533]
        Herz533 --> Zone[Appartamenti Tado]

        style Herz fill:#f96
        style P1 fill:#3498db,color:#fff
        style P2 fill:#3498db,color:#fff
    """
    render_mermaid(mermaid_graph)

with col2:
    st.subheader("📝 Stato Logico")
    st.success("K1: Attivo (T > 50°C)")
    st.info("Integrazione Gas: Automatica")
