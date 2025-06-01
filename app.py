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
    st.session_state.mqtt_status = "No conectado"
if 'conexion_inicial' not in st.session_state:
    st.session_state.conexion_inicial = time.time()

# === FUNCIONES MQTT ===
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        time.sleep(3)  # Esperar 3 segundos antes de confirmar conexión
        st.session_state.mqtt_status = "Conectado al broker MQTT"
        client.subscribe(TOPIC_MODE)
        client.subscribe(TOPIC_BRIGHTNESS)
        client.subscribe(TOPIC_LED)
    else:
        st.session_state.mqtt_status = f"Fallo en la conexión. Código: {rc}"

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        if msg.topic == TOPIC_MODE:
            st.session_state.modo_digital = True if payload.lower() == "digital" else False
        elif msg.topic == TOPIC_BRIGHTNESS:
            brillo = int(payload)
            st.session_state.brillo_actual = brillo
            if st.session_state.modo_digital:
                st.session_state.brillo = brillo
        elif msg.topic == TOPIC_LED:
            st.session_state.estado_led = payload.upper() == "ON"
    except:
        pass

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    st.session_state.mqtt_status = "Conectando..."
except Exception as e:
    st.session_state.mqtt_status = f"Error al conectar: {e}"

# === INTERFAZ STREAMLIT ===
st.set_page_config(page_title="ESP32 MQTT Control", layout="centered")
st.title("Control ESP32 vía MQTT")
st.text(st.session_state.mqtt_status)

st.subheader("Modo de control")
modo = st.radio("Selecciona el modo:", ["Físico", "Digital"], index=1 if st.session_state.modo_digital else 0)

if (modo == "Digital") != st.session_state.modo_digital:
    st.session_state.modo_digital = modo == "Digital"
    mqtt_client.publish(TOPIC_MODE, "digital" if modo == "Digital" else "fisico")
    mqtt_client.publish(TOPIC_BRIGHTNESS, str(st.session_state.brillo_actual))

st.subheader("Control del LED")

col1, col2 = st.columns(2)
with col1:
    if st.button("Encender LED", disabled=not st.session_state.modo_digital):
        st.session_state.estado_led = True
        mqtt_client.publish(TOPIC_LED, "ON")
with col2:
    if st.button("Apagar LED", disabled=not st.session_state.modo_digital):
        st.session_state.estado_led = False
        mqtt_client.publish(TOPIC_LED, "OFF")

brillo = st.slider("Brillo del LED", 0, 1023, st.session_state.brillo_actual, disabled=not st.session_state.modo_digital)

if brillo != st.session_state.brillo_actual and st.session_state.modo_digital:
    st.session_state.brillo_actual = brillo
    st.session_state.brillo = brillo
    mqtt_client.publish(TOPIC_BRIGHTNESS, str(brillo))

st.markdown("---")
st.text(f"Estado del LED: {'Encendido' if st.session_state.estado_led else 'Apagado'}")
st.text(f"Modo actual: {'Digital' if st.session_state.modo_digital else 'Físico'}")
st.text(f"Brillo actual: {st.session_state.brillo_actual}")

# Actualización rápida
time.sleep(0.1)
