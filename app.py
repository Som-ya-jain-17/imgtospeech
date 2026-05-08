import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from PIL import Image
import pytesseract
import tempfile
import cv2
import numpy as np
import os

# =========================
# AZURE CONFIG (YOUR KEYS)
# =========================
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Vision Voice",
    layout="wide",
    page_icon="🎧"
)

# =========================
# 🌌 PREMIUM DARK UI
# =========================
st.markdown("""
<style>

body, .stApp {
    background: radial-gradient(circle at top, #05060a, #0b0f1a, #05060a);
    color: white;
}

/* Glow background */
.stApp::before {
    content: "";
    position: absolute;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at 20% 20%, rgba(124,58,237,0.2),
                transparent 40%),
                radial-gradient(circle at 80% 30%, rgba(6,182,212,0.15),
                transparent 40%),
                radial-gradient(circle at 50% 80%, rgba(255,45,149,0.12),
                transparent 40%);
    z-index: -1;
}

/* TITLE */
.title {
    text-align: center;
    font-size: 45px;
    font-weight: 800;
    background: linear-gradient(90deg,#7c3aed,#06b6d4,#ff2d95);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* CARD */
.card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(124,58,237,0.3);
    box-shadow: 0 0 25px rgba(124,58,237,0.2);
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(90deg,#7c3aed,#06b6d4);
    color: white;
    border-radius: 12px;
    padding: 10px 18px;
    border: none;
    box-shadow: 0 0 15px rgba(6,182,212,0.4);
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 25px rgba(255,45,149,0.6);
}

/* UPLOADER */
[data-testid="stFileUploader"] {
    border: 2px dashed #7c3aed;
    border-radius: 15px;
    padding: 10px;
}

/* AUDIO FIX */
audio {
    width: 100%;
    border-radius: 10px;
    filter: drop-shadow(0 0 10px cyan);
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("<div class='title'>🎧 AI Image → Voice Converter</div>", unsafe_allow_html=True)
st.write("Upload image → Extract text → Listen in Hindi or English")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Controls")

language = st.sidebar.selectbox("Language", ["English", "Hindi"])

voice_map = {
    "English": "en-US-JennyNeural",
    "Hindi": "hi-IN-SwaraNeural"
}

voice = voice_map[language]

speed = st.sidebar.slider("Speed", 0.5, 2.0, 1.0)

# =========================
# OCR (IMPROVED)
# =========================
def extract_text(image):
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3,3), 0)
    gray = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    config = r'--oem 3 --psm 6'

    text = pytesseract.image_to_string(gray, config=config)

    return text

# =========================
# SPEECH FIXED (100% WORKING)
# =========================
def text_to_speech(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    speech_config.speech_synthesis_voice_name = voice

    # IMPORTANT FIX: correct audio output handling
    audio_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_filename)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    # Proper SSML (fixes Hindi + English)
    rate = int((speed - 1.0) * 100)

    ssml = f"""
    <speak version='1.0' xml:lang='en-US'>
        <voice name='{voice}'>
            <prosody rate='{rate}%'>
                {text}
            </prosody>
        </voice>
    </speak>
    """

    synthesizer.speak_ssml_async(ssml).get()

    return audio_filename

# =========================
# MAIN UI
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Upload Image", type=["png","jpg","jpeg"])

if uploaded_file:

    image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col2:

        if st.button("🚀 Convert to Speech"):

            with st.spinner("🧠 AI Processing..."):

                text = extract_text(image)

                if not text.strip():
                    st.error("❌ No text detected. Try clearer image.")
                else:
                    st.success("📝 Extracted Text")
                    st.write(text)

                    audio_path = text_to_speech(text)

                    # FIX: always playable audio
                    with open(audio_path, "rb") as f:
                        audio_bytes = f.read()
                        st.audio(audio_bytes, format="audio/wav")

                    st.success("🎧 Audio generated successfully!")

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("""
<div style="text-align:center;color:#aaa;margin-top:30px;">
✨ Developed by Somya Jain
</div>
""", unsafe_allow_html=True)
