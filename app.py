import streamlit as st
import paho.mqtt.publish as publish
import time

# --- Configuración del Broker MQTT ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_LED = "esp32/led"

# --- Estado del sistema ---
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'led_on' not in st.session_state:
    st.session_state.led_on = False
if 'modo_manual' not in st.session_state:
    st.session_state.modo_manual = True
if 'slider_value' not in st.session_state:
    st.session_state.slider_value = 0

# --- Animación de bienvenida ---
st.markdown("""
    <h1 style='text-align: center; color: green;'>BIENVENIDO</h1>
""", unsafe_allow_html=True)
time.sleep(4)

# --- Título principal ---
st.markdown("""
    <h1 style='text-align: center;'>MOMENTO DE CONTROLAR</h1>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .stButton>button {
        display: block;
        margin: auto;
    }
    .stSlider>div {
        margin: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- LED de estado MQTT ---
def estado_led_html(encendido):
    color = "green" if encendido else "red"
    return f"""
        <div style='text-align: center;'>
            <div style='width: 20px; height: 20px; background-color: {color}; border-radius: 50%; margin: auto;'></div>
        </div>
    """

# --- Botón de conexión MQTT ---
if st.button("Conectar al MQTT"):
    st.session_state.connected = not st.session_state.connected
    mensaje = "CONECTADO EXITOSAMENTE" if st.session_state.connected else "DESCONECTADO EXITOSAMENTE"
    st.success(mensaje)
    st.markdown(estado_led_html(st.session_state.connected), unsafe_allow_html=True)

# --- Botón para controlar el LED ---
if st.session_state.connected:
    if st.button("Encender LED" if not st.session_state.led_on else "Apagar LED"):
        st.session_state.led_on = not st.session_state.led_on
        mensaje = "ON" if st.session_state.led_on else "OFF"
        publish.single(MQTT_TOPIC_LED, mensaje, hostname=MQTT_BROKER, port=MQTT_PORT)

    # --- Control de brillo ---
    st.session_state.slider_value = st.slider("Control de brillo", 0, 100, st.session_state.slider_value)
    brillo_mensaje = f"BRILLO:{st.session_state.slider_value}"
    publish.single(MQTT_TOPIC_LED, brillo_mensaje, hostname=MQTT_BROKER, port=MQTT_PORT)

# --- Botón de modo manual/virtual ---
modo_actual = "MODO MANUAL" if st.session_state.modo_manual else "MODO VIRTUAL"
if st.button(modo_actual):
    st.session_state.modo_manual = not st.session_state.modo_manual
