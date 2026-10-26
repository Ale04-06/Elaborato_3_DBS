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
    except:
        return None
    return None

status_container = st.empty()

st.subheader("Pannello di Controllo")

current_data = get_status_from_java()

if current_data:
    current_mode = current_data.get("workMode", "AUTOMATIC")
    is_manual = (current_mode == "MANUAL")
    
    # buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Passa a Manuale"):
            requests.post(CUS_COMMAND_URL, data="workMode=MANUAL")
            st.rerun()
            
    with col2:
        if st.button("Passa ad Automatico"):
            requests.post(CUS_COMMAND_URL, data="workMode=AUTOMATIC")
            st.rerun()

    if is_manual:
        valve_val = st.slider("Apertura Valvola (%)", 0, 100, current_data.get("valveOpenPercentage", 0))
        if st.button("Invia Apertura Valvola"):
            requests.post(CUS_COMMAND_URL, data=f"valve={valve_val}")
            st.success(f"Valvola impostata al {valve_val}%")

while True:
    data = get_status_from_java()
    
    with status_container.container():
        if data:
            st.metric("Livello Acqua", f"{data.get('waterLevel', 0)} L")
            st.metric("Apertura Valvola", f"{data.get('valveOpenPercentage', 0)} %")
            st.info(f"Modalità Attuale: **{data.get('workMode')}**")
            
            problem_state = data.get('problemsState')
            if problem_state == "Ok":
                st.success(f"Stato Sistema: {problem_state}")
            else:
                st.error(f"Stato Sistema: {problem_state}")
        else:
            st.error("⚠️ Impossibile connettersi al CUS! Assicurati che il programma Java sia acceso.")
    
    time.sleep(1)