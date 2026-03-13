import streamlit as st
import streamlit.components.v1 as components
from groq import Groq  # <-- Assicurati che ci sia questo import

st.set_page_config(page_title="Digital Twin Centrale Termica", layout="wide")

# 1. --- GESTIONE SICURA DELLA CHIAVE API (Subito dopo i set_page_config) ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.sidebar.error("⚠️ API Key mancante nei Secrets!")
    client = None # Impostiamo a None per evitare crash successivi

# 2. --- FUNZIONE RENDERING MERMAID ---
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

# 3. --- SIDEBAR E LAYOUT (Il codice che avevi già) ---
st.title("🛡️ Sistema Ibrido Herz & Solare")

st.sidebar.title("📖 Scheda Tecnica")
st.sidebar.markdown("""
**Generatore:** Herz Firestar 35kW  
**Accumulo:** 2000L (2x1000L)  
**Solare:** ESR 31 (TA)  
---
**Parametri Solare:** - Δ ON: 8.0 K  
- Δ OFF: 4.0 K  
""")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔄 Schema Idraulico")
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

# 4. --- LOGICA DELLA CHIAVE AI (In fondo al file) ---
st.divider()
st.header("🤖 Assistente Tecnico")

if client is None:
    st.info("Configura la chiave GROQ_API_KEY nei Secrets di Streamlit per parlare con l'assistente.")
else:
    # Qui inserisci il codice della chat (messaggi, input, ecc.) che abbiamo visto prima
    system_prompt = "Sei un esperto della centrale termica Herz Firestar dell'utente..."
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Chiedimi qualcosa sulla centrale..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages
            )
            full_response = response.choices[0].message.content
            st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
