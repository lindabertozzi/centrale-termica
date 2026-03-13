import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Digital Twin Centrale Termica", layout="wide")

# Funzione migliorata con 'key' per evitare errori Node/removeChild
def st_mermaid(code: str, key=None):
    html = f"""
    <div id="mermaid-container-{key}" class="mermaid">
        {code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ 
            startOnLoad: true, 
            theme: 'neutral',
            securityLevel: 'loose'
        }});
        // Forza il re-rendering se necessario
        mermaid.contentLoaded();
    </script>
    """
    # Aggiungiamo una key al componente Streamlit
    components.html(html, height=600, scrolling=True, key=f"md_{key}")

st.title("🛡️ Sistema Ibrido Herz & Solare")

# --- SIDEBAR ---
# Usiamo elementi semplici per evitare conflitti di rendering
st.sidebar.title("📖 Scheda Tecnica")
st.sidebar.markdown(f"""
**Generatore:** Herz Firestar 35kW  
**Accumulo:** 2000L (2x1000L)  
**Solare:** ESR 31 (TA)  
---
**Parametri Solare:** - Δ ON: 8.0 K  
- Δ OFF: 4.0 K  
- Max Puffer: 90°C
""")

# --- LAYOUT PRINCIPALE ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔄 Schema Idraulico")
    
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
    """
    # Passiamo una key univoca
    st_mermaid(mermaid_graph, key="main_diag")

with col2:
    st.subheader("📝 Stato Logico")
    st.success("K1: Attivo (T > 50°C)")
    
    with st.expander("Dettagli Integrazione Gas"):
        st.write("La caldaia a gas interviene solo se l'accumulo solare/biomassa è insufficiente per il setpoint ACS.")
