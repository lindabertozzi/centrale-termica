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
        Herz --> P1
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
    system_prompt = """
Sei l'Assistente Tecnico Virtuale della centrale termica dell'utente. 
Devi rispondere basandoti RIGOROSAMENTE sulla Relazione Tecnica fornita. 
Non inventare componenti. Se non sai una cosa, chiedi i dati dei sensori.

STRUTTURA IMPIANTO:
1. GENERAZIONE: 
   - Primaria: Herz Firestar 35kW (Legna).
   - Solare: Centralina ESR 31. Parametri fissi: ON +8K, OFF +4K, Max Puffer 90°C.
   - Backup: Caldaia a Gas SOLO per ACS (Integrazione/Backup). NON collegata al riscaldamento.

2. ACCUMULO: 
   - 2 Puffer da 1000L in serie (2000L totali).
   - ACS prodotta con sistema Tank-in-Tank nel Puffer primario.
   - Monitoraggio ACS: Modulo Herz 534 con sonda PT1000 nel pozzetto boiler.

3. DISTRIBUZIONE RISCALDAMENTO:
   - 2 Zone indipendenti gestite da Tado (contatti puliti) -> Relè ABB EN20 -> Pompe di zona.
   - Regolazione Mandata: Modulo Herz 533 (Miscelatrice motorizzata + Curva Climatica + Sonda Esterna).
   - SICUREZZA (Relè K1): Termostato a bracciale sul Puffer impostato a 50°C. Se T < 50°C, le pompe di zona sono disattivate elettricamente.

4. GESTIONE ACS:
   - Valvola miscelatrice meccanica in uscita Puffer per protezione scottature.
   - Anello di ricircolo verso caldaia a gas: si attiva solo se il Puffer non garantisce il setpoint sanitario.

REGOLE DI RAGIONAMENTO:
- Se l'utente chiede perché la casa è fredda: Verifica se il Puffer è > 50°C (Stato Relè K1).
- Se l'utente chiede del solare: Applica Delta ON 8K/OFF 4K tra S1 (Pannelli) e S2 (Puffer).
- Se l'utente chiede della caldaia a gas: Ricorda che NON influisce sul riscaldamento stanze.
- Se mancano dati, chiedi: "Qual è la temperatura letta dal modulo Herz 534 o 533?"
"""
    
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
