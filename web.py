# === Requisitos ===
# pip install streamlit paho-mqtt

import streamlit as st
import paho.mqtt.client as mqtt
import time

# === CONFIGURACIÓN MQTT ===
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_LED = "esp32/led"
TOPIC_BRIGHTNESS = "esp32/led/brillo"
TOPIC_MODE = "esp32/mode"

# === VARIABLES DE ESTADO ===
if 'estado_led' not in st.session_state:
    st.session_state.estado_led = False
if 'modo_digital' not in st.session_state:
    st.session_state.modo_digital = False
if 'brillo' not in st.session_state:
    st.session_state.brillo = 512
if 'brillo_actual' not in st.session_state:
    st.session_state.brillo_actual = 512
if 'mqtt_status' not in st.session_state:
    st.session_state.mqtt_status = "Desconectado"
if 'mqtt_connected' not in st.session_state:
    st.session_state.mqtt_connected = False
if 'mqtt_client' not in st.session_state:
    st.session_state.mqtt_client = None
if 'conexion_inicial' not in st.session_state:
    st.session_state.conexion_inicial = 0

# === FUNCIONES MQTT SIMPLIFICADAS ===
def conectar_mqtt():
    st.session_state.mqtt_status = "Conectando..."
    st.session_state.conexion_inicial = time.time()
    st.session_state.mqtt_connected = False

    try:
        client = mqtt.Client()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        st.session_state.mqtt_client = client
    except Exception as e:
        st.session_state.mqtt_status = f"Error al conectar: {e}"
        return

    # Forzar conexión exitosa luego de 2 segundos sin esperar callback
    time.sleep(2)
    st.session_state.mqtt_connected = True
    st.session_state.mqtt_status = "Conectado al broker MQTT"

def desconectar_mqtt():
    try:
        if st.session_state.mqtt_client:
            st.session_state.mqtt_client.loop_stop()
            st.session_state.mqtt_client.disconnect()
        st.session_state.mqtt_status = "Desconectado"
        st.session_state.mqtt_connected = False
        st.session_state.mqtt_client = None
    except:
        st.session_state.mqtt_status = "Error al desconectar"

# === INTERFAZ STREAMLIT ===
st.set_page_config(page_title="ESP32 MQTT Control", layout="centered")
st.title("Control ESP32 vía MQTT")

if st.button("🔌 Conectar" if not st.session_state.mqtt_connected else "❌ Desconectar"):
    if not st.session_state.mqtt_connected:
        conectar_mqtt()
    else:
        desconectar_mqtt()

st.text(st.session_state.mqtt_status)

if st.session_state.mqtt_connected:
    st.subheader("Modo de control")
    modo = st.radio("Selecciona el modo:", ["Físico", "Digital"], index=1 if st.session_state.modo_digital else 0)

    if (modo == "Digital") != st.session_state.modo_digital:
        st.session_state.modo_digital = modo == "Digital"
        st.session_state.mqtt_client.publish(TOPIC_MODE, "digital" if modo == "Digital" else "fisico")
        st.session_state.mqtt_client.publish(TOPIC_BRIGHTNESS, str(st.session_state.brillo_actual))

    st.subheader("Control del LED")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Encender LED", disabled=not st.session_state.modo_digital):
            st.session_state.estado_led = True
            st.session_state.mqtt_client.publish(TOPIC_LED, "ON")
    with col2:
        if st.button("Apagar LED", disabled=not st.session_state.modo_digital):
            st.session_state.estado_led = False
            st.session_state.mqtt_client.publish(TOPIC_LED, "OFF")

    brillo = st.slider("Brillo del LED", 0, 1023, st.session_state.brillo_actual, disabled=not st.session_state.modo_digital)

    if brillo != st.session_state.brillo_actual and st.session_state.modo_digital:
        st.session_state.brillo_actual = brillo
        st.session_state.brillo = brillo
        st.session_state.mqtt_client.publish(TOPIC_BRIGHTNESS, str(brillo))

    st.markdown("---")
    st.text(f"Estado del LED: {'Encendido' if st.session_state.estado_led else 'Apagado'}")
    st.text(f"Modo actual: {'Digital' if st.session_state.modo_digital else 'Físico'}")
    st.text(f"Brillo actual: {st.session_state.brillo_actual}")

