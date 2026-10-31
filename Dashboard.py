import time
import requests
import streamlit as st

st.title("💧 IoT Tank Monitoring Dashboard")

CUS_STATUS_URL = "http://localhost:8080/api/status"
CUS_COMMAND_URL = "http://localhost:8080/api/command"

def get_status_from_java():
    try:
        response = requests.get(CUS_STATUS_URL, timeout=1)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass

    return None


def send_command(command):
    try:
        response = requests.post(
            CUS_COMMAND_URL,
            data=command,
            timeout=2
        )
        if response.ok:
            st.success("Comando inviato al CUS.")
        else:
            st.error(f"Errore nell'invio del comando: HTTP {response.status_code}")
    except requests.RequestException:
        st.error("NOT AVAILABLE: impossibile comunicare con il CUS.")


st.subheader("Pannello di Controllo")

# Recupera lo stato corrente del CUS
current_data = get_status_from_java()
cus_available = current_data is not None

# Se il CUS non risponde, mostra uno stato predefinito
if cus_available:
    current_mode = current_data.get("workMode", "AUTOMATIC")
    current_valve = int(current_data.get("valveOpenPercentage", 0))
    current_level = current_data.get("waterLevel", 0)
    problem_state = current_data.get("problemsState", "NOT AVAILABLE")
else:
    current_mode = "AUTOMATIC"
    current_valve = 0
    current_level = 0
    problem_state = "NOT AVAILABLE"

# Stato della connessione
if cus_available:
    st.success("CUS connesso.")
else:
    st.error(
        "⚠️ NOT AVAILABLE — Impossibile comunicare con il CUS. "
        "I dati visualizzati non sono aggiornati."
    )

# Controlli sempre visibili
col1, col2 = st.columns(2)

with col1:
    if st.button("Passa a Manuale", use_container_width=True):
        if cus_available:
            send_command("workMode=MANUAL")
        else:
            st.error("Comando non inviato: CUS NOT AVAILABLE.")

with col2:
    if st.button("Passa ad Automatico", use_container_width=True):
        if cus_available:
            send_command("workMode=AUTOMATIC")
        else:
            st.error("Comando non inviato: CUS NOT AVAILABLE.")

# Slider sempre visibile, anche se il CUS non risponde
valve_val = st.slider(
    "Apertura Valvola (%)",
    min_value=0,
    max_value=100,
    value=max(0, min(100, current_valve)),
    disabled=(current_mode != "MANUAL" or not cus_available)
)

if st.button(
    "Invia Apertura Valvola",
    disabled=(current_mode != "MANUAL" or not cus_available),
    use_container_width=True
):
    send_command(f"valve={valve_val}")

st.divider()
st.subheader("Stato del Sistema")

# Dati sempre visibili
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Livello Acqua",
        f"{current_level} L" if cus_available else "NOT AVAILABLE"
    )

with col2:
    st.metric(
        "Apertura Valvola",
        f"{current_valve} %" if cus_available else "NOT AVAILABLE"
    )

st.info(f"Modalità Attuale: {current_mode}")
if not cus_available:
    st.warning("La modalità mostrata è un valore predefinito, non lo stato reale del CUS.")

if problem_state == "Ok":
    st.success(f"Stato Sistema: {problem_state}")
else:
    st.error(f"Stato Sistema: {problem_state}")

# Aggiorna periodicamente la dashboard
time.sleep(1)
st.rerun()