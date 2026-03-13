from groq import Groq

# Inizializza il client Groq usando i Secrets di Streamlit
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.divider()
st.header("🤖 Assistente Tecnico Centrale")

# Messaggio di sistema per "istruire" l'IA sulla tua configurazione
system_prompt = f"""
Sei un esperto termotecnico specializzato nella centrale termica dell'utente.
Configurazione:
- Caldaia Herz Firestar 35kW (legna).
- 2 Puffer da 1000L in serie.
- Solare termico con centralina ESR 31 (Delta ON 8K, Delta OFF 4K).
- Integrazione caldaia a gas solo per ACS tramite scambiatore.
- Relè K1 di blocco pompe se Puffer < 50°C.
Rispondi in modo conciso e tecnico.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Visualizza lo storico dei messaggi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input dell'utente
if prompt := st.chat_input("Chiedimi un consiglio di efficienza o manutenzione..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state.messages
            ]
        )
        full_response = response.choices[0].message.content
        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
