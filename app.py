import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Digital Twin Centrale Termica", layout="wide")

# Funzione per renderizzare Mermaid in modo affidabile
def st_mermaid(code: str):
    html = f"""
    <div class="mermaid">
        {code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
    </script>
    """
    components.html(html, height=600, scrolling=True)

st.title("🛡️ Sistema Ibrido Herz & Solare")

with st.sidebar:
    st.header("📖 Scheda Tecnica")
    st.info("Herz Firestar 35kW | 2000L Accumulo")
    st.subheader("Parametri Solare")
    st.write("Δ ON: 8.0 K / Δ OFF: 4.0 K")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔄 Schema Idraulico")
    
    # Il tuo schema aggiornato e corretto
    mermaid_graph = """
    graph TD
        subgraph Fonti [Generazione]
            Herz[🔥 Herz Firestar 35kW]
            Solare[☀️ Solare Termico]
            Gas[🔥 Caldaia Gas Backup]
        end

        subgraph Accumulo [Sistema Puffer 2000L]
            P1[Puffer 1 - Master / ACS]
            P2[Puffer 2 - Slave]
            P1 --- P2
        end

        Solare --> ESR31{{Centralina ESR 31}}
        ESR31 -- "dT > 8K" --> P1

        P1 -- "Mandata ACS" --> Scambiatore[Scambiatore Gas]
        Gas --> Scambiatore
        Scambiatore --> ACS[Utenze Sanitarie]

        P1 -- "T > 50°C" --> K1{{Relè Master K1}}
        K1 -- "Consenso" --> Herz533[Modulo Herz 533]
        Herz533 --> Zone[Appartamenti Tado]

        style Herz fill:#f96,stroke:#333
        style P1 fill:#3498db,color:#fff
        style P2 fill:#3498db,color:#fff
        style ESR31 fill:#fff9c4
        style K1 fill:#fff9c4
    """
    st_mermaid(mermaid_graph)

with col2:
    st.subheader("📝 Stato Logico")
    st.success("K1: Attivo (T > 50°C)")
    st.warning("Solare: Standby")
