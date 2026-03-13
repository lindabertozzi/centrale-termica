import streamlit as st
from streamlit_mermaid import st_mermaid

st.set_page_config(page_title="Digital Twin Centrale Termica", layout="wide")

st.title("🛡️ Sistema Ibrido Herz & Solare")

# Sidebar con Dati Tecnici per "Knowledge Base" rapida
with st.sidebar:
    st.header("📖 Scheda Tecnica")
    st.info("""
    **Generatore:** Herz Firestar 35kW
    **Accumulo:** 2000L (2x1000L)
    **Solare:** ESR 31 (TA)
    **Integrazione:** Caldaia Gas (Solo ACS)
    **Logica:** Herz 533 (Climatica)
    """)
    
    st.divider()
    st.subheader("Parametri Solare")
    st.write("- Δ ON: 8.0 K")
    st.write("- Δ OFF: 4.0 K")
    st.write("- Max Puffer: 90°C")

# Layout a due colonne
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔄 Schema Idraulico Dinamico")
    
    # Codice Mermaid basato sulla tua relazione
    mermaid_code = """
    graph TD
        subgraph Calore [Generazione]
            Herz[🔥 Herz Firestar 35kW]
            Solare[☀️ Pannelli Solari]
            Gas[🔥 Caldaia Gas Backup]
        end

        subgraph Accumulo [Sistema Puffer 2000L]
            P1[Puffer 1 - Master / ACS]
            P2[Puffer 2 - Slave]
            P1 --- P2
        end

        %% Logica Solare
        Solare --> ESR31{ESR 31}
        ESR31 -- "dT > 8K" --> P1

        %% Logica ACS
        P1 -- "Pre-riscaldo" --> Scambiatore[Scambiatore Gas]
        Gas --> Scambiatore
        Scambiatore --> ACS[Utenze Sanitarie]

        %% Logica Riscaldamento
        P1 -- "T > 50°C" --> K1{Relè Master K1}
        K1 -- "Consenso" --> Herz533[Modulo Herz 533]
        Herz533 -- "Miscelata" --> Zone[Appartamenti Tado]

        style Herz fill:#f96,stroke:#333
        style P1 fill:#3498db,color:#fff
        style P2 fill:#3498db,color:#fff
    """
    st_mermaid(mermaid_code, height=500)

with col2:
    st.subheader("📝 Note di Funzionamento")
    with st.expander("Logica ACS"):
        st.write("La caldaia a gas non scalda i termosifoni. Interviene solo se il Puffer è sotto il setpoint sanitario.")
    
    with st.expander("Logica K1"):
        st.write("Se il Puffer scende sotto i 50°C, il relè K1 stacca le pompe di zona per evitare di far girare acqua fredda.")

st.divider()
st.caption("Interfaccia basata su Relazione Tecnica - Herz Firestar / ESR 31")
