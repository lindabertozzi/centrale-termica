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
# Funzione aggiornata con scrolling forzato e contenitore flessibile
def render_mermaid(code):
    html_code = f"""
    <div id="graph-container" style="height: 100vh; width: 100%; overflow: auto;">
        <div class="mermaid" style="display: flex; justify-content: center;">
            {code}
        </div>
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ 
            startOnLoad: true, 
            theme: 'neutral',
            securityLevel: 'loose',
            flowchart: {{ useMaxWidth: false, htmlLabels: true }} 
        }});
    </script>
    """
    # Aumentiamo l'altezza a 800 per dare respiro, abilitando lo scrolling di Streamlit
    return components.html(html_code, height=800, scrolling=True)

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
            Herz[🔥 Herz Firestar 35kW]
            Solare[☀️ Solare Termico]
            
            subgraph Caldaia_Gas_Insieme [Caldaia a Gas]
                Gas_ACS[Scambiatore ACS Gas]
                Gas_Risc[Circuito Risc. Gas - NON USATO]
            end
        end

        subgraph Accumulo
            P1[Puffer 1 - Master / ACS]
            P2[Puffer 2 - Slave]
            P1 --- P2
        end

        %% Percorso Solare
        Solare --> ESR31[Centralina ESR 31]
        ESR31 -- "dT > 8K" --> P1

        %% Percorso ACS (Passaggio nel modulo Gas)
        P1 -- "Acqua da Puffer (ACS)" --> Gas_ACS
        Gas_ACS -- "Se T < 55°C: INTEGRA" --> Utenze[Sanitari]
        Gas_ACS -- "Se T >= 55°C: PASSANTE" --> Utenze

        %% Percorso Riscaldamento
        P1 -- "T > 50°C" --> K1[Relè Master K1]
        K1 -- "Consenso" --> Herz533[Modulo Herz 533]
        Herz533 --> Zone[Appartamenti Tado]
        
        %% Nota: Gas_Risc rimane scollegato per chiarezza
        
        style Herz fill:#f96,stroke:#333
        style P1 fill:#3498db,color:#fff
        style P2 fill:#3498db,color:#fff
        style Caldaia_Gas_Insieme fill:#f2f2f2,stroke:#333,stroke-dasharray: 5 5
        style Gas_ACS fill:#ff9999
        style Gas_Risc fill:#cccccc,color:#666
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
Sei l'Assistente Tecnico Virtuale esperto della centrale termica specifica dell'utente. 
Rispondi RIGOROSAMENTE basandoti sulla configurazione idraulica ed elettrica descritta. 
NON suggerire componenti non presenti o soluzioni generiche.

--- CONFIGURAZIONE TECNICA ---

1. GENERAZIONE E ACCUMULO:
   - Caldaia Primaria: Herz Firestar 35 kW (Legna) con gestione elettronica.
   - Accumulo: 2 Puffer da 1000L collegati in serie (totale 2000L).
   - Solare Termico: Centralina ESR 31 (Technische Alternative).
     * S1 (Pannelli) / S2 (Puffer).
     * Logica: Delta ON +8.0K, Delta OFF +4.0K. S2 MAX (Limite Puffer): 90°C.

2. LOGICA ACS (Acqua Calda Sanitaria):
   - Produzione: Sistema Tank-in-Tank (boiler immerso nel Puffer 1 Master).
   - Monitoraggio: Modulo Herz 534 con sonda PT1000 nel pozzetto boiler.
   - Integrazione GAS: L'ACS in uscita dal Puffer entra direttamente nella caldaia a Gas.
     * Se T_Puffer >= 55°C: La caldaia a Gas NON si accende. L'acqua passa e va alle utenze.
     * Se T_Puffer < 55°C: La caldaia a Gas si accende per integrare il calore mancante.
   - Sicurezza: Valvola miscelatrice meccanica esterna post-Puffer per controllo scottature.
   - Ricircolo: Gestito indipendentemente via domotica/timer.
   - La Caldaia a Gas è visualizzata come un unico insieme ma divisa logicamente:
     * La parte 'Gas_ACS' è l'unica attiva e funge da post-riscaldatore istantaneo.
     * La parte 'Gas_Risc' è presente fisicamente nella caldaia ma NON è collegata ai collettori di riscaldamento, che sono alimentati esclusivamente dai Puffer.

3. LOGICA RISCALDAMENTO:
   - Configurazione: 2 Zone (appartamenti) gestite da Tado (contatto pulito).
   - Hardware: Tado -> Relè interfaccia CR-M -> Contattori ABB EN20 -> Pompe di zona.
   - Regolazione: Modulo Herz 533 con valvola miscelatrice motorizzata, sonda esterna e sonda mandata PT1000 (Curva Climatica).
   - INTERBLOCCO ELETTRICO (Relè K1): Termostato a bracciale sul Puffer impostato a 50°C. 
     * Se T_Puffer < 50°C: Il relè K1 toglie fisicamente alimentazione alle pompe di zona (anche se Tado chiede calore).

--- REGOLE DI RAGIONAMENTO ---

- PROBLEMI RISCALDAMENTO: Se le zone sono fredde, chiedi subito la temperatura del Puffer. Se è < 50°C, spiega che il Relè K1 blocca la circolazione per sicurezza.
- PROBLEMI ACS: Se la caldaia a gas si accende, verifica la temperatura del modulo Herz 534. Se è < 55°C, l'accensione è normale integrazione.
- PROBLEMI SOLARE: Calcola sempre Delta ON (8K) tra pannelli e puffer prima di confermare se la pompa dovrebbe girare.
- COMPONENTISTICA: Se l'utente chiede di guasti elettrici, cita i magnetotermici ABB S201L e i relè CR-M.
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
